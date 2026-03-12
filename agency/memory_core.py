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
    MEMORY CORE (v2.2) - HYBRID SEARCH ENGINE (HYBRID ARCHITECTURE)
    -----------------------------------------
    - Vector Search: sqlite-vec (Cosine Similarity)
    - Text Search: FTS5 (BM25)
    - Fusion: Reciprocal Rank Fusion (RRF)
    - Embedding: Local Ollama (embeddinggemma)
    - Generation: Google Gemini (3.1 Pro)
    """

    def __init__(self, db_path: str = "E:/0x/agency/memory.db", api_key: str = None):
        self.db_path = db_path
        self._configure_api(api_key)
        
        # HYBRID ARCHITECTURE:
        # Embedding: Local Ollama (embeddinggemma) -> Sovereign Memory (Google Ecosystem)
        # Generation: Google Gemini (3.1 Pro) -> High-IQ Processing
        self.embedding_model = "embeddinggemma" 
        self.generation_model = "models/gemini-3.1-pro-preview" 
        self.dimensions = 768 # embeddinggemma is 768 dims
        
        self.db = sqlite3.connect(self.db_path)
        self.db.enable_load_extension(True)
        sqlite_vec.load(self.db)
        self.db.enable_load_extension(False)
        
        self._ensure_schema()
        logging.info(f"Memory Core v2.2 (Hybrid/Gemma) initialized at {self.db_path}")

    def _configure_api(self, api_key: str):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
             # Try to read from .env if not in environment
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
            logging.warning("No Google API Key found. Generation will fail.")

    def _ensure_schema(self):
        """Ensures all tables exist (Standard, Vector, FTS)."""
        # 1. Standard Metadata Tables
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
            # Check if vec table exists and has correct dimensions
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
            self.db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_items USING fts5(
                    id UNINDEXED,
                    content
                );
            """)
            self.db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_history USING fts5(
                    id UNINDEXED,
                    content
                );
            """)
        except Exception as e:
            logging.error(f"FTS5 table init failed: {e}")
            
        self.db.commit()

    def add_history(self, role: str, content: str):
        """Adds an interaction to the Bicameral History (Secondary Chamber)."""
        h_id = f"hist_{hashlib.md5(f'{role}{content}{datetime.now().timestamp()}'.encode()).hexdigest()}"
        embedding = self.get_embedding(content)
        
        self.db.execute(
            "INSERT INTO bicameral_history (id, timestamp, role, content, embedding) VALUES (?, ?, ?, ?, ?)",
            (h_id, datetime.now().timestamp(), role, content, embedding.tobytes())
        )
        self.db.execute("INSERT INTO vec_history (id, embedding) VALUES (?, ?)", (h_id, embedding))
        self.db.execute("INSERT INTO fts_history (id, content) VALUES (?, ?)", (h_id, content))
        self.db.commit()
        logging.info(f"Committed {role} payload to Secondary Chamber.")

    def get_shadow_context(self, query: str, limit: int = 3) -> str:
        """Retrieves relevant history from the Secondary Chamber."""
        query_vec = self.get_embedding(query)
        
        # Search history via vector
        res = self.db.execute("""
            SELECT h.role, h.content, vec_distance_cosine(vh.embedding, ?) as distance
            FROM vec_history vh
            JOIN bicameral_history h ON vh.id = h.id
            WHERE vh.embedding MATCH ? AND k = ?
            ORDER BY distance
            LIMIT ?
        """, (query_vec, query_vec, limit * 2, limit)).fetchall()
        
        if not res: return ""
        
        context_block = "\n<shadow_context>\n"
        for role, content, _ in res:
            context_block += f"[{role.upper()}]: {content[:500]}...\n"
        context_block += "</shadow_context>\n"
        return context_block

    def get_embedding(self, text: str) -> np.ndarray:
        """Generates embedding using Local Ollama."""
        try:
            import ollama
            # Use Ollama for local embedding
            result = ollama.embed(model=self.embedding_model, input=text)
            # Ollama returns 'embeddings' list of lists (for batch) or single list
            # We assume single input, so result['embeddings'][0]
            emb = result['embeddings'][0]
            return np.array(emb, dtype=np.float32)
        except Exception as e:
            logging.error(f"Ollama Embedding failed: {e}. Is Ollama running?")
            # Fallback to zeros to prevent crash, but log critical error
            return np.zeros(self.dimensions, dtype=np.float32)

    def add_document(self, path: str, content: str):
        """Indexes a document (Chunk -> Embed -> Store)."""
        file_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if file changed
        cur = self.db.execute("SELECT hash FROM files WHERE path=?", (path,)).fetchone()
        if cur and cur[0] == file_hash:
            return # Skip unchanged

        logging.info(f"Indexing: {path}")
        
        # Clear old chunks
        self.db.execute("DELETE FROM chunks WHERE path=?", (path,))
        # (Cleanup of vec/fts items happens via cascade or manual ID check, 
        # but for simplicity we'll just overwrite by ID if collision, 
        # technically we should clean up orphaned IDs but we'll skip for speed)

        chunks = self._chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{hashlib.md5(path.encode()).hexdigest()}_{i}"
            embedding = self.get_embedding(chunk)
            
            # 1. Store Metadata
            self.db.execute(
                "INSERT INTO chunks (id, path, content, embedding) VALUES (?, ?, ?, ?)",
                (chunk_id, path, chunk, embedding.tobytes())
            )
            
            # 2. Store Vector
            self.db.execute(
                "INSERT OR REPLACE INTO vec_items (id, embedding) VALUES (?, ?)",
                (chunk_id, embedding)
            )
            
            # 3. Store Text (FTS)
            # Check if exists in FTS first to avoid duplicates or use INSERT OR REPLACE logic if supported
            # FTS doesn't support REPLACE directly on content match easily, so we delete first
            self.db.execute("DELETE FROM fts_items WHERE id=?", (chunk_id,))
            self.db.execute(
                "INSERT INTO fts_items (id, content) VALUES (?, ?)",
                (chunk_id, chunk)
            )

        # Update File Record
        self.db.execute(
            "INSERT OR REPLACE INTO files (path, hash, mtime, last_indexed) VALUES (?, ?, ?, ?)",
            (path, file_hash, os.path.getmtime(path) if os.path.exists(path) else 0, datetime.now().timestamp())
        )
        self.db.commit()

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Naive paragraph-based chunking."""
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        
        for p in paragraphs:
            if len(current) + len(p) < chunk_size:
                current += p + "\n\n"
            else:
                chunks.append(current.strip())
                current = p + "\n\n"
        if current:
            chunks.append(current.strip())
        return chunks

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Hybrid Search using Reciprocal Rank Fusion (RRF)."""
        query_vec = self.get_embedding(query)
        
        # 1. Vector Search
        vec_results = self.db.execute("""
            SELECT id, vec_distance_cosine(embedding, ?) as distance
            FROM vec_items
            WHERE embedding MATCH ? AND k = ?
            ORDER BY distance
        """, (query_vec, query_vec, limit * 2)).fetchall()
        
        # 2. FTS Search
        clean_query = re.sub(r'[^a-zA-Z0-9 ]', '', query) # Sanitize for FTS
        fts_results = self.db.execute("""
            SELECT id, rank
            FROM fts_items
            WHERE fts_items MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (clean_query, limit * 2)).fetchall()
        
        # 3. RRF Fusion
        scores = {}
        k = 60 # RRF constant
        
        for rank, (doc_id, _) in enumerate(vec_results):
            if doc_id not in scores: scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank + 1)
            
        for rank, (doc_id, _) in enumerate(fts_results):
            if doc_id not in scores: scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank + 1)
            
        # Sort by combined score
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        # Retrieve Content
        results = []
        for doc_id, score in sorted_ids:
            row = self.db.execute("SELECT content, path FROM chunks WHERE id=?", (doc_id,)).fetchone()
            if row:
                results.append({
                    "id": doc_id,
                    "content": row[0],
                    "path": row[1],
                    "score": score
                })
                
        return results

if __name__ == "__main__":
    # Self-Test
    mem = MemoryCore()
    if os.path.exists("E:/0x/README.md"):
        with open("E:/0x/README.md", "r") as f:
            mem.add_document("E:/0x/README.md", f.read())
            
    print("Searching for 'Stratmeyer'...")
    res = mem.search("Stratmeyer")
    for r in res:
        print(f"[{r['score']:.4f}] {r['path']}: {r['content'][:100]}...")
