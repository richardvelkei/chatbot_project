from pydantic import BaseModel

class User(BaseModel):
    id: str  # egyedi azonosító, pl. e-mail
    subscription_active: bool
    knowledge_base: str
    base_prompt: str
    stripe_customer_id: str | None = None

