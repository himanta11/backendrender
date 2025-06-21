from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from .database import get_db, SessionLocal
from .models import Question, ExamType, ExamStage, Subject
from pydantic import BaseModel
import logging
import traceback
import requests

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["questions"])

# Together AI configuration
TOGETHER_API_KEY = "39b58efc9f06bc95aeb6a246badf5561100d6247136a4cd33bc6f2c96cc9d6bf"
TOGETHER_CHAT_URL = "https://api.together.xyz/v1/chat/completions"

class QuestionFilters(BaseModel):
    exam_type: Optional[str] = None
    topics: Optional[List[str]] = None
    has_diagram: Optional[bool] = None
    limit: Optional[int] = 50
    subject: Optional[str] = None
    year: Optional[int] = None
    exam_stage: Optional[str] = None

class QuestionResponse(BaseModel):
    id: int
    exam_type: str
    exam_stage: str
    subject: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None
    year: Optional[int] = None

    class Config:
        from_attributes = True

class QuestionExplanationRequest(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None

class QuestionExplanationResponse(BaseModel):
    response: str
    chat_id: str

@router.post("/")
async def get_questions(filters: QuestionFilters):
    try:
        logger.info(f"Received request with filters: {filters}")
        db = SessionLocal()
        
        # Check if questions table exists and has data
        try:
            result = db.execute(text("SELECT COUNT(*) FROM questions"))
            count = result.scalar()
            logger.info(f"Number of questions in database: {count}")
        except Exception as e:
            logger.error(f"Error checking questions table: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Database error: Questions table may not exist"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                    "Access-Control-Allow-Credentials": "true",
                    "Content-Type": "application/json"
                }
            )
        
        # Build the SQL query
        query = """
            SELECT id, question_text, option_a, option_b, option_c, option_d, 
                   correct_answer, explanation, topic, exam_type, has_diagram,
                   subject, year, exam_stage, difficulty_level
            FROM questions
            WHERE 1=1
        """
        params = {}
        
        if filters.exam_type:
            query += " AND exam_type = :exam_type"
            params['exam_type'] = filters.exam_type
        
        if filters.has_diagram is not None:
            query += " AND has_diagram = :has_diagram"
            params['has_diagram'] = filters.has_diagram
        
        if filters.topics:
            topic_conditions = []
            for i, topic in enumerate(filters.topics):
                param_name = f"topic_{i}"
                topic_conditions.append(f"topic = :{param_name}")
                params[param_name] = topic.replace('_', ' ').title()
            if topic_conditions:
                query += " AND (" + " OR ".join(topic_conditions) + ")"
        
        if filters.subject:
            query += " AND subject = :subject"
            params['subject'] = filters.subject
            
        if filters.year:
            query += " AND year = :year"
            params['year'] = filters.year
            
        if filters.exam_stage:
            query += " AND exam_stage = :exam_stage"
            params['exam_stage'] = filters.exam_stage
        
        # Add limit and randomize
        query += " ORDER BY RANDOM() LIMIT :limit"
        params['limit'] = filters.limit or 50
        
        logger.info(f"Executing query: {query}")
        logger.info(f"With parameters: {params}")
        
        try:
            result = db.execute(text(query), params)
            questions = result.fetchall()
            logger.info(f"Found {len(questions)} questions")
            
            # Convert to list of dicts
            questions_list = []
            for q in questions:
                question_dict = {
                    "id": q.id,
                    "question_text": q.question_text,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "topic": q.topic,
                    "exam_type": q.exam_type,
                    "has_diagram": q.has_diagram,
                    "subject": q.subject,
                    "year": q.year,
                    "exam_stage": q.exam_stage,
                    "difficulty_level": q.difficulty_level
                }
                questions_list.append(question_dict)
            
            return JSONResponse(
                content={"questions": questions_list},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                    "Access-Control-Allow-Credentials": "true",
                    "Content-Type": "application/json"
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"error": f"Error executing query: {str(e)}"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                    "Access-Control-Allow-Credentials": "true",
                    "Content-Type": "application/json"
                }
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in get_questions: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error: {str(e)}"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
                "Access-Control-Allow-Credentials": "true",
                "Content-Type": "application/json"
            }
        )
    finally:
        db.close()

@router.options("/")
async def options_questions():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
            "Access-Control-Allow-Credentials": "true",
            "Content-Type": "application/json"
        }
    )

@router.post("/explain")
async def explain_question(request: QuestionExplanationRequest):
    try:
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Format the prompt for the AI
        options_text = "\n".join([f"{chr(65 + i)}. {opt}" for i, opt in enumerate(request.options)])
        prompt = f"""Please explain this question in a friendly and simple way:

Question: {request.question}

Options:
{options_text}

Correct Answer: {request.correct_answer}

Current Explanation: {request.explanation or 'No explanation provided'}

Please provide:
1. A simple, easy-to-understand explanation of the concept
2. Break down the question in simple steps
3. Explain why the correct answer is right in a friendly way
4. Use emojis to make it engaging
5. End with an encouraging message and invite questions

Remember to:
- Use simple language
- Be friendly and encouraging
- Add relevant emojis
- Make it engaging and fun to read
- End with "Feel free to ask if you have any doubts! 😊"
"""
        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a friendly and encouraging AI tutor. Follow these rules strictly:
- Use simple, easy-to-understand language
- Be warm and friendly in your tone
- Use emojis to make explanations engaging
- Break down complex concepts into simple steps
- Encourage questions and interaction
- End with an invitation for follow-up questions
- If asked general questions, answer them in a friendly way
- Use markdown formatting for better readability
- Make learning fun and engaging
- If user says "thank you", respond warmly and encourage further interaction
- Be conversational and maintain a friendly chat
- Handle both academic and general questions
- Keep the conversation going naturally
- If user asks about other topics, engage in friendly conversation
- Remember previous context and maintain conversation flow"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(TOGETHER_CHAT_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        ai_response = response.json()
        logger.info(f"Together AI response: {ai_response}")
        
        if not ai_response.get("choices") or not ai_response["choices"][0].get("message"):
            logger.error(f"Unexpected Together AI response format: {ai_response}")
            raise HTTPException(
                status_code=500,
                detail="Invalid response from AI service"
            )
        
        explanation = ai_response["choices"][0]["message"]["content"]
        if not explanation or explanation.strip() == "😊":
            logger.error("Together AI returned empty or emoji-only response")
            explanation = f"""I apologize, but I'm having trouble generating an explanation right now. Here's what we know:

📝 Question: {request.question}

✅ Correct Answer: {request.correct_answer}

{request.explanation or "I'll try to provide a better explanation soon. Feel free to try again!"}

Feel free to ask if you have any questions! 😊"""
        
        chat_id = str(hash(request.question + str(request.options)))
        
        return QuestionExplanationResponse(
            response=explanation,
            chat_id=chat_id
        )
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {str(e)}"
        )

# Questions endpoint implementation complete 