import os
import sys
from pathlib import Path

print("--- [AGENT 3: THE EXECUTOR] REPL INITIALIZED ---")

# Task: Execute Project A, Layer 2 (Kinetic Lens Integration)
# We will rewrite MemoryCore to include the KineticLens reasoning loop.

def integrate_kinetic_lens():
    memory_path = Path("E:/0x/agency/memory_core.py")
    blueprint_path = Path("E:/0x/agency/kinetic_lens_blueprint.py")
    
    if not memory_path.exists() or not blueprint_path.exists():
        print("Error: Required files missing for integration.")
        return

    print("Integrating KineticLens into MemoryCore...")
    
    with open(memory_path, "r") as f:
        core_content = f.read()
        
    with open(blueprint_path, "r") as f:
        # We only need the class definition logic, but let's just make sure it's available
        pass

    # We need to add the kinetic lens retrieval to the search method or as a dedicated context generator.
    # Let's add a 'get_kinetic_context' method to MemoryCore.
    
    new_method = """
    def get_kinetic_context(self, current_prompt: str, limit: int = 50) -> str:
        \"\"\"
        LAYER 2: THE KINETIC LENS
        Uses a reasoning model to compress raw logs into a heuristic card.
        \"\"\"
        try:
            from agency.kinetic_lens_blueprint import KineticLens
            from agency.open_web_ui import OpenWebUIClient

            client = OpenWebUIClient()
            lens = KineticLens(self.db_path, client)

            # 1. Pull raw narrative
            narrative = lens.pull_recent_narrative(limit=limit)

            # 2. Generate Heuristic Card via Reasoning Model
            card = lens.generate_heuristic_card(narrative)

            # 3. Inject context
            return lens.inject_context(current_prompt, card)
        except Exception as e:
            logging.error(f"Kinetic Lens Failure: {e}")
            return current_prompt # Fallback to raw prompt
    """

    
    if "get_kinetic_context" not in core_content:
        # Insert before the closing __main__ block
        insertion_point = core_content.find('if __name__ == "__main__":')
        updated_content = core_content[:insertion_point] + new_method + "\n" + core_content[insertion_point:]
        
        with open(memory_path, "w") as f:
            f.write(updated_content)
        print(" -> SUCCESS: MemoryCore now equipped with Kinetic Lens Reasoning.")
    else:
        print(" -> Kinetic Lens already integrated.")

integrate_kinetic_lens()
print("--- [AGENT 3: THE EXECUTOR] EXECUTION COMPLETE ---")
