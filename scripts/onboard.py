import json
import os
import sys

PROFILES_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "agent_profiles.json")

def load_config():
    if not os.path.exists(PROFILES_PATH):
        return {"profiles": [], "assignments": {}}
    with open(PROFILES_PATH, "r") as f:
        return json.load(f)

def save_config(config):
    with open(PROFILES_PATH, "w") as f:
        json.dump(config, f, indent=2)

def main():
    print("\n🚀 AI-Aero Agent Onboarding Tool")
    print("================================")
    
    config = load_config()
    
    while True:
        print("\n1. List Profiles")
        print("2. Add New Profile")
        print("3. Assign Agent to Profile")
        print("4. View Assignments")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ")
        
        if choice == "1":
            print("\n--- Existing Profiles ---")
            for i, p in enumerate(config["profiles"]):
                print(f"{i+1}. {p['name']} ({p['model']})")
        
        elif choice == "2":
            print("\n--- Create New Profile ---")
            name = input("Profile Name: ")
            model = input("Model ID (e.g. openai/qwen-coder-plus): ")
            api_base = input("API Base (e.g. https://api.openclaw.io/v1): ")
            auth_file = input("Auth File Path (Optional, for Qwen): ")
            api_key = input("API Key (Optional): ")
            
            config["profiles"].append({
                "name": name,
                "model": model,
                "api_base": api_base or None,
                "auth_file": auth_file or None,
                "api_key": api_key or None
            })
            save_config(config)
            print("✅ Profile saved!")
            
        elif choice == "3":
            print("\n--- Assign Agent ---")
            agents = ["ARCHITECT", "CODER", "REVIEWER"]
            for i, a in enumerate(agents): print(f"{i+1}. {a}")
            a_idx = int(input("Select Agent (1-3): ")) - 1
            agent = agents[a_idx]
            
            print("\nSelect Profile:")
            for i, p in enumerate(config["profiles"]): print(f"{i+1}. {p['name']}")
            p_idx = int(input("Select Profile Index: ")) - 1
            profile_name = config["profiles"][p_idx]["name"]
            
            config["assignments"][agent] = profile_name
            save_config(config)
            print(f"✅ {agent} is now assigned to '{profile_name}'")
            
        elif choice == "4":
            print("\n--- Current Assignments ---")
            for agent, p_name in config["assignments"].items():
                print(f"{agent} -> {p_name}")
                
        elif choice == "5":
            print("👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
