import openai
import os
from fastapi import APIRouter
from pydantic import BaseModel
from knowledge import get_knowledge_base
from users import mock_users  # ideiglenesen
from database import SessionLocal
from crud import get_user
from auth import get_current_user
from fastapi import Depends
from crud import log_chat
from database import SessionLocal

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

profile_prompts = {
    "support": "You are a professional customer service assistant. Be helpful and polite.",
    "marketing": "You are a creative and persuasive copywriter and marketer.",
    "education": "You are a smart and friendly teacher who explains complex topics simply."
}

@chat_router.post("/chat")
async def chat(req: ChatRequest, user=Depends(get_current_user)):
    if not user.subscription_active:
        raise HTTPException(status_code=403, detail="Nincs aktív előfizetés.")

    # TIER alapú korlátozás
    if user.tier == "basic":
        model = "gpt-3.5-turbo"
        knowledge = user.knowledge_base[:500]  # max 500 karakter
        max_tokens = 250
    elif user.tier == "pro":
        model = "gpt-4"
        knowledge = user.knowledge_base
        max_tokens = 500
    else:  # VIP
        model = "gpt-4"
        knowledge = user.knowledge_base
        max_tokens = 1000

    profile_prompt = profile_prompts.get(user.selected_profile, profile_prompts["support"])
    full_prompt = f"{profile_prompt}\n\nKnowledge base:\n{knowledge}"

    completion = openai.ChatCompletion.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": req.message}
        ]
    )
    db = SessionLocal()
    log_chat(db, user.id, req.message, completion.choices[0].message.content)

    return {"response": completion.choices[0].message.content}
    full_prompt = f"{user.base_prompt}\n\nKnowledge base:\n{user.knowledge_base}"
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": req.message}
        ]
    )
    return {"response": completion.choices[0].message.content}

knowledge = get_knowledge_base()
base_prompt = f"""
You are a helpful assistant.
Knowledge base:
{knowledge}
"""

