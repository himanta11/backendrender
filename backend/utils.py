from passlib.context import CryptContext
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from .models import UserSubscription, UserTier, UserUsage, UsageType
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class UserLimitService:
    """Service to manage user subscription tiers and usage limits"""
    
    @staticmethod
    def get_user_tier(db: Session, user_id: int) -> str:
        """Get user's current tier (FREE or PRO)"""
        try:
            # Check if user has active subscription
            subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.is_active == True,
                UserSubscription.end_date > datetime.utcnow()
            ).first()
            
            if subscription:
                return "PRO"
            else:
                return "FREE"
        except Exception as e:
            logger.error(f"Error getting user tier: {str(e)}")
            return "FREE"
    
    @staticmethod
    def ensure_user_tier_exists(db: Session, user_id: int) -> None:
        """Ensure user has a tier record, create if doesn't exist"""
        try:
            tier_record = db.query(UserTier).filter(UserTier.user_id == user_id).first()
            if not tier_record:
                current_tier = UserLimitService.get_user_tier(db, user_id)
                tier_record = UserTier(
                    user_id=user_id,
                    tier=current_tier,
                    daily_pyq_limit=10 if current_tier == "FREE" else -1,  # -1 means unlimited
                    weekly_mock_limit=1 if current_tier == "FREE" else -1,
                    daily_reel_limit=10 if current_tier == "FREE" else -1,
                    ai_chat_limit=5 if current_tier == "FREE" else -1
                )
                db.add(tier_record)
                db.commit()
        except Exception as e:
            logger.error(f"Error ensuring user tier exists: {str(e)}")
            db.rollback()
    
    @staticmethod
    def get_daily_usage(db: Session, user_id: int, usage_type: UsageType) -> int:
        """Get user's usage count for today"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            usage = db.query(UserUsage).filter(
                UserUsage.user_id == user_id,
                UserUsage.usage_type == usage_type,
                UserUsage.usage_date == today
            ).first()
            return usage.count if usage else 0
        except Exception as e:
            logger.error(f"Error getting daily usage: {str(e)}")
            return 0
    
    @staticmethod
    def get_weekly_usage(db: Session, user_id: int, usage_type: UsageType) -> int:
        """Get user's usage count for this week (for mock tests)"""
        try:
            # Get start of week (Monday)
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            
            total_count = 0
            for i in range(7):  # Check each day of the week
                check_date = (start_of_week + timedelta(days=i)).strftime('%Y-%m-%d')
                usage = db.query(UserUsage).filter(
                    UserUsage.user_id == user_id,
                    UserUsage.usage_type == usage_type,
                    UserUsage.usage_date == check_date
                ).first()
                if usage:
                    total_count += usage.count
                    
            return total_count
        except Exception as e:
            logger.error(f"Error getting weekly usage: {str(e)}")
            return 0
    
    @staticmethod
    def check_usage_limit(db: Session, user_id: int, usage_type: UsageType) -> Dict[str, Any]:
        """Check if user can perform an action based on their tier and usage"""
        try:
            UserLimitService.ensure_user_tier_exists(db, user_id)
            
            user_tier = UserLimitService.get_user_tier(db, user_id)
            tier_record = db.query(UserTier).filter(UserTier.user_id == user_id).first()
            
            if user_tier == "PRO":
                return {"allowed": True, "message": "Unlimited access", "remaining": -1}
            
            # Check free tier limits
            if usage_type == UsageType.PYQ:
                daily_usage = UserLimitService.get_daily_usage(db, user_id, usage_type)
                limit = tier_record.daily_pyq_limit
                if daily_usage >= limit:
                    return {"allowed": False, "message": f"Daily PYQ limit reached ({limit}/day). Upgrade to Pro for unlimited access!", "remaining": 0}
                return {"allowed": True, "message": "Access granted", "remaining": limit - daily_usage}
            
            elif usage_type == UsageType.MOCK_TEST:
                weekly_usage = UserLimitService.get_weekly_usage(db, user_id, usage_type)
                limit = tier_record.weekly_mock_limit
                if weekly_usage >= limit:
                    return {"allowed": False, "message": f"Weekly mock test limit reached ({limit}/week). Upgrade to Pro for unlimited access!", "remaining": 0}
                return {"allowed": True, "message": "Access granted", "remaining": limit - weekly_usage}
            
            elif usage_type == UsageType.REEL_SCROLL:
                daily_usage = UserLimitService.get_daily_usage(db, user_id, usage_type)
                limit = tier_record.daily_reel_limit
                if daily_usage >= limit:
                    return {"allowed": False, "message": f"Daily reel limit reached ({limit}/day). Upgrade to Pro for unlimited access!", "remaining": 0}
                return {"allowed": True, "message": "Access granted", "remaining": limit - daily_usage}
            
            elif usage_type == UsageType.AI_CHAT:
                daily_usage = UserLimitService.get_daily_usage(db, user_id, usage_type)
                limit = tier_record.ai_chat_limit
                if daily_usage >= limit:
                    return {"allowed": False, "message": f"Daily AI chat limit reached ({limit}/day). Upgrade to Pro for unlimited access!", "remaining": 0}
                return {"allowed": True, "message": "Access granted", "remaining": limit - daily_usage}
            
            return {"allowed": False, "message": "Unknown usage type", "remaining": 0}
            
        except Exception as e:
            logger.error(f"Error checking usage limit: {str(e)}")
            return {"allowed": False, "message": "Error checking limits", "remaining": 0}
    
    @staticmethod
    def record_usage(db: Session, user_id: int, usage_type: UsageType) -> bool:
        """Record user's usage"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            
            # Check if usage record exists for today
            usage = db.query(UserUsage).filter(
                UserUsage.user_id == user_id,
                UserUsage.usage_type == usage_type,
                UserUsage.usage_date == today
            ).first()
            
            if usage:
                usage.count += 1
                usage.updated_at = datetime.utcnow()
            else:
                usage = UserUsage(
                    user_id=user_id,
                    usage_type=usage_type,
                    usage_date=today,
                    count=1
                )
                db.add(usage)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error recording usage: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def get_user_limits_status(db: Session, user_id: int) -> Dict[str, Any]:
        """Get comprehensive status of user's limits"""
        try:
            user_tier = UserLimitService.get_user_tier(db, user_id)
            
            if user_tier == "PRO":
                return {
                    "tier": "PRO",
                    "pyq": {"used": 0, "limit": -1, "remaining": -1},
                    "mock_tests": {"used": 0, "limit": -1, "remaining": -1},
                    "reels": {"used": 0, "limit": -1, "remaining": -1},
                    "ai_chat": {"used": 0, "limit": -1, "remaining": -1}
                }
            
            # Free tier status
            UserLimitService.ensure_user_tier_exists(db, user_id)
            tier_record = db.query(UserTier).filter(UserTier.user_id == user_id).first()
            
            pyq_used = UserLimitService.get_daily_usage(db, user_id, UsageType.PYQ)
            mock_used = UserLimitService.get_weekly_usage(db, user_id, UsageType.MOCK_TEST)
            reel_used = UserLimitService.get_daily_usage(db, user_id, UsageType.REEL_SCROLL)
            ai_used = UserLimitService.get_daily_usage(db, user_id, UsageType.AI_CHAT)
            
            return {
                "tier": "FREE",
                "pyq": {
                    "used": pyq_used,
                    "limit": tier_record.daily_pyq_limit,
                    "remaining": max(0, tier_record.daily_pyq_limit - pyq_used)
                },
                "mock_tests": {
                    "used": mock_used,
                    "limit": tier_record.weekly_mock_limit,
                    "remaining": max(0, tier_record.weekly_mock_limit - mock_used)
                },
                "reels": {
                    "used": reel_used,
                    "limit": tier_record.daily_reel_limit,
                    "remaining": max(0, tier_record.daily_reel_limit - reel_used)
                },
                "ai_chat": {
                    "used": ai_used,
                    "limit": tier_record.ai_chat_limit,
                    "remaining": max(0, tier_record.ai_chat_limit - ai_used)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user limits status: {str(e)}")
            return {"error": "Could not fetch limits status"}