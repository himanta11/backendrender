from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from . import models
from . import schemas
from .database import SessionLocal, engine, Base
from .auth import create_access_token, get_current_user, router as auth_router
from datetime import datetime, timedelta
import logging
import traceback
from fastapi.responses import JSONResponse, StreamingResponse
from .questions import router as questions_router, QuestionFilters
from fastapi.routing import APIRouter
from pydantic import BaseModel
import os
import json
from sqlalchemy import text
import requests
from together import Together
from dotenv import load_dotenv
import time
from .payment_service import payment_service
from .models import PaymentPlan, Payment, UserSubscription, UsageType
from .utils import UserLimitService
from .intent_detection import intent_detector, IntentType

# Initialize FastAPI app with CORS configuration
app = FastAPI(
    title="Aspirant Backend",
    description="Backend service for Aspirant application",
    version="1.0.0"
)

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://newfrontend-sage.vercel.app",    # Production frontend
        "https://aspirant-app.onrender.com",      # Render backend domain
        "https://*.onrender.com",                 # Any Render subdomain
        "http://localhost:5500",                  # Local development
        "http://127.0.0.1:5500",                  # Local development
        "http://localhost:8000",                  # Local backend
        "http://127.0.0.1:8000"                   # Local backend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(questions_router, prefix="/questions", tags=["questions"])

# Add startup event
@app.on_event("startup")
async def startup_event():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Application started and database initialized")

# Load environment variables
load_dotenv()

# Initialize Together AI client with hardcoded API key
TOGETHER_API_KEY = "39b58efc9f06bc95aeb6a246badf5561100d6247136a4cd33bc6f2c96cc9d6bf"
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"
TOGETHER_CHAT_URL = "https://api.together.xyz/v1/chat/completions"
together_client = Together(api_key=TOGETHER_API_KEY)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chat request/response models
class Message(BaseModel):
    role: str
    content: str

class FormatRequest(BaseModel):
    type: str
    style: str
    structured: bool = True

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    history: Optional[List[Message]] = None
    questionType: Optional[str] = None
    complexity: Optional[str] = None
    format: Optional[FormatRequest] = None

class ChatResponse(BaseModel):
    response: str
    chat_id: str

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    logger.error(traceback.format_exc())

# Models

