from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import logging
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

try:
    # Try to get DATABASE_URL from environment variable (for Render)
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        # Fallback to hardcoded PostgreSQL URL
        DATABASE_URL = "postgresql://postgres:VkIEJUdPvuxmATvoicDaEFZmTxhBIBiW@shuttle.proxy.rlwy.net:25171/railway"
    
    logger.info("Attempting to connect to PostgreSQL...")
    
    engine = create_engine(DATABASE_URL)
    # Test the connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Successfully connected to PostgreSQL")

except Exception as e:
    logger.warning(f"PostgreSQL connection failed: {str(e)}")
    logger.info("Falling back to SQLite database")
    
    # Use SQLite as fallback
    DATABASE_URL = "sqlite:///./aspirant.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    logger.info("Using SQLite database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("Session maker configured")

Base = declarative_base()
logger.info("Base class created")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error in database session: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def modify_username_column():
    """Make username column nullable"""
    try:
        with engine.connect() as conn:
            # Check if username column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'username'
            """))
            if result.fetchone():
                # Make username column nullable
                conn.execute(text("""
                    ALTER TABLE users 
                    ALTER COLUMN username DROP NOT NULL
                """))
                logger.info("Made username column nullable")
            conn.commit()
    except Exception as e:
        logger.error(f"Error modifying username column: {str(e)}")
        raise

def add_timestamp_columns():
    """Safely add timestamp columns if they don't exist"""
    try:
        with engine.connect() as conn:
            # Check if created_at exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'created_at'
            """))
            if not result.fetchone():
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                """))
                logger.info("Added created_at column")

            # Check if updated_at exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'updated_at'
            """))
            if not result.fetchone():
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                """))
                logger.info("Added updated_at column")

            conn.commit()
    except Exception as e:
        logger.error(f"Error adding timestamp columns: {str(e)}")
        raise

# Make username column nullable
try:
    modify_username_column()
except Exception as e:
    logger.error(f"Error in modify_username_column: {str(e)}")

# Add timestamp columns if they don't exist
try:
    add_timestamp_columns()
except Exception as e:
    logger.error(f"Error in add_timestamp_columns: {str(e)}")
