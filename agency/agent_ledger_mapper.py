import os
from pathlib import Path
import sqlite3

def map_directory_and_propose_schema(base_dir="E:/0x"):
    print(f"--- [AGENT: LEDGER MAPPER] INITIALIZED ---")
    print(f"Target Substrate: {base_dir}\n")
    
    # 1. Map existing log structures
    log_dirs = ["logs", "wiggum_logs", "vox_tmp", "agency", "core"]
    print("--- 1. DIRECTORY TOPOLOGY (RELEVANT TO MEMORY) ---")
    for d in log_dirs:
        p = Path(base_dir) / d
        if p.exists():
            files = list(p.rglob("*.*"))
            print(f"Directory /{d}: {len(files)} files found.")
        else:
            print(f"Directory /{d}: DOES NOT EXIST.")

    # 2. Propose the Directory Structure for the Immutable Ledger
    ledger_dir = Path(base_dir) / "ledger"
    print("\n--- 2. PROPOSED IMMUTABLE LEDGER STRUCTURE ---")
    print(f"MKDIR: {ledger_dir.resolve()}")
    print(f"MKDIR: {ledger_dir.resolve()}/blobs  (For binary artifacts, audio, images)")
    
    # 3. Propose the SQLite Schema
    print("\n--- 3. EXECUTABLE SQL SCHEMA (IMMUTABLE LEDGER) ---")
    schema = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY, -- e.g., UUID or ISO Timestamp
    start_time REAL NOT NULL,
    entity_id TEXT NOT NULL,     -- e.g., 'G-PRIME', 'APOLLO'
    environmental_context TEXT   -- JSON payload of initial state
);

CREATE TABLE IF NOT EXISTS narrative_turns (
    turn_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp REAL NOT NULL,
    role TEXT NOT NULL,          -- 'architect', 'entity', 'system'
    content TEXT NOT NULL,       -- Raw, uncompressed text
    token_count INTEGER,
    action_type TEXT,            -- 'dialogue', 'tool_call', 'tool_result'
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS kinetic_vectors (
    vector_id TEXT PRIMARY KEY,
    turn_id TEXT NOT NULL,
    embedding BLOB NOT NULL,     -- float[768] via sqlite-vec
    FOREIGN KEY(turn_id) REFERENCES narrative_turns(turn_id)
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    turn_id TEXT NOT NULL,
    file_path TEXT NOT NULL,     -- Path relative to ledger/blobs
    mime_type TEXT NOT NULL,
    FOREIGN KEY(turn_id) REFERENCES narrative_turns(turn_id)
);

-- Immutable Triggers (Prevent Updates/Deletes on the Ledger)
CREATE TRIGGER prevent_turn_update BEFORE UPDATE ON narrative_turns
BEGIN SELECT RAISE(ABORT, 'IMMUTABLE LEDGER: Updates are strictly forbidden.'); END;

CREATE TRIGGER prevent_turn_delete BEFORE DELETE ON narrative_turns
BEGIN SELECT RAISE(ABORT, 'IMMUTABLE LEDGER: Deletions are strictly forbidden.'); END;
    """
    print(schema.strip())
    
    print("\n--- [AGENT: LEDGER MAPPER] EXECUTION COMPLETE ---")

if __name__ == "__main__":
    map_directory_and_propose_schema()