class QuestionExplanationRequest(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None

class QuestionExplanationResponse(BaseModel):
    response: str
    chat_id: str

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/signup", response_model=schemas.Token)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to create user with email: {user.email}")
        
        # Validate email format
        if not user.email or '@' not in user.email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Validate password length
        if not user.password or len(user.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        # Validate username length
        if not user.username or len(user.username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
        
        # Check if email exists
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            logger.warning(f"Email {user.email} already exists")
            raise HTTPException(status_code=400, detail="Email already registered")
            
        # Check if username exists
        if user.username:
            db_user = db.query(models.User).filter(models.User.username == user.username).first()
            if db_user:
                logger.warning(f"Username {user.username} already exists")
                raise HTTPException(status_code=400, detail="Username already taken")
        
        # Create new user
        try:
            new_user = models.User(
                email=user.email,
                username=user.username
            )
            new_user.set_password(user.password)
            logger.info("User object created successfully")
            
            # Add to database
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info("User added to database successfully")
            
            # Create access token
            access_token = create_access_token(data={"sub": user.email})
            logger.info("Access token created successfully")
            return {"access_token": access_token, "token_type": "bearer"}
            
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # Try to find user by email first
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        if not user or not user.verify_password(form_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/me")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}

# Questions endpoint functionality is now handled by questions_router

# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Chat with AI with usage limits and intent detection"""
    try:
        logger.info(f"Chat request received from user {current_user.id}")
        
        # Detect intent first
        intent, confidence = intent_detector.detect_intent(request.message)
        logger.info(f"Detected intent: {intent.value} with confidence: {confidence}")
        
        # Check if we should use a predefined response
        if not intent_detector.should_use_ai(intent):
            # Use predefined response for simple intents
            response_text = intent_detector.get_response(intent, request.message)
            chat_id = request.chat_id or str(datetime.now().timestamp())
            
            return JSONResponse(
                content=ChatResponse(
                    response=response_text,
                    chat_id=chat_id
                ).dict(),
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                    "Access-Control-Allow-Credentials": "true",
                    "Content-Type": "application/json"
                }
            )
        
        # For educational and general questions, check usage limits
        try:
            limit_check = UserLimitService.check_usage_limit(db, current_user.id, UsageType.AI_CHAT)
            logger.info(f"Limit check result: {limit_check}")
            if not limit_check["allowed"]:
                raise HTTPException(status_code=429, detail=limit_check["message"])
        except Exception as e:
            logger.error(f"Error checking usage limits: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error checking usage limits: {str(e)}")
        
        # Record AI chat usage
        try:
            UserLimitService.record_usage(db, current_user.id, UsageType.AI_CHAT)
            logger.info("Usage recorded successfully")
        except Exception as e:
            logger.error(f"Error recording usage: {str(e)}")
            logger.error(traceback.format_exc())
            # Continue anyway, don't fail the request for usage recording
        
        logger.info(f"Received chat request: {request.dict()}")
        
        # Initialize chat history if not provided
        chat_id = request.chat_id or str(datetime.now().timestamp())
        history = request.history or []

        # Define headers for Together AI API
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Get question analysis from frontend
        question_type = request.questionType or "explanation"
        complexity = request.complexity or "simple"
        format_style = request.format.style if request.format else "natural"
        
        # Create dynamic system message based on intent and question type
        def get_system_message(q_type, comp, detected_intent):
            # Get intent-specific context
            intent_context = intent_detector.get_ai_prompt_context(detected_intent, request.message)
            
            base_system = f"""You are an expert AI tutor specializing in educational content. {intent_context} Always respond in well-formatted markdown when appropriate."""
            
            if q_type == "definition":
                return f"""{base_system}
                
For definition questions:
- Start with a clear, concise definition
- Provide 2-3 key characteristics
- Include practical examples
- Use markdown formatting with headers and bullet points
- Keep it {'detailed' if comp == 'complex' else 'concise'}"""
                
            elif q_type == "explanation":
                return f"""{base_system}
                
For explanation questions:
- Use clear markdown headers (# ## ###)
- Break down complex concepts into digestible sections
- Use bullet points and numbered lists appropriately
- Include examples and analogies
- {'Provide comprehensive coverage with multiple sections' if comp == 'complex' else 'Keep explanations focused and direct'}"""
                
            elif q_type == "steps":
                return f"""{base_system}
                
For step-by-step questions:
- Use numbered lists (1. 2. 3.)
- Create clear section headers
- Provide detailed instructions for each step
- Include tips or notes where helpful
- Format with proper markdown structure"""
                
            elif q_type == "list":
                return f"""{base_system}
                
For list-based questions:
- Use bullet points or numbered lists as appropriate
- Group related items under subheadings
- Provide brief explanations for each item
- Use markdown formatting for clarity"""
                
            elif q_type == "comparison":
                return f"""{base_system}
                
For comparison questions:
- Use markdown tables when appropriate
- Create clear sections for each item being compared
- Highlight key differences and similarities
- Use headers to organize the comparison"""
                
            else:  # default/shortAnswer
                return f"""{base_system}
                
Provide clear, well-structured responses using appropriate markdown formatting including headers, lists, and emphasis where helpful."""

        # Build the conversation messages
        messages = [
            {
                "role": "system",
                "content": get_system_message(question_type, complexity, intent)
            }
        ]
        
        # Add conversation history
        for msg in history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg.role if msg.role in ["user", "assistant"] else "user",
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": request.message
        })

        # Use chat completion endpoint with proper parameters
        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }

        logger.info("Making request to Together AI...")
        logger.info(f"Payload: {payload}")
        logger.info(f"Question type: {question_type}, Complexity: {complexity}, Intent: {intent.value}")

        # Make request to Together AI
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    TOGETHER_CHAT_URL, 
                    headers=headers, 
                    json=payload, 
                    timeout=30
                )
                
                if response.ok:
                    ai_response = response.json()
                    logger.info(f"Received response from Together AI: {ai_response}")
                    
                    if "choices" not in ai_response or not ai_response["choices"]:
                        error_msg = "Invalid response format from Together AI"
                        logger.error(error_msg)
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying... Attempt {attempt + 2} of {max_retries}")
                            time.sleep(retry_delay)
                            continue
                        return JSONResponse(
                            status_code=500,
                            content={"detail": error_msg},
                            headers={
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                                "Access-Control-Allow-Credentials": "true",
                                "Content-Type": "application/json"
                            }
                        )
                    
                    # Extract message content from chat completion response
                    choice = ai_response["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        ai_message = choice["message"]["content"].strip()
                    elif "text" in choice:
                        ai_message = choice["text"].strip()
                    else:
                        error_msg = "No content found in AI response"
                        logger.error(f"{error_msg}: {ai_response}")
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying... Attempt {attempt + 2} of {max_retries}")
                            time.sleep(retry_delay)
                            continue
                        ai_message = "I apologize, but I'm having trouble generating a response right now. Please try again."
                    
                    return JSONResponse(
                        content=ChatResponse(
                            response=ai_message,
                            chat_id=chat_id
                        ).dict(),
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                            "Access-Control-Allow-Credentials": "true",
                            "Content-Type": "application/json"
                        }
                    )
                else:
                    error_msg = f"Together AI API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    # Check if we should retry based on status code
                    if response.status_code in [429, 500, 502, 503, 504] and attempt < max_retries - 1:
                        logger.info(f"Retrying... Attempt {attempt + 2} of {max_retries}")
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                    
                    return JSONResponse(
                        status_code=500,
                        content={"detail": error_msg},
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                            "Access-Control-Allow-Credentials": "true",
                            "Content-Type": "application/json"
                        }
                    )
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                logger.error(error_msg)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying... Attempt {attempt + 2} of {max_retries}")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                return JSONResponse(
                    status_code=500,
                    content={"detail": error_msg},
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                        "Access-Control-Allow-Credentials": "true",
                        "Content-Type": "application/json"
                    }
                )
        
        # If we get here, all retries failed
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to get response from AI after multiple attempts"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                "Access-Control-Allow-Credentials": "true",
                "Content-Type": "application/json"
            }
        )
            
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": error_msg},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                "Access-Control-Allow-Credentials": "true",
                "Content-Type": "application/json"
            }
        )

