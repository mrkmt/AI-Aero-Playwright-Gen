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

class HybridAIPipeline:
    def __init__(self):
        self.local_model = os.getenv("AI_LOCAL_MODEL", "moondream:latest")
        self.cloud_model = os.getenv("AI_CLOUD_MODEL", "openai/qwen-coder-plus")
        self.use_cloud_threshold = int(os.getenv("AI_CLOUD_THRESHOLD", "500"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "2048"))
        self.daily_quota = int(os.getenv("AI_DAILY_TOKEN_QUOTA", "50000"))
        self.latency_threshold = int(os.getenv("AI_LATENCY_THRESHOLD_MS", "15000"))
        self.qwen_auth_file = os.getenv("QWEN_AUTH_FILE", r"C:\Users\kaung myat thu\.qwen\oauth_creds.json")
        self.openclaw_base = os.getenv("OPENCLAW_API_BASE", "")
        self.usage_file = "usage_stats.json"
        self._init_usage()

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
        print(f"📊 Total tokens used today: {usage['total_tokens']}/{self.daily_quota}")

    def _get_qwen_token(self) -> Optional[str]:
        """Loads access token from .qwen/oauth_creds.json."""
        try:
            if os.path.exists(self.qwen_auth_file):
                with open(self.qwen_auth_file, 'r') as f:
                    creds = json.load(f)
                    return creds.get("access_token")
        except Exception as e:
            print(f"⚠️ Failed to load Qwen token: {e}")
        return None

    async def generate_with_fallback(self, prompt: str, system_prompt: Optional[str] = None, force_cloud: bool = False) -> str:
        """
        Tries Cloud model first, falls back to Local Ollama if it fails or quota is exceeded.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Quota Check
        usage = self._get_usage()
        if usage["total_tokens"] >= self.daily_quota and not force_cloud:
            print(f"🛑 Daily Quota Reached. Forcing Local Fallback.")
            return await self._call_local_async(messages)

        # Load Token
        token = self._get_qwen_token() or os.getenv("QWEN_API_KEY")
        if not token:
            print("⚠️ No Qwen API key or OAuth token found. Falling back to Local.")
            return await self._call_local_async(messages)

        start_time = time.time()
        print(f"☁️ Attempting Cloud Generation ({self.cloud_model})...")
        try:
            if not litellm:
                raise ImportError("LiteLLM not installed")
            
            # LiteLLM call with custom base (OpenClaw) and token
            kwargs = {
                "model": self.cloud_model,
                "messages": messages,
                "api_key": token,
                "max_tokens": self.max_tokens
            }
            if self.openclaw_base:
                kwargs["api_base"] = self.openclaw_base
                print(f"🔗 Proxying through OpenClaw: {self.openclaw_base}")

            response = await litellm.acompletion(**kwargs)
            
            latency = (time.time() - start_time) * 1000
            print(f"✅ Cloud responded in {latency:.0f}ms")

            # Update token usage
            usage_info = getattr(response, 'usage', None)
            if usage_info:
                self._update_tokens(usage_info.total_tokens)
                
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ Cloud Generation Failed: {e}. Falling back to Local.")
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
                print(f"🐢 Local AI is too slow ({latency:.0f}ms). Suggesting cloud next time.")

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
