from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

class ChatLog(Base):
    __tablename__ = "chatlogs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)  # pl. email
    hashed_password = Column(String)
    subscription_active = Column(Boolean, default=False)
    tier = Column(String, default="basic")
    knowledge_base = Column(String, default="")
    base_prompt = Column(String, default="You are a helpful assistant.")
    stripe_customer_id = Column(String, nullable=True)
    selected_profile = Column(String, default="support")
