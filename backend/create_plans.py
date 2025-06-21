#!/usr/bin/env python3

"""
Script to create default payment plans in the database
Run this script to populate the database with sample plans for testing
"""

import json
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, PaymentPlan

def create_default_plans():
    """Create default payment plans"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if plans already exist
        existing_plans = db.query(PaymentPlan).count()
        if existing_plans > 0:
            print(f"Found {existing_plans} existing plans. Skipping creation.")
            return
        
        # Define default plans
        plans = [
            {
                "name": "Basic Plan",
                "description": "Perfect for beginners starting their preparation journey",
                "price": 499.0,
                "duration_days": 30,
                "features": json.dumps([
                    "Access to mock tests",
                    "Basic question bank (1000+ questions)",
                    "Performance analytics",
                    "Email support",
                    "Study progress tracking"
                ]),
                "is_active": True
            },
            {
                "name": "Premium Plan",
                "description": "Most popular choice for serious aspirants",
                "price": 1299.0,
                "duration_days": 90,
                "features": json.dumps([
                    "Everything in Basic Plan",
                    "AI-powered doubt clearing",
                    "Previous year questions (5000+)",
                    "Priority support",
                    "Study plan recommendations",
                    "Detailed performance insights",
                    "Mobile app access"
                ]),
                "is_active": True
            },
            {
                "name": "Pro Plan",
                "description": "Complete package for exam success",
                "price": 2499.0,
                "duration_days": 180,
                "features": json.dumps([
                    "Everything in Premium Plan",
                    "Live classes access",
                    "1-on-1 mentoring sessions",
                    "Exclusive study materials",
                    "Interview preparation",
                    "Custom study schedules",
                    "Expert guidance",
                    "Unlimited practice tests"
                ]),
                "is_active": True
            }
        ]
        
        # Create plans
        for plan_data in plans:
            plan = PaymentPlan(**plan_data)
            db.add(plan)
        
        # Commit changes
        db.commit()
        print(f"Successfully created {len(plans)} payment plans!")
        
        # Display created plans
        created_plans = db.query(PaymentPlan).all()
        print("\nCreated Plans:")
        for plan in created_plans:
            print(f"- {plan.name}: ₹{plan.price} for {plan.duration_days} days")
            
    except Exception as e:
        print(f"Error creating plans: {str(e)}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating default payment plans...")
    create_default_plans()
    print("Done!") 