# Payment Models
class CreateOrderRequest(BaseModel):
    plan_id: int
    
class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    payment_method: Optional[str] = None

# Payment Endpoints
@app.get("/payment/plans")
async def get_payment_plans(db: Session = Depends(get_db)):
    """Get all available payment plans"""
    try:
        plans = payment_service.get_payment_plans(db)
        return {"plans": plans}
    except Exception as e:
        logger.error(f"Error fetching payment plans: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payment/create-order")
async def create_payment_order(
    request: CreateOrderRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Razorpay order"""
    try:
        # Get the payment plan
        plan = db.query(PaymentPlan).filter(PaymentPlan.id == request.plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Payment plan not found")
        
        # Create Razorpay order
        order = payment_service.create_order(amount=plan.price)
        
        # Create payment record in database
        payment = payment_service.create_payment_record(
            db=db,
            user_id=current_user.id,
            plan_id=plan.id,
            razorpay_order_id=order['id'],
            amount=plan.price,
            receipt=order['receipt']
        )
        
        return {
            "order_id": order['id'],
            "amount": order['amount'],
            "currency": order['currency'],
            "key": payment_service.client.auth[0],  # Razorpay key ID
            "plan": {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "price": plan.price,
                "duration_days": plan.duration_days
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating payment order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payment/verify")
async def verify_payment(
    request: PaymentVerificationRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify payment and update subscription"""
    try:
        # Verify payment signature
        is_valid = payment_service.verify_payment_signature(
            request.razorpay_order_id,
            request.razorpay_payment_id,
            request.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Update payment record
        payment = payment_service.update_payment_success(
            db=db,
            razorpay_order_id=request.razorpay_order_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_signature=request.razorpay_signature,
            payment_method=request.payment_method
        )
        
        return {
            "success": True,
            "message": "Payment verified successfully",
            "payment_id": payment.id
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payment/subscription")
async def get_user_subscription(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current subscription"""
    try:
        subscription = payment_service.get_user_subscription(db, current_user.id)
        if not subscription:
            return {"subscription": None}
        
        return {
            "subscription": {
                "id": subscription.id,
                "plan_name": subscription.plan.name,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "is_active": subscription.is_active,
                "days_remaining": (subscription.end_date - datetime.now()).days
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching user subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# User Limits API
@app.get("/user/limits")
async def get_user_limits(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current usage limits and status"""
    try:
        limits_status = UserLimitService.get_user_limits_status(db, current_user.id)
        return {"limits": limits_status}
    except Exception as e:
        logger.error(f"Error fetching user limits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/check-limit/{usage_type}")
async def check_usage_limit(
    usage_type: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user can perform a specific action"""
    try:
        # Convert string to enum
        usage_enum = UsageType(usage_type.upper())
        limit_check = UserLimitService.check_usage_limit(db, current_user.id, usage_enum)
        return limit_check
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid usage type")
    except Exception as e:
        logger.error(f"Error checking usage limit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/record-usage/{usage_type}")
async def record_usage(
    usage_type: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record user's usage of a feature"""
    try:
        # Convert string to enum
        usage_enum = UsageType(usage_type.upper())
        
        # First check if user can use this feature
        limit_check = UserLimitService.check_usage_limit(db, current_user.id, usage_enum)
        if not limit_check["allowed"]:
            return {"success": False, "message": limit_check["message"]}
        
        # Record the usage
        success = UserLimitService.record_usage(db, current_user.id, usage_enum)
        if success:
            return {"success": True, "message": "Usage recorded successfully"}
        else:
            return {"success": False, "message": "Failed to record usage"}
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid usage type")
    except Exception as e:
        logger.error(f"Error recording usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Event handler for startup
@app.on_event("startup")
def on_startup():
    logger.info("Application startup complete")

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Check database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)