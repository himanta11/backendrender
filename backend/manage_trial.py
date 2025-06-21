#!/usr/bin/env python3
"""
Simple management script for the free trial system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import User, UserTier, UserUsage, UserSubscription
from datetime import datetime, timedelta
import json

def show_menu():
    """Display the management menu"""
    print("\n" + "="*50)
    print("🎓 ASPIRANT.AI - Free Trial Management")
    print("="*50)
    print("1. Show all users and their tiers")
    print("2. Show user limits and usage")
    print("3. Upgrade user to PRO")
    print("4. Downgrade user to FREE")
    print("5. Setup free trial for new users")
    print("6. Reset all limits (testing)")
    print("7. Show usage statistics")
    print("8. Exit")
    print("="*50)

def show_all_users():
    """Display all users and their tiers"""
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        print(f"\n📊 Total Users: {len(users)}")
        print("-" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Tier':<8} {'Created':<12}")
        print("-" * 80)
        
        for user in users:
            tier = db.query(UserTier).filter(UserTier.user_id == user.id).first()
            tier_name = tier.tier if tier else "NONE"
            created = user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
            
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {tier_name:<8} {created:<12}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

def show_user_limits():
    """Show limits and usage for a specific user"""
    db = SessionLocal()
    
    try:
        email = input("Enter user email: ").strip()
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print("❌ User not found!")
            return
        
        tier = db.query(UserTier).filter(UserTier.user_id == user.id).first()
        
        if not tier:
            print("❌ User has no tier record!")
            return
        
        print(f"\n👤 User: {user.username} ({user.email})")
        print(f"🎯 Tier: {tier.tier}")
        print(f"📅 Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Show limits
        print(f"\n📋 Limits:")
        print(f"  • PYQs per day: {tier.daily_pyq_limit if tier.daily_pyq_limit != -1 else '∞'}")
        print(f"  • Mock tests per week: {tier.weekly_mock_limit if tier.weekly_mock_limit != -1 else '∞'}")
        print(f"  • Reel scrolls per day: {tier.daily_reel_limit if tier.daily_reel_limit != -1 else '∞'}")
        print(f"  • AI chat per day: {tier.ai_chat_limit if tier.ai_chat_limit != -1 else '∞'}")
        
        # Show today's usage
        today = datetime.now().strftime("%Y-%m-%d")
        usage = db.query(UserUsage).filter(
            UserUsage.user_id == user.id,
            UserUsage.usage_date == today
        ).all()
        
        if usage:
            print(f"\n📊 Today's Usage ({today}):")
            for u in usage:
                print(f"  • {u.usage_type}: {u.count}")
        else:
            print(f"\n📊 Today's Usage ({today}): No usage recorded")
        
        # Show subscription
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user.id,
            UserSubscription.is_active == True,
            UserSubscription.end_date > datetime.utcnow()
        ).first()
        
        if subscription:
            print(f"\n💳 Active Subscription:")
            print(f"  • Plan: {subscription.plan.name}")
            print(f"  • Ends: {subscription.end_date.strftime('%Y-%m-%d')}")
            print(f"  • Days remaining: {(subscription.end_date - datetime.utcnow()).days}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

def upgrade_user():
    """Upgrade a user to PRO tier"""
    db = SessionLocal()
    
    try:
        email = input("Enter user email: ").strip()
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print("❌ User not found!")
            return
        
        tier = db.query(UserTier).filter(UserTier.user_id == user.id).first()
        
        if tier:
            tier.tier = "PRO"
            tier.daily_pyq_limit = -1
            tier.weekly_mock_limit = -1
            tier.daily_reel_limit = -1
            tier.ai_chat_limit = -1
            tier.updated_at = datetime.utcnow()
        else:
            tier = UserTier(
                user_id=user.id,
                tier="PRO",
                daily_pyq_limit=-1,
                weekly_mock_limit=-1,
                daily_reel_limit=-1,
                ai_chat_limit=-1
            )
            db.add(tier)
        
        db.commit()
        print(f"✅ Successfully upgraded {user.username} to PRO tier!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def downgrade_user():
    """Downgrade a user to FREE tier"""
    db = SessionLocal()
    
    try:
        email = input("Enter user email: ").strip()
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print("❌ User not found!")
            return
        
        tier = db.query(UserTier).filter(UserTier.user_id == user.id).first()
        
        if tier:
            tier.tier = "FREE"
            tier.daily_pyq_limit = 10
            tier.weekly_mock_limit = 1
            tier.daily_reel_limit = 10
            tier.ai_chat_limit = 5
            tier.updated_at = datetime.utcnow()
        else:
            tier = UserTier(
                user_id=user.id,
                tier="FREE",
                daily_pyq_limit=10,
                weekly_mock_limit=1,
                daily_reel_limit=10,
                ai_chat_limit=5
            )
            db.add(tier)
        
        db.commit()
        print(f"✅ Successfully downgraded {user.username} to FREE tier!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def setup_free_trial():
    """Setup free trial for users without tier records"""
    db = SessionLocal()
    
    try:
        users_without_tier = db.query(User).outerjoin(UserTier).filter(UserTier.id.is_(None)).all()
        
        if not users_without_tier:
            print("✅ All users already have tier records!")
            return
        
        print(f"📝 Found {len(users_without_tier)} users without tier records")
        
        for user in users_without_tier:
            tier_record = UserTier(
                user_id=user.id,
                tier="FREE",
                daily_pyq_limit=10,
                weekly_mock_limit=1,
                daily_reel_limit=10,
                ai_chat_limit=5
            )
            db.add(tier_record)
            print(f"  • Created FREE tier for {user.username}")
        
        db.commit()
        print(f"✅ Successfully setup free trial for {len(users_without_tier)} users!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def reset_limits():
    """Reset all user limits (for testing)"""
    db = SessionLocal()
    
    try:
        confirm = input("⚠️  This will reset ALL user limits. Are you sure? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Operation cancelled")
            return
        
        # Delete all tier records
        deleted = db.query(UserTier).delete()
        db.commit()
        print(f"🗑️  Deleted {deleted} tier records")
        
        # Setup fresh limits
        setup_free_trial()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def show_statistics():
    """Show usage statistics"""
    db = SessionLocal()
    
    try:
        # Count users by tier
        free_users = db.query(UserTier).filter(UserTier.tier == "FREE").count()
        pro_users = db.query(UserTier).filter(UserTier.tier == "PRO").count()
        total_users = db.query(User).count()
        
        print(f"\n📊 User Statistics:")
        print(f"  • Total users: {total_users}")
        print(f"  • Free users: {free_users}")
        print(f"  • Pro users: {pro_users}")
        print(f"  • Conversion rate: {(pro_users/total_users*100):.1f}%" if total_users > 0 else "  • Conversion rate: 0%")
        
        # Today's usage
        today = datetime.now().strftime("%Y-%m-%d")
        today_usage = db.query(UserUsage).filter(UserUsage.usage_date == today).all()
        
        usage_by_type = {}
        for usage in today_usage:
            usage_by_type[usage.usage_type] = usage_by_type.get(usage.usage_type, 0) + usage.count
        
        print(f"\n📈 Today's Usage ({today}):")
        for usage_type, count in usage_by_type.items():
            print(f"  • {usage_type}: {count}")
        
        if not usage_by_type:
            print("  • No usage recorded today")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

def main():
    """Main menu loop"""
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                show_all_users()
            elif choice == '2':
                show_user_limits()
            elif choice == '3':
                upgrade_user()
            elif choice == '4':
                downgrade_user()
            elif choice == '5':
                setup_free_trial()
            elif choice == '6':
                reset_limits()
            elif choice == '7':
                show_statistics()
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 