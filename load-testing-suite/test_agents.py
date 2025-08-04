# test_agents.py
import requests
import json
import os

# Twoje Cloud Run URLs
AGENT_URLS = {
   "crewai": os.getenv("CREWAI_URL", "https://crewai-agent-REPLACE.run.app"),
   "langraph": os.getenv("LANGRAPH_URL", "https://langraph-agent-REPLACE.run.app"), 
   "adk": os.getenv("ADK_URL", "https://adk-agent-REPLACE.run.app")
}

# Przykładowe zadania dopasowane do każdego agenta
TEST_TASKS = {
    "crewai": {
        "task_type": "research",
        "description": "Research about AI agents",
        "context": {"keywords": ["AI", "agents", "2025"]},
        "collaborators": {}
    },
    "langraph": {
        "task_type": "decision_making",
        "description": "Decide best approach to data processing",
        "context": {"options": ["parallel", "sequential", "hybrid"]},
        "collaborators": {}
    },
    "adk": {
        "task_type": "data_analysis",
        "description": "Analyze sample dataset for trends",
        "context": {"data": [1, 2, 3, 4, 5]},
        "collaborators": {}
    }
}

def test_agent(name, url):
    print(f"\nTesting {name} agent...")

    try:
        # Health check
        response = requests.get(f"{url}/health", timeout=10)
        print(f"Health: {response.status_code} - {response.json()}")

        # Capabilities
        response = requests.get(f"{url}/capabilities", timeout=10)
        capabilities = response.json()
        print(f"Capabilities: {response.status_code} - {len(capabilities)} capabilities")

        # Spec
        response = requests.get(f"{url}/spec", timeout=10)
        spec = response.json()
        print(f"Spec: {response.status_code} - Agent: {spec.get('agent_id', 'unknown')}")

        # Execute task
        test_task = TEST_TASKS.get(name)
        if test_task:
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{url}/execute", data=json.dumps(test_task), headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                print(f"Execute: {response.status_code} - Success: {result['success']} - Result: {result.get('result', {})}")
            else:
                print(f"Execute: {response.status_code} - Failed to execute task: {response.text}")
        else:
            print("⚠️ No test task defined for this agent.")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing Cloud Run Agents...")

    for name, url in AGENT_URLS.items():
        success = test_agent(name, url)
        if not success:
            print(f"❌ {name} agent failed")
        else:
            print(f"✅ {name} agent OK")

    print("\nDone!")

