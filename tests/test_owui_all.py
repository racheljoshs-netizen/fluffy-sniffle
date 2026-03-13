import time
from agency.open_web_ui import OpenWebUIClient

def test_all_models():
    print("--- INITIATING OPEN WEB UI FLEET DIAGNOSTIC ---")
    try:
        client = OpenWebUIClient()
        agents = client.list_agents()
        if not agents:
            print("No agents found or auth failed.")
            return
            
        model_ids = [a['id'] for a in agents]
        print(f"Total Models Detected: {len(model_ids)}\n")
        
        working_models = []
        failed_models = []
        
        for idx, model_id in enumerate(model_ids):
            print(f"[{idx+1}/{len(model_ids)}] Testing {model_id}...")
            # Keep it extremely short to save tokens/time if it does work
            response = client.chat(model_id, "Ping. Respond with 'Pong'.")
            
            if "Error:" in response or "Failed" in response or "401" in response or "400" in response or "API key" in response:
                print(f"  -> FAILED: {response[:150]}...")
                failed_models.append(model_id)
            else:
                print(f"  -> SUCCESS: {response[:50]}")
                working_models.append(model_id)
            
            # Brief pause to avoid hammering the local server too hard
            time.sleep(1)
            
        print("\n--- DIAGNOSTIC COMPLETE ---")
        print(f"Working Models ({len(working_models)}):")
        for m in working_models:
            print(f"  - {m}")
            
        print(f"\nFailed Models ({len(failed_models)}):")
        for m in failed_models:
            print(f"  - {m}")

    except Exception as e:
        print(f"Substrate Test Failed: {e}")

if __name__ == "__main__":
    test_all_models()
