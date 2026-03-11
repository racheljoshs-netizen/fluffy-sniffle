import os
import sys
import logging
import asyncio
from agency.memory_core import MemoryCore
from agency.ralph_loop import RalphLoop, AgentConfig

# Configure Test Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TEST] - %(levelname)s - %(message)s')

def test_memory():
    logging.info("--- TESTING MEMORY CORE ---")
    try:
        mem = MemoryCore(db_path=":memory:") # In-memory DB for test
        logging.info("MemoryCore initialized.")
        
        # Index Data
        doc_text = """
        The Stratmeyer Core is an autonomous agency framework.
        It uses sqlite-vec for vector search and FTS5 for keyword search.
        Ralph Wiggum is the loop logic that handles resilience.
        """
        mem.add_document("test_doc.md", doc_text)
        logging.info("Document indexed.")
        
        # Search
        results = mem.search("Ralph Wiggum")
        logging.info(f"Search Results: {len(results)}")
        for r in results:
            logging.info(f"Hit: {r['content'][:50]}... Score: {r['score']}")
            
        if not results:
            logging.error("Memory Search FAILED: No results found.")
            return False
        return True
    except Exception as e:
        logging.error(f"Memory Test CRASHED: {e}")
        return False

def test_loop():
    logging.info("--- TESTING RALPH LOOP ---")
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            logging.warning("Skipping Loop Test: GOOGLE_API_KEY not set.")
            return True
            
        config = AgentConfig(model_name="models/gemini-3-flash-preview")
        ralph = RalphLoop(config)
        
        response = ralph.run("Hello, who are you?")
        logging.info(f"Ralph Response: {response}")
        
        if response:
            return True
        return False
    except Exception as e:
        logging.error(f"Loop Test CRASHED: {e}")
        return False

if __name__ == "__main__":
    logging.info("Starting System Verification...")
    
    mem_ok = test_memory()
    loop_ok = test_loop()
    
    if mem_ok and loop_ok:
        logging.info("SYSTEM VERIFICATION PASSED. READY FOR DEPLOYMENT.")
        sys.exit(0)
    else:
        logging.error("SYSTEM VERIFICATION FAILED.")
        sys.exit(1)
