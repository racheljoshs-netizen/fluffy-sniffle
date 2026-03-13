from memory_store import MemoryStore
import json
from datetime import datetime
from hashlib import sha256

class LibrarianService:
    def __init__(self):
        self.store = MemoryStore()

    def upsert(self, content: str, metadata: dict, embedding: list[float] = None):
        return self.store.upsert(content, metadata, embedding)
