import razorpay
import os
import uuid
import hashlib
import hmac
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Payment, PaymentPlan, UserSubscription, PaymentStatus, User
from .database import get_db
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_live_oecfzJZiQHiyVp")  # Live key
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "GtONJTIsxOGjHMQW4ilmWujx")  # Live secret key

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class PaymentService:
    def __init__(self):
        self.client = razorpay_client
    
    def create_order(self, amount: float, currency: str = "INR", receipt: str = None) -> Dict[str, Any]:
        """Create a Razorpay order"""
        try:
            if not receipt:
                receipt = f"receipt_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Amount should be in paisa (multiply by 100)
            amount_in_paisa = int(amount * 100)
            
            order_data = {
                "amount": amount_in_paisa,
                "currency": currency,
                "receipt": receipt,
                "payment_capture": 1  # Auto capture payment
            }
            
            order = self.client.order.create(data=order_data)
            logger.info(f"Razorpay order created: {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            raise Exception(f"Failed to create payment order: {str(e)}")
    
    def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """Verify Razorpay payment signature"""
        try:
            # Create the signature
            body = razorpay_order_id + "|" + razorpay_payment_id
            expected_signature = hmac.new(
                key=RAZORPAY_KEY_SECRET.encode('utf-8'),
                msg=body.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, razorpay_signature)
            
        except Exception as e:
            logger.error(f"Error verifying payment signature: {str(e)}")
            return False
    
    def create_payment_record(self, db: Session, user_id: int, plan_id: int, razorpay_order_id: str, amount: float, receipt: str) -> Payment:
        """Create a payment record in database"""
        try:
            payment = Payment(
                user_id=user_id,
                plan_id=plan_id,
                razorpay_order_id=razorpay_order_id,
                amount=amount,
                receipt_number=receipt,
                status=PaymentStatus.PENDING
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            logger.info(f"Payment record created: {payment.id}")
            return payment
            
        except Exception as e:
            logger.error(f"Error creating payment record: {str(e)}")
            db.rollback()
            raise Exception(f"Failed to create payment record: {str(e)}")
    
    def update_payment_success(self, db: Session, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str, payment_method: str = None) -> Payment:
        """Update payment record on successful payment"""
        try:
            payment = db.query(Payment).filter(Payment.razorpay_order_id == razorpay_order_id).first()
            if not payment:
                raise Exception("Payment record not found")
            
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = PaymentStatus.COMPLETED
            payment.payment_method = payment_method
            payment.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(payment)
            
            # Create user subscription
            self.create_user_subscription(db, payment)
            
            logger.info(f"Payment updated successfully: {payment.id}")
            return payment
            
        except Exception as e:
            logger.error(f"Error updating payment: {str(e)}")
            db.rollback()
            raise Exception(f"Failed to update payment: {str(e)}")
    
    def create_user_subscription(self, db: Session, payment: Payment) -> UserSubscription:
        """Create user subscription after successful payment"""
        try:
            plan = db.query(PaymentPlan).filter(PaymentPlan.id == payment.plan_id).first()
            if not plan:
                raise Exception("Payment plan not found")
            
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=plan.duration_days)
            
            subscription = UserSubscription(
                user_id=payment.user_id,
                plan_id=payment.plan_id,
                payment_id=payment.id,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            
            logger.info(f"User subscription created: {subscription.id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating user subscription: {str(e)}")
            db.rollback()
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    def get_payment_plans(self, db: Session):
        """Get all active payment plans"""
        return db.query(PaymentPlan).filter(PaymentPlan.is_active == True).all()
    
    def get_user_subscription(self, db: Session, user_id: int):
        """Get user's active subscription"""
        return db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True,
            UserSubscription.end_date > datetime.utcnow()
        ).first()

# Initialize payment service
payment_service = PaymentService() 