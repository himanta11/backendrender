from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from .database import SessionLocal
from .models import User
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request models
class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str

# Create router
router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days (7 * 24 * 60 = 10080 minutes)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    # Try to find user by email first
    user = db.query(User).filter(User.email == username).first()
    if not user:
        # If not found by email, try username
        user = db.query(User).filter(User.username == username).first()
    
    if not user:
        logger.info(f"User not found: {username}")
        return False
    
    if not verify_password(password, user.hashed_password):
        logger.info(f"Invalid password for user: {username}")
        return False
    
    logger.info(f"User authenticated successfully: {username}")
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Try to find user by email first, then by username
    user = db.query(User).filter(User.email == username).first()
    if not user:
        user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
    return user

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Use email for token generation
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"Login successful for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint that matches the frontend expectation"""
    logger.info(f"Login attempt for user: {form_data.username}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Use email for token generation
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"Login successful for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup")
async def signup_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for username: {username}, email: {email}")
    
    # Check if email already exists
    if db.query(User).filter(User.email == email).first():
        logger.warning(f"Email already registered: {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == username).first():
        logger.warning(f"Username already taken: {username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created successfully: {username}")
        
        # Generate token for automatic login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "message": "User created successfully"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/register")
async def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register endpoint that matches the frontend expectation"""
    logger.info(f"Register attempt for username: {user_data.username}, email: {user_data.email}")
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        logger.warning(f"Email already registered: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        logger.warning(f"Username already taken: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created successfully: {user_data.username}")
        
        # Generate token for automatic login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "message": "User created successfully"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh token endpoint - creates a new token for the current user"""
    logger.info(f"Token refresh for user: {current_user.email}")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    logger.info(f"Token refreshed successfully for user: {current_user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email
    }