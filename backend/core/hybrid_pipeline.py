import os
from typing import Optional, List, Dict, Any
try:
    import litellm
except ImportError:
    litellm = None
try:
    import ollama
except ImportError:
    ollama = None

import json
import time
from datetime import datetime
from services.activity_service import activity_service

class HybridAIPipeline:
    def __init__(self):
        self.local_model = os.getenv("AI_LOCAL_MODEL", "moondream:latest")
        self.cloud_model = os.getenv("AI_CLOUD_MODEL", "openai/qwen-coder-plus")
        self.use_cloud_threshold = int(os.getenv("AI_CLOUD_THRESHOLD", "500"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "2048"))
        self.daily_quota = int(os.getenv("AI_DAILY_TOKEN_QUOTA", "50000"))
        self.latency_threshold = int(os.getenv("AI_LATENCY_THRESHOLD_MS", "15000"))
        self.qwen_auth_file = os.getenv("QWEN_AUTH_FILE", r"C:\Users\kaung myat thu\.qwen\oauth_creds.json")
        self.aero_gateway_base = os.getenv("AERO_GATEWAY_API_BASE", "")
        self.usage_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "usage_stats.json")
        self.profiles_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agent_profiles.json")
        self._init_usage()

    def _get_dynamic_profile(self, agent_name: str) -> Optional[Dict]:
        """Loads profile from agent_profiles.json for the given agent."""
        if not os.path.exists(self.profiles_path):
            return None
        try:
            with open(self.profiles_path, "r") as f:
                config = json.load(f)
                assignment = config.get("assignments", {}).get(agent_name.upper())
                if assignment:
                    for p in config.get("profiles", []):
                        if p["name"] == assignment:
                            return p
        except Exception as e:
            print(f"⚠️ Failed to load dynamic profiles: {e}")
        return None

    def _init_usage(self):
        """Initializes usage file if not exists."""
        if not os.path.exists(self.usage_file):
            self._save_usage({"date": datetime.now().strftime("%Y-%m-%d"), "total_tokens": 0, "avg_latency_ms": 0})

    def _get_usage(self) -> Dict[str, Any]:
        try:
            with open(self.usage_file, 'r') as f:
                data = json.load(f)
                if data.get("date") != datetime.now().strftime("%Y-%m-%d"):
                    return {"date": datetime.now().strftime("%Y-%m-%d"), "total_tokens": 0, "avg_latency_ms": 0}
                return data
        except:
            return {"date": datetime.now().strftime("%Y-%m-%d"), "total_tokens": 0}

    def _save_usage(self, data: Dict[str, Any]):
        with open(self.usage_file, 'w') as f:
            json.dump(data, f)

    def _update_tokens(self, count: int):
        usage = self._get_usage()
        usage["total_tokens"] += count
        self._save_usage(usage)
        activity_service.add_log(f"Used {count} tokens. Session total: {usage['total_tokens']}/{self.daily_quota}", level="success", agent="Pipeline")
        print(f"📊 Total tokens used today: {usage['total_tokens']}/{self.daily_quota}")

    def _get_qwen_token(self, custom_path: Optional[str] = None) -> Optional[str]:
        """Loads access token from custom_path or default .qwen/oauth_creds.json."""
        path = custom_path or self.qwen_auth_file
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    creds = json.load(f)
                    token = creds.get("access_token")
                    if token:
                        print(f"🔑 Loaded OAuth token from: {os.path.basename(path)}")
                        return token
                    else:
                        print(f"⚠️ Auth file found at {path} but 'access_token' is missing.")
            else:
                pass # Silent if file doesn't exist
        except Exception as e:
            print(f"❌ Error reading auth file at {path}: {e}")
        return None

    def _get_fallback_chain(self, start_agent: Optional[str] = None) -> List[Dict]:
        """
        Constructs a chain of profiles to try:
        1. Specific Agent Profile (if exists) [Qwen-Acc-X]
        2. Other Qwen Accounts (Round Robin) [Qwen-Acc-Y, Qwen-Acc-Z]
        3. Cloud Fallback Models [GPT-OSS, Qwen3-Coder, Minimax]
        4. Local Model [Last Resort]
        """
        chain = []
        all_profiles = []
        
        # Load all profiles
        if os.path.exists(self.profiles_path):
            try:
                with open(self.profiles_path, "r") as f:
                    data = json.load(f)
                    all_profiles = data.get("profiles", [])
                    gateway_token = data.get("gateway", {}).get("token")
            except:
                pass

        # 1. Start Agent
        current_profile_name = None
        if start_agent:
            profile = self._get_dynamic_profile(start_agent)
            if profile:
                chain.append(profile)
                current_profile_name = profile["name"]

        # 2. Other Qwen Accounts (Simple Rotation) - REMOVED per user request
        # qwen_accounts = [p for p in all_profiles if "Qwen-Acc" in p["name"] and p["name"] != current_profile_name]
        # chain.extend(qwen_accounts)

        # 2. Cloud Fallbacks (GPT-OSS, Minimax, etc.)
        cloud_fallbacks = [p for p in all_profiles if "Cloud" in p["name"] or "GPT-OSS" in p["name"]]
        # Inject gateway token if needed
        for p in cloud_fallbacks:
            if p.get("api_key") == "from_gateway" and gateway_token:
                p["api_key"] = gateway_token
        chain.extend(cloud_fallbacks)

        return chain

    async def generate_with_fallback(self, prompt: str, system_prompt: Optional[str] = None, force_cloud: bool = False, agent_name: Optional[str] = None) -> str:
        """
        Robust Generation with Auto-Rotation and Fallback Chain.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Get the execution chain
        chain = self._get_fallback_chain(agent_name)
        
        # Quota Check before starting cloud chain
        usage = self._get_usage()
        if usage["total_tokens"] >= self.daily_quota and not force_cloud:
            print(f"🛑 Daily Quota Reached. Skipping Cloud Chain.")
            return await self._call_local_async(messages)

        # Iterate through chain
        for profile in chain:
            model = profile.get("model")
            auth_file = profile.get("auth_file")
            api_base = profile.get("api_base")
            api_key = profile.get("api_key")
            profile_name = profile.get("name", "Unknown")

            # Load Token from file if needed
            token = api_key
            if auth_file:
                 token = self._get_qwen_token(auth_file)
            
            if not token:
                print(f"⚠️ Skipping {profile_name}: No token found.")
                continue

            print(f"🔄 [{agent_name or 'Global'}] Trying {profile_name} ({model})...")
            
            try:
                if not litellm:
                    raise ImportError("LiteLLM not installed")
                
                start_time = time.time()
                
                # LiteLLM call
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "api_key": token,
                    "max_tokens": profile.get("max_tokens", self.max_tokens)
                }
                if api_base:
                    kwargs["api_base"] = api_base

                response = await litellm.acompletion(**kwargs)
                
                latency = (time.time() - start_time) * 1000
                activity_service.add_log(f"Success: {profile_name} responded in {latency:.0f}ms", level="success", agent=agent_name or "Global")
                print(f"✅ [{agent_name}] Success with {profile_name}!")

                # Update usage
                usage_info = getattr(response, 'usage', None)
                if usage_info:
                    self._update_tokens(usage_info.total_tokens)
                    
                return response.choices[0].message.content

            except Exception as e:
                error_str = str(e)
                if "AuthenticationError" in error_str or "401" in error_str:
                    print(f"❌ Auth Failed for {profile_name}. Rotating to next option...")
                    activity_service.add_log(f"Auth Failed: {profile_name}. Rotating...", level="warning", agent=agent_name or "Global")
                else:
                    print(f"⚠️ Error with {profile_name}: {e}")
                    
                # Continue to next item in chain

        print("🔻 All Cloud options failed. Falling back to Local.")
        activity_service.add_log("All Cloud options failed. Using Local Model.", level="error", agent=agent_name or "Global")
        return await self._call_local_async(messages)
    async def _call_local_async(self, messages: List[Dict[str, str]]) -> str:
        """Calls local Ollama asynchronously with latency monitoring."""
        start_time = time.time()
        try:
            if not ollama:
                raise ImportError("Ollama library not installed")
            
            print(f"🏠 Routing to Local Model ({self.local_model})...")
            response = await litellm.acompletion(
                model=f"ollama/{self.local_model}",
                messages=messages,
                api_base="http://localhost:11434"
            )
            
            latency = (time.time() - start_time) * 1000
            print(f"🏠 Local responded in {latency:.0f}ms")

            if latency > self.latency_threshold:
                print(f"🐢 CRITICAL SLOWNESS: Local AI took {latency:.0f}ms (Threshold: {self.latency_threshold}ms).")
                print("💡 Recommendation: Check your GPU usage or switch to Cloud (Qwen) by updating your API key.")

            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Hybrid Pipeline Error: Both Cloud and Local failed. ({e})"

    async def route_query(self, prompt: str, task_type: str = "general") -> str:
        """Legacy routing logic maintained for backward compatibility."""
        if task_type in ["generation", "complex_healing"] or len(prompt.split()) > self.use_cloud_threshold:
            return await self.generate_with_fallback(prompt)
        else:
            messages = [{"role": "user", "content": prompt}]
            return await self._call_local_async(messages)

pipeline = HybridAIPipeline()
