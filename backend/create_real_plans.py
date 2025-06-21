#!/usr/bin/env python3

"""
Script to create the real payment plans that match pricing.html
"""

import json
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, PaymentPlan

def create_real_plans():
    """Create the real payment plans matching pricing.html"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Clear existing plans first
        db.query(PaymentPlan).delete()
        db.commit()
        print("Cleared existing plans")
        
        # Define real plans matching pricing.html
        plans = [
            {
                "name": "Pro Plan",
                "description": "Unlock unlimited access to all features",
                "price": 99.0,
                "duration_days": 90,  # 3 months as mentioned in pricing
                "features": json.dumps([
                    "Unlimited PYQs - All previous year questions",
                    "Unlimited Mock Tests - Detailed analytics",
                    "Unlimited Reel Scrolls - All learning content",
                    "Advanced AI Chat - 24/7 question support",
                    "Weak Areas Detection - Identify improvement areas",
                    "AI Explanations - Detailed answer explanations",
                    "No ads - Clean experience",
                    "Priority support"
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
        print(f"Successfully created {len(plans)} payment plan!")
        
        # Display created plans
        created_plans = db.query(PaymentPlan).all()
        print("\nCreated Plans:")
        for plan in created_plans:
            print(f"- {plan.name}: ₹{plan.price} for {plan.duration_days} days")
            print(f"  Features: {json.loads(plan.features)}")
            
    except Exception as e:
        print(f"Error creating plans: {str(e)}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating real payment plans...")
    create_real_plans()
    print("Done!") 