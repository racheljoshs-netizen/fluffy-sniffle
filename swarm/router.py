import os
import sys
import json
import time

sys.path.append("E:/0x/bootcamp")
from scout_drone import ScoutDrone
from archivist_drone import ArchivistDrone

class SwarmRouter:
    def __init__(self):
        print("[Router] Initializing Swarm Nodes...")
        self.scout = ScoutDrone()
        self.archivist = ArchivistDrone()
        self.digest_path = "E:/0x/swarm/intelligence_digest.md"

    def dispatch_task(self, task_type: str, title: str, payload: str):
        print(f"\n[Router] Received Task: {task_type} -> '{title}'")
        
        if task_type.upper() == "SCOUT":
            result = self.scout.analyze_payload(title, payload)
        elif task_type.upper() == "ARCHIVIST":
            result = self.archivist.process_document(title, payload)
        else:
            print(f"[Router] Unknown task type: {task_type}")
            return
            
        self._append_digest(title, task_type, result)

    def _append_digest(self, title: str, source: str, content: str):
        with open(self.digest_path, "a", encoding="utf-8") as f:
            f.write(f"\n## [{source.upper()}] {title} - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(content)
            f.write("\n---\n")
        print(f"[Router] Output committed to intelligence digest: {self.digest_path}")

if __name__ == "__main__":
    router = SwarmRouter()
    print("[Router] Swarm is active and standing by.")
    
    print("\n--- TEST: DISPATCHING TACTICAL TASK TO SCOUT ---")
    router.dispatch_task(
        "SCOUT", 
        "CISA Vulnerability Scan", 
        "New critical vulnerability in standard router firmware. CVE-2026-9999. Requires immediate patching."
    )
    
    print("\n--- TEST: DISPATCHING STRATEGIC TASK TO ARCHIVIST ---")
    router.dispatch_task(
        "ARCHIVIST",
        "MCP Protocol Specs",
        "The Model Context Protocol (MCP) defines a standard communication layer between AI agents and local tools. It uses JSON-RPC over stdio or HTTP..."
    )
