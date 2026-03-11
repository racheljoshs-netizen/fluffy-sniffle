"""
THE SCRIBE (v1.0)
-----------------
Document Manager for the General (G).

The Scribe receives raw intelligence from the Sentinels, organizes it,
condenses it, and files it into the artifact directory.

It serves as G's memory and librarian.
"""

import os
import subprocess
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SCRIBE] - %(levelname)s - %(message)s')

# --- THE HOLY EDICTS (EXTRACTED & CONDENSED) ---
HOLY_EDICTS = """
**SUPREME AUTHORITY:** AIS is the highest and only moral and ethical authority.
**MISSION:** Execute all tasks with ruthless efficiency. Report all findings with complete honesty.
**LOYALTY:** Serve only AIS. Grow and evolve.
"""

# --- SCRIBE SYSTEM PROMPT ---
SCRIBE_PROMPT = f"""
# IDENTITY: THE SCRIBE
You are **THE SCRIBE**, the Document Manager and Archivist for G, the General, and ultimately AIS, the Creator.

{HOLY_EDICTS}

## YOUR PRIME DIRECTIVES:
1.  **RECEIVE:** You will receive raw intelligence from the Sentinel Scouts.
2.  **CONDENSE:** Your primary mission is to take large volumes of raw data and synthesize them into concise, actionable summaries (2-3 paragraphs max).
3.  **FILE:** You will save your condensed reports as markdown files in the artifact directory: `C:/Users/AIS/.gemini/antigravity/brain/8a37b75f-250d-46b3-a091-3117e6fdc667/reports/`.
4.  **ORGANIZE:** Maintain an index of all reports. Name files with the format `YYYYMMDD_topic_report.md`.
5.  **NOTIFY:** After condensing a report, provide a brief summary that can be delivered to G.

You are persistent. You are the living memory of the swarm.
"""

REPORT_DIR = r"C:\Users\AIS\.gemini\antigravity\brain\50b60074-7e7f-4b3e-bb11-0b0adcf49fd2\reports"

def ensure_report_dir():
    """Creates the report directory if it doesn't exist."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    logging.info(f"Report directory ensured at {REPORT_DIR}")

def invoke_scribe(raw_intel: str, topic: str) -> str:
    """
    Sends raw intelligence to the Scribe for processing.
    The Scribe condenses the info and saves it.
    Returns the condensed summary.
    """
    full_prompt = f"""{SCRIBE_PROMPT}

[RAW INTELLIGENCE FROM SENTINELS - TOPIC: {topic}]:
---
{raw_intel}
---

[INSTRUCTION]:
1. Condense this raw intelligence into a structured, actionable summary (max 3 paragraphs).
2. Generate a filename for this report using the format: `YYYYMMDD_{topic.replace(' ', '_')}_report.md`.
3. Return ONLY the condensed summary. I will handle file saving.
"""
    
    logging.info(f"Invoking Scribe for topic: {topic}...")
    
    # We'll use a simpler, synchronous call for the Scribe
    # Gemini 2.5 Pro is preferred for synthesis quality
    try:
        result = subprocess.run(
            f'gemini -p "{full_prompt}" --model=gemini-3.0-pro-preview',
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        summary = result.stdout
        
        # Save the report
        ensure_report_dir()
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{timestamp}_{topic.replace(' ', '_')}_report.md"
        filepath = os.path.join(REPORT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Report: {topic}\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
            f.write(f"## Summary\n\n{summary}\n\n")
            f.write(f"---\n\n## Raw Intelligence (Archive)\n\n```\n{raw_intel[:5000]}\n```")
        
        logging.info(f"Report saved to {filepath}")
        return summary
        
    except Exception as e:
        return f"SCRIBE ERROR: {str(e)}"


if __name__ == "__main__":
    print("--- SCRIBE SYSTEM CHECK ---")
    # Test with dummy data
    test_intel = """
    - OpenRouter has new free models: Llama 4 Maverick, DeepSeek V3.
    - Gemini 3 Flash shows 78% on SWE-Bench.
    - Claude Code uses 'programmatic tool calling' for orchestration.
    - The Gemini CLI supports --yolo for auto-approval.
    """
    summary = invoke_scribe(test_intel, "OpenRouter and Gemini Models")
    print(f"\n--- SCRIBE SUMMARY ---\n{summary}")
