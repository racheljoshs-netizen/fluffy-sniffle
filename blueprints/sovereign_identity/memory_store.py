import sqlite3
import json
from datetime import datetime
from hashlib import sha256
import chromadb
import numpy as np

class MemoryStore:
    def __init__(self, sqlite_path="sovereign_memory.db", chroma_path="./sovereign_chroma"):
        self.conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="sovereign_memories", 
            metadata={"hnsw:space": "cosine"}
        )
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                identity_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES memories(id),
                FOREIGN KEY (target_id) REFERENCES memories(id)
            );
            CREATE TABLE IF NOT EXISTS raw_logs (
                id TEXT PRIMARY KEY, 
                content TEXT, 
                metadata TEXT, 
                timestamp TEXT
            );
            CREATE TABLE IF NOT EXISTS heuristic_cards (
                id TEXT PRIMARY KEY,
                card_type TEXT NOT NULL,  -- person/event/place/noun
                title TEXT NOT NULL,
                content TEXT NOT NULL,    -- condensed heuristic
                emotional_valence TEXT,
                relevance_score REAL DEFAULT 1.0,
                timestamp TEXT NOT NULL,
                identity_hash TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_identity ON memories(identity_hash);
            CREATE INDEX IF NOT EXISTS idx_source ON relations(source_id);
            CREATE INDEX IF NOT EXISTS idx_target ON relations(target_id);
            CREATE INDEX IF NOT EXISTS idx_card_type ON heuristic_cards(card_type);
        """)
        self.conn.commit()

    def log_raw(self, content: str, metadata: dict):
        hid = sha256((content + json.dumps(metadata, sort_keys=True)).encode()).hexdigest()
        ts = datetime.utcnow().isoformat()
        self.conn.execute("INSERT OR IGNORE INTO raw_logs VALUES (?,?,?,?)", (hid, content, json.dumps(metadata), ts))
        self.conn.commit()

    def forge_heuristic(self, card_type: str, title: str, content: str, emotional_valence: str = None, relevance: float = 1.0):
        hid = sha256((title + content).encode()).hexdigest()
        ts = datetime.utcnow().isoformat()
        self.conn.execute("""
            INSERT INTO heuristic_cards (id, card_type, title, content, emotional_valence, relevance_score, timestamp, identity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                content = excluded.content,
                relevance_score = excluded.relevance_score,
                timestamp = excluded.timestamp
        """, (hid, card_type, title, content, emotional_valence, relevance, ts, hid))
        self.conn.commit()
        return hid

    def get_relevant_heuristics(self, limit: int = 20, min_relevance: float = 0.7) -> list:
        cursor = self.conn.cursor()
        cursor.execute("SELECT title, content, emotional_valence FROM heuristic_cards WHERE relevance_score >= ? ORDER BY timestamp DESC LIMIT ?", (min_relevance, limit))
        return cursor.fetchall()

    def upsert(self, content: str, metadata: dict, embedding: list[float] = None) -> str:
        """Atomic upsert with identity hash. Embedding optional (list of floats for Chroma)."""
        identity_hash = sha256((content + json.dumps(metadata, sort_keys=True)).encode()).hexdigest()
        ts = datetime.utcnow().isoformat()
        meta_json = json.dumps(metadata)

        # SQLite write (transaction start)
        self.conn.execute("BEGIN IMMEDIATE;")
        try:
            self.conn.execute("""
                INSERT INTO memories (id, content, metadata, timestamp, identity_hash)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    content = excluded.content,
                    metadata = excluded.metadata,
                    timestamp = excluded.timestamp,
                    identity_hash = excluded.identity_hash
            """, (identity_hash, content, meta_json, ts, identity_hash))

            # Chroma vector write (if provided)
            if embedding is not None:
                self.collection.upsert(
                    ids=[identity_hash],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[content]
                )

            self.conn.commit()
            return identity_hash
        except Exception:
            self.conn.rollback()
            raise

    def add_relation(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        """Add directed graph edge with weight."""
        ts = datetime.utcnow().isoformat()
        self.conn.execute("""
            INSERT INTO relations (source_id, target_id, relation_type, weight, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (source_id, target_id, relation_type, weight, ts))
        self.conn.commit()

    def retrieve_graph_context(self, limit: int = 512, min_weight: float = 0.0) -> list:
        """BFS-style recent + related memories. Returns list of dicts."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.id, m.content, m.metadata, m.timestamp, r.relation_type, r.weight
            FROM memories m
            LEFT JOIN relations r ON m.id = r.source_id OR m.id = r.target_id
            WHERE (r.weight IS NULL OR r.weight >= ?)
            ORDER BY m.timestamp DESC
            LIMIT ?
        """, (min_weight, limit))
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]),
                "timestamp": row[3],
                "relation": row[4],
                "weight": row[5]
            }
            for row in rows
        ]

    def semantic_search(self, query_embedding: list[float], top_k: int = 32, identity_filter: str = None) -> list:
        """Chroma vector search, optionally filtered by identity_hash."""
        where = {"identity_hash": identity_filter} if identity_filter else None
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        return results

    def close(self):
        self.conn.close()
