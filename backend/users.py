from fastapi import APIRouter, HTTPException
from models import User
from crud import get_user, create_user
from database import SessionLocal
from auth import get_current_user
from fastapi import Depends

user_router = APIRouter()

# Mock adatbázis (később SQLite / PostgreSQL)
mock_users = {
    "gangster@example.com": User(
        id="gangster@example.com",
        subscription_active=False,
        knowledge_base="Ez egy teszt tudásbázis.",
        base_prompt="You are a helpful AI chatbot.",
        stripe_customer_id=None
    )
}


@user_router.get("/user/{user_id}")
def get_user_data(user_id: str, user=Depends(get_current_user)):
    if user_id != user.id:
        raise HTTPException(status_code=403, detail="Hozzáférés megtagadva")
    return user

@user_router.post("/user/{user_id}/knowledge")
def update_knowledge(user_id: str, content: str, user=Depends(get_current_user)):
    if user_id != user.id:
        raise HTTPException(status_code=403, detail="Hozzáférés megtagadva")
    user.knowledge_base = content
    db = SessionLocal()
    db.add(user)
    db.commit()
    return {"message": "Updated knowledge base."}

    @user_router.post("/user/{user_id}/profile")
def update_profile(user_id: str, profile: dict, user=Depends(get_current_user)):
    if user_id != user.id:
        raise HTTPException(status_code=403, detail="Hozzáférés megtagadva")

    allowed_profiles = {
        "basic": ["support"],
        "pro": ["support", "marketing"],
        "vip": ["support", "marketing", "education"]
    }

    if profile["profile"] not in allowed_profiles.get(user.tier, []):
        raise HTTPException(status_code=403, detail="Ez a profil nem elérhető a jelenlegi csomagodhoz.")

    user.selected_profile = profile["profile"]
    db = SessionLocal()
    db.add(user)
    db.commit()
    return {"message": "Profil sikeresen frissítve!"}

