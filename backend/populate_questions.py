#!/usr/bin/env python3
"""
Script to populate the questions table with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from models import Base, Question, ExamType, ExamStage, Subject, DifficultyLevel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_questions():
    """Create sample questions for testing"""
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if questions already exist
        existing_count = db.query(Question).count()
        if existing_count > 0:
            logger.info(f"Database already has {existing_count} questions. Skipping population.")
            return
        
        sample_questions = [
            {
                "question_text": "The Make In India Logo is made up of what?",
                "option_a": "Lion made of Cogs",
                "option_b": "Eagle Made of Steel",
                "option_c": "Chakra Made of Cotton",
                "option_d": "Tiger Made of Khadi",
                "correct_answer": "A",
                "explanation": "The Make in India logo features a lion made of cogs, symbolizing strength and manufacturing.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.GENERAL_AWARENESS,
                "topic": "Government Schemes",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "Practice Set"
            },
            {
                "question_text": "Find the missing number in the series: 2, 6, 12, 20, 30, ?",
                "option_a": "40",
                "option_b": "42",
                "option_c": "44",
                "option_d": "46",
                "correct_answer": "B",
                "explanation": "The series follows the pattern n(n+1): 1×2=2, 2×3=6, 3×4=12, 4×5=20, 5×6=30, 6×7=42",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.MATHEMATICS,
                "topic": "Number Series",
                "difficulty_level": DifficultyLevel.MODERATE,
                "source": "Previous Year Paper"
            },
            {
                "question_text": "Who is known as the Father of Indian Constitution?",
                "option_a": "Mahatma Gandhi",
                "option_b": "Jawaharlal Nehru",
                "option_c": "Dr. B.R. Ambedkar",
                "option_d": "Sardar Vallabhbhai Patel",
                "correct_answer": "C",
                "explanation": "Dr. B.R. Ambedkar is known as the Father of the Indian Constitution for his role as the chairman of the drafting committee.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.POLITY,
                "topic": "Constitution",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "General Knowledge"
            },
            {
                "question_text": "What is the chemical formula of water?",
                "option_a": "H2O",
                "option_b": "CO2",
                "option_c": "NaCl",
                "option_d": "HCl",
                "correct_answer": "A",
                "explanation": "Water has the chemical formula H2O, consisting of two hydrogen atoms and one oxygen atom.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.SCIENCE,
                "topic": "Chemistry",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "Basic Science"
            },
            {
                "question_text": "If A = 1, B = 2, C = 3, then what is the value of CAB?",
                "option_a": "312",
                "option_b": "321",
                "option_c": "123",
                "option_d": "132",
                "correct_answer": "A",
                "explanation": "C=3, A=1, B=2, so CAB = 312",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.REASONING,
                "topic": "Coding-Decoding",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "Practice Set"
            },
            {
                "question_text": "Which planet is known as the Red Planet?",
                "option_a": "Venus",
                "option_b": "Mars",
                "option_c": "Jupiter",
                "option_d": "Saturn",
                "correct_answer": "B",
                "explanation": "Mars is known as the Red Planet due to its reddish appearance caused by iron oxide on its surface.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.GENERAL_SCIENCE,
                "topic": "Astronomy",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "General Knowledge"
            },
            {
                "question_text": "What is 15% of 200?",
                "option_a": "25",
                "option_b": "30",
                "option_c": "35",
                "option_d": "40",
                "correct_answer": "B",
                "explanation": "15% of 200 = (15/100) × 200 = 30",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.MATHEMATICS,
                "topic": "Percentage",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "Practice Set"
            },
            {
                "question_text": "Which is the longest river in India?",
                "option_a": "Yamuna",
                "option_b": "Ganga",
                "option_c": "Godavari",
                "option_d": "Krishna",
                "correct_answer": "B",
                "explanation": "The Ganga (Ganges) is the longest river in India, flowing for about 2,525 km.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.GEOGRAPHY,
                "topic": "Rivers",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "General Knowledge"
            },
            {
                "question_text": "Who was the first President of India?",
                "option_a": "Dr. A.P.J. Abdul Kalam",
                "option_b": "Dr. Rajendra Prasad",
                "option_c": "Dr. S. Radhakrishnan",
                "option_d": "Dr. Zakir Hussain",
                "correct_answer": "B",
                "explanation": "Dr. Rajendra Prasad was the first President of India, serving from 1950 to 1962.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.HISTORY,
                "topic": "Indian Independence",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "General Knowledge"
            },
            {
                "question_text": "What is the square root of 144?",
                "option_a": "10",
                "option_b": "11",
                "option_c": "12",
                "option_d": "13",
                "correct_answer": "C",
                "explanation": "The square root of 144 is 12, because 12 × 12 = 144.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.MATHEMATICS,
                "topic": "Square Roots",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "Basic Mathematics"
            },
            {
                "question_text": "Which gas is most abundant in Earth's atmosphere?",
                "option_a": "Oxygen",
                "option_b": "Carbon Dioxide",
                "option_c": "Nitrogen",
                "option_d": "Argon",
                "correct_answer": "C",
                "explanation": "Nitrogen makes up about 78% of Earth's atmosphere, making it the most abundant gas.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.SCIENCE,
                "topic": "Atmosphere",
                "difficulty_level": DifficultyLevel.MODERATE,
                "source": "Environmental Science"
            },
            {
                "question_text": "Find the odd one out: Apple, Banana, Carrot, Orange",
                "option_a": "Apple",
                "option_b": "Banana",
                "option_c": "Carrot",
                "option_d": "Orange",
                "correct_answer": "C",
                "explanation": "Carrot is a vegetable, while Apple, Banana, and Orange are fruits.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.REASONING,
                "topic": "Classification",
                "difficulty_level": DifficultyLevel.EASY,
                "source": "Logical Reasoning"
            },
            {
                "question_text": "What is the capital of Australia?",
                "option_a": "Sydney",
                "option_b": "Melbourne",
                "option_c": "Canberra",
                "option_d": "Brisbane",
                "correct_answer": "C",
                "explanation": "Canberra is the capital city of Australia, not Sydney or Melbourne as commonly thought.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.GEOGRAPHY,
                "topic": "World Capitals",
                "difficulty_level": DifficultyLevel.MODERATE,
                "source": "World Geography"
            },
            {
                "question_text": "Which element has the chemical symbol 'Fe'?",
                "option_a": "Fluorine",
                "option_b": "Iron",
                "option_c": "Francium",
                "option_d": "Fermium",
                "correct_answer": "B",
                "explanation": "Fe is the chemical symbol for Iron, derived from its Latin name 'ferrum'.",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.CHEMISTRY,
                "topic": "Chemical Symbols",
                "difficulty_level": DifficultyLevel.MODERATE,
                "source": "Chemistry Basics"
            },
            {
                "question_text": "If 5x + 3 = 18, what is the value of x?",
                "option_a": "2",
                "option_b": "3",
                "option_c": "4",
                "option_d": "5",
                "correct_answer": "B",
                "explanation": "5x + 3 = 18, so 5x = 15, therefore x = 3",
                "year": 2023,
                "exam_type": ExamType.NTPC,
                "exam_stage": ExamStage.CBT1,
                "subject": Subject.MATHEMATICS,
                "topic": "Linear Equations",
                "difficulty_level": DifficultyLevel.MODERATE,
                "source": "Algebra"
            }
        ]
        
        # Add questions to database
        for q_data in sample_questions:
            question = Question(**q_data)
            db.add(question)
        
        db.commit()
        logger.info(f"Successfully added {len(sample_questions)} sample questions to the database")
        
    except Exception as e:
        logger.error(f"Error populating questions: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_questions()
    print("Sample questions populated successfully!") 