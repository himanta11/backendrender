#!/usr/bin/env python3

from database import engine, SessionLocal
from models import Base, User, UserTier, UserUsage, UsageType
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Set up database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Test database connection
        db = SessionLocal()
        try:
            # Test a simple query
            result = db.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            
            # Check if tables exist
            tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            table_names = [row[0] for row in tables.fetchall()]
            logger.info(f"Available tables: {table_names}")
            
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database() 