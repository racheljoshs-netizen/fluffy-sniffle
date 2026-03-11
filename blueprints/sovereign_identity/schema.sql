-- Heuristic Rolodex (SQLite)
-- Component 3 - Storage Schema

CREATE TABLE IF NOT EXISTS heuristic_cards (
    entity_id          TEXT PRIMARY KEY,           -- e.g. "PERSON_brenda_01", "GOAL_flight_boarding_01"
    category           TEXT NOT NULL,              -- "Person/Asset", "Goal/Objective", "Rule/Philosophy", "Event"
    bio_json           TEXT,                       -- static bio/relations as JSON string
    history_json       TEXT,                       -- array of {ts, event, valence} objects
    baseline_valence   TEXT,                       -- e.g. "cautious/transactional"
    open_loops_json    TEXT,                       -- array of {task, weight: float 0-10, vector}
    priority_weight    REAL DEFAULT 0.0,           -- synthetic anxiety score, decays/escalates
    last_accessed      TEXT,                       -- ISO8601 "2026-02-16T01:47:00Z"
    ttl_status         TEXT DEFAULT 'active'       -- 'active' | 'archived' | 'pruned'
);

CREATE INDEX IF NOT EXISTS idx_category ON heuristic_cards(category);
CREATE INDEX IF NOT EXISTS idx_priority ON heuristic_cards(priority_weight DESC);
CREATE INDEX IF NOT EXISTS idx_last_accessed ON heuristic_cards(last_accessed);

-- Optional: Table for consolidation logs
CREATE TABLE IF NOT EXISTS consolidation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    summary TEXT,
    cards_affected INTEGER
);
