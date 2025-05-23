# chatbot_project/
# ├── backend/
# │   ├── admin.py
# │   ├── auth.py
# │   ├── chat.py
# │   ├── crud.py
# │   ├── database.py
# │   ├── knowledge.py
# │   ├── knowledge.txt
# │   ├── main.py
# │   ├── models.py
# │   ├── models.sql.py
# │   ├── requirements.txt
# │   ├── subscriptions.py
# │   ├── user.py
# │   └── .env
# ├── frontend/
# │   └── index.html
# ├── .gitignore
# ├── README.md
# ├── render.yaml
# └── requirements.txt

# --- backend/requirements.txt --- !!!
# fastapi
# openai
# uvicorn
# uvicorn main:app --host 0.0.0.0 --port 8000
# python-dotenv

# pip install stripe
#pip install sqlalchemy aiosqlite
#pip install passlib[bcrypt] python-jose


from fastapi import FastAPI
from routers.chat_router import router as chat_router
from routers.chat_router import router as chat_router
from subscriptions import subscription_router
from users import user_router
from backend.db_init import init_db


from database import Base, engine
Base.metadata.create_all(bind=engine)

from auth import auth_router
app.include_router(auth_router)

from admin import admin_router
app.include_router(admin_router)

app = FastAPI()
init_db()

app.include_router(user_router)
app.include_router(chat_router)
app.include_router(subscription_router)

@app.get("/")
def root():
    return {"message": "AI Chatbot API működik!"}


# Stripe integráció 
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.post("/create-checkout-session")
def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": "price_12345",  # A Stripe dashboardban beállított ár ID-je
            "quantity": 1,
        }],
        mode="subscription",
        success_url="https://yourdomain.com/success",
        cancel_url="https://yourdomain.com/cancel",
    )
    return {"url": session.url}

#webhook stripe

@subscription_router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Webhook aláírás hiba")

    # Példa: sikeres előfizetés
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session["customer_details"]["email"]
        # TODO: felhasználó beazonosítása és aktiválása
        print(f"Előfizetés aktív lett: {customer_email}")

    return {"status": "success"}


