import sqlite3
from pathlib import Path
import json

print("--- [AGENT 3: THE EXECUTOR] REPL INITIALIZED ---")

db_path = Path("E:/0x/ledger/immutable_v2.db")

def test_ledger_insertion():
    print("Testing Immutable Ledger Insertion...")
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Test Insert
        cursor.execute(
            "INSERT INTO session_logs (session_id, role, content) VALUES (?, ?, ?)",
            ("test_session_001", "user", "Initiate project Citadel.")
        )
        conn.commit()
        print(" -> SUCCESS: Raw uncompressed log inserted.")
        
        # Test Immutability (Update)
        try:
            cursor.execute("UPDATE session_logs SET content='Tampered' WHERE session_id='test_session_001'")
            conn.commit()
            print(" -> FAILED: Immutability breached. Update was allowed.")
        except sqlite3.OperationalError as e:
            if "IMMUTABLE LEDGER" in str(e) or "abort" in str(e).lower():
                print(f" -> SUCCESS: Immutability enforced on UPDATE. Error caught: {e}")
            else:
                print(f" -> ERROR: Unexpected error on UPDATE: {e}")

        # Test Immutability (Delete)
        try:
            cursor.execute("DELETE FROM session_logs WHERE session_id='test_session_001'")
            conn.commit()
            print(" -> FAILED: Immutability breached. Delete was allowed.")
        except sqlite3.OperationalError as e:
            if "IMMUTABLE LEDGER" in str(e) or "abort" in str(e).lower():
                print(f" -> SUCCESS: Immutability enforced on DELETE. Error caught: {e}")
            else:
                print(f" -> ERROR: Unexpected error on DELETE: {e}")

    except Exception as e:
        print(f" -> FATAL ERROR during Ledger testing: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def test_kinetic_lens():
    print("\nTesting Kinetic Lens Integration logic...")
    try:
        from kinetic_lens_blueprint import KineticLens
        print(" -> SUCCESS: Kinetic Lens Blueprint imported.")
    except Exception as e:
        print(f" -> WARNING: Could not import blueprint natively. Simulating object. Error: {e}")

test_ledger_insertion()
test_kinetic_lens()

print("\n--- [AGENT 3: THE EXECUTOR] EXECUTION COMPLETE ---")
