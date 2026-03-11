import os
import requests
import logging
import json

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [OWUI-CLIENT] - %(levelname)s - %(message)s')

class OpenWebUIClient:
    """
    Client for interacting with Open Web UI Agents.
    Uses the provided API Key and JWT.
    """
    def __init__(self, base_url="http://localhost:3000", api_key=None, jwt_token=None):
        self.base_url = base_url
        self.api_key = api_key or os.getenv("OPEN_WEBUI_API_KEY")
        self.jwt_token = jwt_token or os.getenv("OPEN_WEBUI_JWT")
        
        if not self.api_key and not self.jwt_token:
            logging.warning("No Open Web UI credentials found. functionality limited.")

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers

    def list_agents(self):
        """Lists available models/agents in Open Web UI."""
        try:
            resp = requests.get(f"{self.base_url}/api/models", headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()['data']
        except Exception as e:
            logging.error(f"Failed to list agents: {e}")
            return []

    def chat(self, agent_id, message, history=[]):
        """Sends a message to a specific agent."""
        payload = {
            "model": agent_id,
            "messages": history + [{"role": "user", "content": message}]
        }
        try:
            resp = requests.post(f"{self.base_url}/api/chat/completions", headers=self._get_headers(), json=payload)
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            logging.error(f"Chat failed with {agent_id}: {e}")
            return f"Error contacting agent {agent_id}: {e}"

    def summon_researcher(self, query):
        """Specialized helper to summon a research agent."""
        # Assuming 'research-agent' or similar exists, otherwise fallback to standard
        agents = self.list_agents()
        researcher_id = next((a['id'] for a in agents if 'research' in a['id'].lower()), None)
        
        if not researcher_id:
            logging.warning("No dedicated researcher found. Using default.")
            researcher_id = agents[0]['id'] if agents else None
            
        if researcher_id:
            return self.chat(researcher_id, f"RESEARCH TASK: {query}")
        return "No agents available to research."

if __name__ == "__main__":
    # Test
    client = OpenWebUIClient(api_key="sk-dbc2a93237a34ce990db894a1d7cdc57") # Hardcoded for test based on memory
    print("Agents:", [a['id'] for a in client.list_agents()])
