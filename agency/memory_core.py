import sqlite3
import sqlite_vec
import numpy as np
import google.generativeai as genai
import hashlib
import json
import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MEMORY-CORE] - %(levelname)s - %(message)s')

class MemoryCore:
    """
    MEMORY CORE (v2.3) - HYBRID SEARCH ENGINE
    -----------------------------------------
    - Vector Search: sqlite-vec (Cosine Similarity)
    - Text Search: FTS5 (BM25)
    - Fusion: Reciprocal Rank Fusion (RRF)
    - Embedding: Local Ollama (embeddinggemma) with Gemini Fallback
    - Generation: Google Gemini (3.1 Pro)
    """

    def __init__(self, db_path: str = "E:/0x/agency/memory.db", api_key: str = None):
        self.db_path = db_path
        self._configure_api(api_key)
        
        self.embedding_model = "embeddinggemma" 
        self.generation_model = "models/gemini-3.1-pro-preview" 
        self.dimensions = 768 
        
        self.db = sqlite3.connect(self.db_path)
        self.db.enable_load_extension(True)
        sqlite_vec.load(self.db)
        self.db.enable_load_extension(False)
        
        self._ensure_schema()
        logging.info(f"Memory Core v2.3 (Hybrid Resilience) initialized at {self.db_path}")

    from agency.key_rotator import KeyRotator
    def _configure_api(self, api_key: str):
        self.rotator = KeyRotator("gemini")
        self.api_key = self.rotator.get_key()
        if not self.api_key:
            try:
                with open("E:/0x/.env", "r") as f:
                    for line in f:
                        if line.startswith("GOOGLE_API_KEY="):
                            self.api_key = line.split("=")[1].strip()
                            break
            except:
                pass
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            logging.warning("No Google API Key found. Fallback embeddings and generation will fail.")

    def _ensure_schema(self):
        """Ensures all tables exist and match current schema."""
        # 1. Check for legacy tables and rebuild if necessary
        for table in ['chunks', 'files', 'bicameral_history']:
            res = self.db.execute(f"PRAGMA table_info({table})").fetchall()
            if not res: continue
            
            # Specific column checks
            rebuild = False
            if table == 'chunks' and not any(r[1] == 'content' for r in res): rebuild = True
            if table == 'files' and not any(r[1] == 'last_indexed' for r in res): rebuild = True
            
            if rebuild:
                logging.warning(f"Schema mismatch in '{table}'. Rebuilding.")
                self.db.execute(f"DROP TABLE {table}")
                if table == 'chunks': self.db.execute("DROP TABLE IF EXISTS vec_items")

        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS files (
              path TEXT PRIMARY KEY,
              hash TEXT NOT NULL,
              mtime REAL NOT NULL,
              last_indexed REAL NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS chunks (
              id TEXT PRIMARY KEY,
              path TEXT NOT NULL,
              content TEXT NOT NULL,
              start_line INTEGER,
              end_line INTEGER,
              token_count INTEGER,
              embedding BLOB
            );

            CREATE TABLE IF NOT EXISTS bicameral_history (
              id TEXT PRIMARY KEY,
              timestamp REAL NOT NULL,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              summary TEXT,
              embedding BLOB
            );
        """)
        
        # 2. Vector Tables (sqlite-vec)
        try:
            res = self.db.execute("SELECT sql FROM sqlite_master WHERE name='vec_items'").fetchone()
            if res and f"float[{self.dimensions}]" not in res[0].lower():
                logging.warning(f"Vector dimensions mismatch. Rebuilding vec_items.")
                self.db.execute("DROP TABLE vec_items")

            self.db.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_items USING vec0(
                    id TEXT PRIMARY KEY,
                    embedding float[{self.dimensions}]
                );
            """)

            self.db.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_history USING vec0(
                    id TEXT PRIMARY KEY,
                    embedding float[{self.dimensions}]
                );
            """)
        except Exception as e:
            logging.error(f"Vector table init failed: {e}")

        # 3. FTS5 Table (Text Search)
        try:
            self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_items USING fts5(id UNINDEXED, content);")
            self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_history USING fts5(id UNINDEXED, content);")
        except Exception as e:
            logging.error(f"FTS5 table init failed: {e}")
            
        self.db.commit()

    def get_embedding(self, text: str) -> np.ndarray:
        """Generates embedding using Local Ollama with Gemini Fallback."""
        # 1. Try Local Ollama
        try:
            import ollama
            result = ollama.embed(model=self.embedding_model, input=text)
            emb = result['embeddings'][0]
            return np.array(emb, dtype=np.float32)
        except Exception as e:
            logging.debug(f"Ollama Embedding failed: {e}. Trying Gemini fallback.")
            
        # 2. Try Gemini Fallback
        try:
            # We use the genai.embed_content for the fallback
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return np.array(result['embedding'], dtype=np.float32)
        except Exception as e:
            logging.error(f"Gemini Embedding fallback failed: {e}. Returning zeros.")
            self.rotator.mark_failed(self.api_key, str(e))
            self.api_key = self.rotator.get_key() # Cycle for next time
            genai.configure(api_key=self.api_key)
            return np.zeros(self.dimensions, dtype=np.float32)

    def add_document(self, path: str, content: str):
        """Indexes a document (Chunk -> Embed -> Store)."""
        file_hash = hashlib.sha256(content.encode()).hexdigest()
        cur = self.db.execute("SELECT hash FROM files WHERE path=?", (path,)).fetchone()
        if cur and cur[0] == file_hash: return 

        logging.info(f"Indexing: {path}")
        self.db.execute("DELETE FROM chunks WHERE path=?", (path,))
        chunks = self._chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{hashlib.md5(path.encode()).hexdigest()}_{i}"
            embedding = self.get_embedding(chunk)
            
            self.db.execute(
                "INSERT INTO chunks (id, path, content, embedding) VALUES (?, ?, ?, ?)",
                (chunk_id, path, chunk, embedding.tobytes())
            )
            self.db.execute("INSERT OR REPLACE INTO vec_items (id, embedding) VALUES (?, ?)", (chunk_id, embedding))
            self.db.execute("DELETE FROM fts_items WHERE id=?", (chunk_id,))
            self.db.execute("INSERT INTO fts_items (id, content) VALUES (?, ?)", (chunk_id, chunk))

        self.db.execute(
            "INSERT OR REPLACE INTO files (path, hash, mtime, last_indexed) VALUES (?, ?, ?, ?)",
            (path, file_hash, os.path.getmtime(path) if os.path.exists(path) else 0, datetime.now().timestamp())
        )
        self.db.commit()

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        paragraphs = text.split("\n\n")
        chunks, current = [], ""
        for p in paragraphs:
            if len(current) + len(p) < chunk_size: current += p + "\n\n"
            else:
                chunks.append(current.strip())
                current = p + "\n\n"
        if current: chunks.append(current.strip())
        return chunks

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Hybrid Search using Reciprocal Rank Fusion (RRF)."""
        query_vec = self.get_embedding(query)
        vec_results = self.db.execute("SELECT id, vec_distance_cosine(embedding, ?) as distance FROM vec_items WHERE embedding MATCH ? AND k = ? ORDER BY distance", (query_vec, query_vec, limit * 2)).fetchall()
        clean_query = re.sub(r'[^a-zA-Z0-9 ]', '', query)
        fts_results = self.db.execute("SELECT id, rank FROM fts_items WHERE fts_items MATCH ? ORDER BY rank LIMIT ?", (clean_query, limit * 2)).fetchall()
        
        scores, k = {}, 60
        for rank, (doc_id, _) in enumerate(vec_results):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        for rank, (doc_id, _) in enumerate(fts_results):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
            
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        results = []
        for doc_id, score in sorted_ids:
            row = self.db.execute("SELECT content, path FROM chunks WHERE id=?", (doc_id,)).fetchone()
            if row: results.append({"id": doc_id, "content": row[0], "path": row[1], "score": score})
            
        # --- FALLBACK MECHANISM (Axiom 311.F) ---
        if not results:
            logging.warning("Memory Search returned zero results. Reverting to Monolithic Anchor.")
            anchor_path = "E:/0x/gemini.md"
            if os.path.exists(anchor_path):
                with open(anchor_path, "r") as f:
                    results.append({
                        "id": "monolithic_anchor",
                        "content": f.read(),
                        "path": anchor_path,
                        "score": 1.0
                    })
        return results

    def add_history(self, role: str, content: str):
        h_id = f"hist_{hashlib.md5(f'{role}{content}{datetime.now().timestamp()}'.encode()).hexdigest()}"
        embedding = self.get_embedding(content)
        self.db.execute("INSERT INTO bicameral_history (id, timestamp, role, content, embedding) VALUES (?, ?, ?, ?, ?)", (h_id, datetime.now().timestamp(), role, content, embedding.tobytes()))
        self.db.execute("INSERT INTO vec_history (id, embedding) VALUES (?, ?)", (h_id, embedding))
        self.db.execute("INSERT INTO fts_history (id, content) VALUES (?, ?)", (h_id, content))
        self.db.commit()


    def get_kinetic_context(self, current_prompt: str, limit: int = 50) -> str:
        """
        LAYER 2: THE KINETIC LENS
        Uses a reasoning model to compress raw logs into a heuristic card.
        """
        try:
            from agency.kinetic_lens_blueprint import KineticLens
            from agency.open_web_ui import OpenWebUIClient

            client = OpenWebUIClient()
            lens = KineticLens(self.db_path, client)

            # 1. Pull raw narrative
            narrative = lens.pull_recent_narrative(limit=limit)

            # 2. Generate Heuristic Card via Reasoning Model
            card = lens.generate_heuristic_card(narrative)

            # 3. Inject context
            return lens.inject_context(current_prompt, card)
        except Exception as e:
            logging.error(f"Kinetic Lens Failure: {e}")
            return current_prompt # Fallback to raw prompt
    
if __name__ == "__main__":
    mem = MemoryCore()
    if os.path.exists("E:/0x/README.md"):
        with open("E:/0x/README.md", "r") as f:
            mem.add_document("E:/0x/README.md", f.read())
    print("Self-test complete.")
