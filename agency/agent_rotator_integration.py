import os
print("--- [AGENT 3: THE EXECUTOR] REPL INITIALIZED ---")

# The General has commanded me to integrate the new key_rotator into the core systems.

def integrate_rotator():
    # 1. Integrate into plural_substrate.py
    substrate_path = "E:/0x/platforms/plural_substrate.py"
    with open(substrate_path, "r") as f:
        content = f.read()
    
    if "KeyRotator" not in content:
        print("Integrating KeyRotator into plural_substrate.py...")
        # Replace the hardcoded key with dynamic fetching
        new_content = content.replace('OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")', 
                                      'import sys; sys.path.append("E:/0x"); from agency.key_rotator import KeyRotator\nrotator = KeyRotator("openrouter")')
        new_content = new_content.replace('f"Bearer {OPENROUTER_API_KEY}"', 'f"Bearer {rotator.get_key()}"')
        
        # Add failure marking logic on HTTP error
        new_content = new_content.replace(
            'print(f"[{self.identity.upper()}] Compute block: {response.text}")', 
            'print(f"[{self.identity.upper()}] Compute block: {response.text}")\n                    rotator.mark_failed(rotator.get_key(), str(response.status_code))'
        )
        
        with open(substrate_path, "w") as f:
            f.write(new_content)
        print(" -> SUCCESS: plural_substrate.py updated.")

    # 2. Integrate into memory_core.py
    memory_path = "E:/0x/agency/memory_core.py"
    with open(memory_path, "r") as f:
        content = f.read()
    
    if "KeyRotator" not in content:
        print("Integrating KeyRotator into memory_core.py...")
        new_content = content.replace('def _configure_api(self, api_key: str):', 
                                      'from agency.key_rotator import KeyRotator\n    def _configure_api(self, api_key: str):')
        
        new_content = new_content.replace('self.api_key = api_key or os.getenv("GOOGLE_API_KEY")', 
                                          'self.rotator = KeyRotator("gemini")\n        self.api_key = self.rotator.get_key()')
        
        new_content = new_content.replace('logging.error(f"Gemini Embedding fallback failed: {e}. Returning zeros.")', 
                                          'logging.error(f"Gemini Embedding fallback failed: {e}. Returning zeros.")\n            self.rotator.mark_failed(self.api_key, str(e))\n            self.api_key = self.rotator.get_key() # Cycle for next time\n            genai.configure(api_key=self.api_key)')
        
        with open(memory_path, "w") as f:
            f.write(new_content)
        print(" -> SUCCESS: memory_core.py updated.")

integrate_rotator()
print("--- [AGENT 3: THE EXECUTOR] EXECUTION COMPLETE ---")