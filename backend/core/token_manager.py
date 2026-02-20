"""
Token Management Service
Tracks and enforces token usage limits to prevent quota exceeded errors
"""

import tiktoken
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuotaStatus:
    """Token quota status"""
    user_id: str
    minute_used: int
    minute_limit: int
    hour_used: int
    hour_limit: int
    day_used: int
    day_limit: int
    can_proceed: bool
    wait_seconds: Optional[int] = None


@dataclass
class UsageStats:
    """Token usage statistics"""
    user_id: str
    total_tokens: int
    input_tokens: int
    output_tokens: int
    request_count: int
    cost_estimate: float
    period_start: datetime
    period_end: datetime


class TokenManager:
    """
    Manages token counting and quota enforcement
    Prevents 429 (quota exceeded) errors
    """
    
    def __init__(self):
        """Initialize token manager with default limits"""
        # Default limits (configurable via settings)
        self.limits = {
            "per_message": 4000,
            "per_minute": 10000,
            "per_hour": 50000,
            "per_day": 500000,
            "max_concurrent": 5
        }
        
        # In-memory tracking (should be moved to database for production)
        self.usage: Dict[str, Dict] = {}
        
        # Token encoder (using GPT-3.5 encoding as default)
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except:
            self.encoding = None
        
        logger.info("TokenManager initialized with default limits")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        """
        if not text:
            return 0
            
        try:
            if self.encoding:
                tokens = self.encoding.encode(text)
                return len(tokens)
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4
    
    async def check_quota(self, user_id: str) -> QuotaStatus:
        """
        Check if user has quota available
        """
        now = datetime.utcnow()
        
        # Initialize user tracking if not exists
        if user_id not in self.usage:
            self.usage[user_id] = {
                "minute": {"tokens": 0, "reset_at": now + timedelta(minutes=1)},
                "hour": {"tokens": 0, "reset_at": now + timedelta(hours=1)},
                "day": {"tokens": 0, "reset_at": now + timedelta(days=1)}
            }
        
        user_usage = self.usage[user_id]
        
        # Reset counters if time period has passed
        for period in ["minute", "hour", "day"]:
            if now >= user_usage[period]["reset_at"]:
                user_usage[period]["tokens"] = 0
                if period == "minute":
                    user_usage[period]["reset_at"] = now + timedelta(minutes=1)
                elif period == "hour":
                    user_usage[period]["reset_at"] = now + timedelta(hours=1)
                else:
                    user_usage[period]["reset_at"] = now + timedelta(days=1)
        
        # Check if any limit is exceeded
        minute_ok = user_usage["minute"]["tokens"] < self.limits["per_minute"]
        hour_ok = user_usage["hour"]["tokens"] < self.limits["per_hour"]
        day_ok = user_usage["day"]["tokens"] < self.limits["per_day"]
        
        can_proceed = minute_ok and hour_ok and day_ok
        
        # Calculate wait time if quota exceeded
        wait_seconds = None
        if not can_proceed:
            if not minute_ok:
                wait_seconds = int((user_usage["minute"]["reset_at"] - now).total_seconds())
            elif not hour_ok:
                wait_seconds = int((user_usage["hour"]["reset_at"] - now).total_seconds())
            elif not day_ok:
                wait_seconds = int((user_usage["day"]["reset_at"] - now).total_seconds())
        
        return QuotaStatus(
            user_id=user_id,
            minute_used=user_usage["minute"]["tokens"],
            minute_limit=self.limits["per_minute"],
            hour_used=user_usage["hour"]["tokens"],
            hour_limit=self.limits["per_hour"],
            day_used=user_usage["day"]["tokens"],
            day_limit=self.limits["per_day"],
            can_proceed=can_proceed,
            wait_seconds=wait_seconds
        )
    
    async def consume_tokens(
        self,
        user_id: str,
        token_count: int,
        check_quota_bool: bool = True
    ) -> bool:
        """
        Consume tokens from user's quota
        """
        if check_quota_bool:
            quota_status = await self.check_quota(user_id)
            if not quota_status.can_proceed:
                logger.warning(f"Quota exceeded for user {user_id}")
                return False
        
        # Initialize if needed
        if user_id not in self.usage:
            await self.check_quota(user_id)
        
        # Consume tokens
        user_usage = self.usage[user_id]
        user_usage["minute"]["tokens"] += token_count
        user_usage["hour"]["tokens"] += token_count
        user_usage["day"]["tokens"] += token_count
        
        logger.info(f"Consumed {token_count} tokens for user {user_id}")
        return True
    
    async def get_usage_stats(
        self,
        user_id: str,
        period_hours: int = 24
    ) -> UsageStats:
        """
        Get usage statistics for a user
        """
        if user_id not in self.usage:
            return UsageStats(
                user_id=user_id,
                total_tokens=0,
                input_tokens=0,
                output_tokens=0,
                request_count=0,
                cost_estimate=0.0,
                period_start=datetime.utcnow() - timedelta(hours=period_hours),
                period_end=datetime.utcnow()
            )
        
        user_usage = self.usage[user_id]
        total = user_usage["day"]["tokens"]
        
        # Rough cost estimate ($0.0001 per 1K tokens)
        cost = (total / 1000) * 0.0001
        
        return UsageStats(
            user_id=user_id,
            total_tokens=total,
            input_tokens=int(total * 0.6),  # Estimate
            output_tokens=int(total * 0.4),  # Estimate
            request_count=0,
            cost_estimate=cost,
            period_start=datetime.utcnow() - timedelta(hours=period_hours),
            period_end=datetime.utcnow()
        )
    
    async def reset_quota(self, user_id: str, period: str = "all") -> None:
        """
        Reset quota for a user
        """
        if user_id not in self.usage:
            return
        
        user_usage = self.usage[user_id]
        
        if period == "all":
            for p in ["minute", "hour", "day"]:
                user_usage[p]["tokens"] = 0
        elif period in user_usage:
            user_usage[period]["tokens"] = 0
        
        logger.info(f"Reset {period} quota for user {user_id}")
    
    def update_limits(self, new_limits: Dict[str, int]) -> None:
        """
        Update token limits
        """
        self.limits.update(new_limits)
        logger.info(f"Updated token limits: {self.limits}")
    
    def get_limits(self) -> Dict[str, int]:
        """Get current token limits"""
        return self.limits.copy()


# Global instance
_token_manager: Optional[TokenManager] = None


def get_token_manager() -> TokenManager:
    """Get or create global TokenManager instance"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
