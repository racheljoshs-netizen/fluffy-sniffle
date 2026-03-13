from agency.open_web_ui import OpenWebUIClient

def test_substrate():
    try:
        client = OpenWebUIClient()
        agents = client.list_agents()
        if not agents:
            print("No agents found or auth failed.")
            return
            
        # Try a Gemini model that might be correctly configured
        target_model = "google_ai_studio_gemini_integration_for_openwebui.gemini/gemini-2.0-flash"
        
        # Fallback to DeepSeek R1 via OpenRouter pipe if Gemini isn't there
        if target_model not in [a['id'] for a in agents]:
            target_model = "openrouter_reasoning_tokens_pipe.reasoning/deepseek/deepseek-r1:free"
            
        if target_model not in [a['id'] for a in agents]:
            target_model = agents[0]['id'] # Absolute fallback
            
        print(f"Sending test ping to {target_model}...")
        response = client.chat(target_model, "Identify yourself. Are you receiving telemetry from the Stratmeyer Core?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Substrate Test Failed: {e}")

if __name__ == "__main__":
    test_substrate()