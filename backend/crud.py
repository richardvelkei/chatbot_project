from sqlalchemy.orm import Session
from models_sql import User
from models_sql import ChatLog

def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_id: str):
    db_user = User(id=user_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def activate_subscription(db: Session, email: str, stripe_id: str):
    user = get_user(db, email)
    if user:
        user.subscription_active = True
        user.stripe_customer_id = stripe_id
        db.commit()
        return user
    return None

def get_all_users(db: Session):
    return db.query(User).all()

def log_chat(db: Session, user_id: str, question: str, answer: str):
    log = ChatLog(user_id=user_id, question=question, answer=answer)
    db.add(log)
    db.commit()
    return log