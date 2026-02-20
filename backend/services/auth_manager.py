import os
import json
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self):
        self.profiles_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "agent_profiles.json"
        )

    def check_tokens(self) -> Dict[str, str]:
        """
        Checks validity of acc1, acc2, acc3 tokens.
        Returns a dictionary of {profile_name: status_message}
        """
        results = {}
        
        profiles = self._load_profiles()
        qwen_profiles = [p for p in profiles if "Qwen-Acc" in p.get("name", "")]

        if not qwen_profiles:
            print("ℹ️ No Qwen Account profiles found to check.")
            return {}

        print("🔐 Checking Qwen Authentication Tokens...")
        
        for p in qwen_profiles:
            name = p.get("name")
            auth_file = p.get("auth_file")
            
            if not auth_file or not os.path.exists(auth_file):
                msg = f"❌ Missing auth file: {auth_file}"
                print(f"[{name}] {msg}")
                results[name] = "missing_file"
                continue

            try:
                with open(auth_file, 'r') as f:
                    creds = json.load(f)
                    
                expiry = creds.get("expiry_date")
                # Qwen/Oauth expiry is usually in milliseconds timestamp
                if expiry:
                    # Check if expired (with 1 hour buffer)
                    if time.time() * 1000 > (expiry - 3600000):
                        msg = "⚠️ Token EXPIRED or expiring soon."
                        print(f"[{name}] {msg}")
                        print(f"   💡 ACTION REQUIRED: Run `qwen login` to refresh credentials for {name}.")
                        results[name] = "expired"
                    else:
                        print(f"[{name}] ✅ Token valid.")
                        results[name] = "valid"
                else:
                    # If no expiry date, assume valid but warn
                    print(f"[{name}] ❓ No expiry date found. Assuming valid.")
                    results[name] = "unknown"

            except Exception as e:
                print(f"[{name}] ❌ Error reading token: {e}")
                results[name] = "error"

        return results

    def _load_profiles(self) -> List[Dict]:
        if not os.path.exists(self.profiles_path):
            return []
        try:
            with open(self.profiles_path, "r") as f:
                data = json.load(f)
                return data.get("profiles", [])
        except:
            return []

# Singleton
auth_manager = AuthManager()
