sdef get_knowledge_base():
    try:
        with open("backend/knowledge.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# --- backend/subscriptions.py ---
from fastapi import APIRouter

subscription_router = APIRouter()

@subscription_router.get("/subscription/check")
def check_subscription():
    return {"status": "mock subscription active"}