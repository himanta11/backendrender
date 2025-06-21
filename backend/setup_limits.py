#!/usr/bin/env python3

"""
Setup script to initialize user limits and tiers for free user restrictions
Run this script after adding the new models to create the necessary database tables
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, UserTier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_user_limits():
    """Setup user limits and ensure all existing users have tier records"""
    
    # Create all tables (including new ones)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/updated successfully")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get all existing users without tier records
        users_without_tiers = db.query(User).filter(
            ~User.id.in_(db.query(UserTier.user_id))
        ).all()
        
        logger.info(f"Found {len(users_without_tiers)} users without tier records")
        
        # Create tier records for existing users
        for user in users_without_tiers:
            tier_record = UserTier(
                user_id=user.id,
                tier="FREE",  # Default to free tier
                daily_pyq_limit=10,
                weekly_mock_limit=1,
                daily_reel_limit=10,
                ai_chat_limit=5
            )
            db.add(tier_record)
            logger.info(f"Created tier record for user {user.email}")
        
        # Commit changes
        if users_without_tiers:
            db.commit()
            logger.info(f"Successfully created {len(users_without_tiers)} tier records")
        else:
            logger.info("All users already have tier records")
            
    except Exception as e:
        logger.error(f"Error setting up user limits: {str(e)}")
        db.rollback()
        raise
        
    finally:
        db.close()

if __name__ == "__main__":
    setup_user_limits()
    print("User limits setup completed!") 