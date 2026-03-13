import sqlite3
import os
from pathlib import Path

print("--- [AGENT 1: THE ARCHIVIST] REPL INITIALIZED ---")
db_path = Path("E:/0x/ledger/immutable_v2.db")
db_path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

schema = """
CREATE TABLE IF NOT EXISTS session_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS prevent_update BEFORE UPDATE ON session_logs
BEGIN SELECT RAISE(ABORT, 'IMMUTABLE LEDGER: Updates forbidden.'); END;

CREATE TRIGGER IF NOT EXISTS prevent_delete BEFORE DELETE ON session_logs
BEGIN SELECT RAISE(ABORT, 'IMMUTABLE LEDGER: Deletions forbidden.'); END;
"""
cursor.executescript(schema)
conn.commit()

print(f"Immutable Ledger established at: {db_path.resolve()}")
print("Schema enforced. Triggers active. Ready for raw ingestion.")
print("--- [AGENT 1: THE ARCHIVIST] EXECUTION COMPLETE ---")
