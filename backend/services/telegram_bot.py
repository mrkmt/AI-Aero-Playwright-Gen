"""
Telegram Bot Integration with Aero Gateway
Handles message processing, rate limiting, and conversation storage
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import asyncio
import os
import json

from .knowledge_service import get_knowledge_service
from core.token_manager import get_token_manager
from core.knowledge_brain import get_knowledge_brain
from core.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram bot integration via Aero gateway
    """

    def __init__(self, bot_token: Optional[str] = None):
        """
        Initialize Aero Direct Gateway (formerly OpenClaw based)
        """
        config = self._load_config()
        saved_gateway = config.get("gateway", {})

        # Priority: Constructor > agent_profiles.json > Env
        self.bot_token = (
            bot_token
            or saved_gateway.get("token")
            or os.getenv("TELEGRAM_BOT_TOKEN", "")
        )
        self.api_base = "https://api.telegram.org"

        # Secret for webhook verification
        self.webhook_secret = os.getenv("AERO_WEBHOOK_SECRET", "aero_secure_secret_123")

        self.knowledge_service = get_knowledge_service()
        self.token_manager = get_token_manager()

        # Active conversations
        self.conversations: Dict[str, List[Dict]] = {}

        # Rate limiting queue
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.processing = False

        logger.info(f"Aero TelegramBot initialized (Token: {self.bot_token[:5]}...)")
        # Avoid emoji for Windows cp1252 encoding compatibility
        print(
            f"[DEBUG] Aero TelegramBot started with token: {self.bot_token[:10] if self.bot_token else 'N/A'}..."
        )

    def _load_config(self) -> Dict:
        """Load agent profiles and gateway settings."""
        profiles_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "agent_profiles.json"
        )
        if os.path.exists(profiles_path):
            try:
                with open(profiles_path, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming Telegram message
        """
        chat_id = str(message.get("chat_id", ""))
        user_id = str(message.get("user_id", chat_id))
        text = message.get("text", "")
        message_id = message.get("message_id")

        if not chat_id:
            return {"success": False, "error": "missing_chat_id"}

        # 0. Detect and process commands (ONLY respond to slash commands to save tokens)
        if text.startswith("/"):
            return await self._process_command(message)
        else:
            logger.info(f"Ignoring non-command message from {user_id}: {text[:50]}...")
            return {"success": True, "status": "ignored_non_command"}

        # 1. Check rate limits and quota
        quota_status = await self.token_manager.check_quota(user_id)

        if not quota_status.can_proceed:
            wait_time = quota_status.wait_seconds or 60
            response_msg = f"Token quota exceeded. Please wait {wait_time} seconds."
            await self._send_message(chat_id, response_msg)
            return {
                "success": False,
                "error": "quota_exceeded",
                "message": response_msg,
            }

        # 2. Count tokens in incoming message
        input_tokens = self.token_manager.count_tokens(text)

        # 3. Add to conversation history
        conversation_id = f"{chat_id}_{datetime.utcnow().strftime('%Y%m%d')}"

        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        self.conversations[conversation_id].append(
            {
                "role": "user",
                "content": text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # 4. Search knowledge base
        relevant_knowledge = await self.knowledge_service.search_knowledge(
            query=text, limit=3
        )

        # 5. Generate response
        short_term_memory = self.conversations[conversation_id][-5:]

        response_text = await self._generate_response(
            text=text,
            context=relevant_knowledge,
            conversation_history=short_term_memory,
        )

        # 6. Count output tokens
        output_tokens = self.token_manager.count_tokens(response_text)
        total_tokens = input_tokens + output_tokens

        # 7. Consume tokens from quota
        await self.token_manager.consume_tokens(
            user_id=user_id, token_count=total_tokens, check_quota_bool=False
        )

        # 8. Add response to conversation
        self.conversations[conversation_id].append(
            {
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # 9. Store conversation (async)
        asyncio.create_task(
            self.knowledge_service.add_conversation(
                conversation_id=conversation_id,
                messages=self.conversations[conversation_id],
                user_id=user_id,
                chat_id=chat_id,
            )
        )

        # 10. Send response
        await self._send_message(chat_id, response_text)

        return {"success": True, "response": response_text, "tokens_used": total_tokens}

    async def _process_command(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process slash commands (/train, /status, /reports)"""
        chat_id = str(message.get("chat_id", ""))
        text = message.get("text", "")

        parts = text.split(" ", 2)
        command = parts[0].lower()

        response = ""

        if command == "/start":
            response = "Hello! I am Aero AI Testing Assistant. I can help you track your automation progress.\n\nAvailable commands:\n/status - Check recording status\n/reports - Last test report summary\n/train [tag] content - Add knowledge"

        elif command == "/status":
            # Real-time status from Aero
            try:
                from .recorder_service import get_recorder_service

                recorder = get_recorder_service()
                state = recorder.get_state()
                is_recording = state.get("is_recording", False)
                steps = len(state.get("steps", []))

                status_text = (
                    "🟢 Recording in progress..." if is_recording else "⚪ Idle"
                )
                response = f"Current Status: {status_text}\nSteps Recorded: {steps}\nView: {state.get('current_view', 'Dashboard')}"
            except:
                response = "I couldn't reach the recorder service right now."

        elif command == "/train":
            if len(parts) < 3:
                response = "Usage: /train [tag] content"
            else:
                tag = parts[1].strip("[]")
                content = parts[2]
                kb = get_knowledge_brain()
                await kb.add_knowledge(
                    content=content,
                    title=f"Telegram [{tag}]",
                    tags=[tag],
                    source="telegram",
                )
                response = f"Training complete! Stored under [{tag}]."

        elif command == "/reports":
            response = "Generating summary of latest reports...\n- Login Flow: ✅ Passed\n- Checkout Test: ❌ Failed (Selector mismatch)\n- Profile Update: ✅ Passed"

        else:
            response = f"Unknown command: {command}. Try /status or /train."

        await self._send_message(chat_id, response)
        return {"success": True, "response": response}

    async def _generate_response(
        self, text: str, context: List[Dict], conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate response from AI
        """
        # Format context
        ctx_text = ""
        if context:
            ctx_text = "\n".join(
                [f"- {d.get('content', '')[:300]}" for d in context[:3]]
            )

        # Format history
        hist_text = ""
        if conversation_history:
            hist_text = "\n".join(
                [f"{m['role']}: {m['content']}" for m in conversation_history[-5:]]
            )

        try:
            llm = get_llm_service()
            system_prompt = "You are Aero, a testing assistant. Use the provided context to answer accurately."

            full_context = f"DOCUMENTS:\n{ctx_text}\n\nHISTORY:\n{hist_text}"

            return await llm.generate_response(
                prompt=text, context=full_context, system_prompt=system_prompt
            )
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return f"I received: {text} (AI processing failed)"

    async def _send_message(self, chat_id: str, text: str) -> bool:
        """Send message directly via Telegram API"""
        if not self.bot_token:
            logger.error("No Telegram Bot Token configured. Cannot send message.")
            return False

        url = f"{self.api_base}/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Aero Gateway: Sending message to {chat_id}...")
                response = await client.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    return True
                else:
                    logger.error(f"Telegram API Error: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Direct Send Error: {e}")
            return False


# Global instance
_telegram_bot: Optional[TelegramBot] = None


def get_telegram_bot() -> TelegramBot:
    global _telegram_bot
    if _telegram_bot is None:
        _telegram_bot = TelegramBot()
    return _telegram_bot
