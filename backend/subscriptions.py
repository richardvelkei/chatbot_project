import stripe
import os
from fastapi import APIRouter, Request, HTTPException
from users import mock_users
from crud import activate_subscription
from database import SessionLocal

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
subscription_router = APIRouter()

# Ez lesz az előfizetési gombot kiszolgáló endpoint
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

    
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            email = session["customer_details"]["email"]         
            # Itt aktiváljuk a user-t DB-ben
            stripe_id = session["customer"]

            db = SessionLocal()
            user = get_user(db, email)
            if not user:
                create_user(db, email)

            activate_subscription(db, email, stripe_id)
            print(f"[STRIPE] Előfizetés aktiválva: {email}")
        else:
            print(f"[STRIPE] Ismeretlen e-mail: {email}")

    return {"status": "success"}

@subscription_router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()
    email = data.get("email")
    tier = data.get("tier")

    tier_price_map = {
        "basic": "price_20_BASIC",
        "pro": "price_50_PRO",
        "vip": "price_100_VIP"
    }

    price_id = tier_price_map.get(tier)
    if not price_id:
        raise HTTPException(status_code=400, detail="Érvénytelen előfizetés szint")

    try:
        session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=["card"],
            line_items=[{
                "price": "price_1Nx...",  # ← IDE A STRIPE ÁR ID
                "quantity": 1,
            }],
            mode="subscription",
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )
        return {"url": session.url}
    except Exception as e:
        return {"error": str(e)}


#      if price_id == "price_50_PRO":
#          user.tier = "pro"
#      elif price_id == "price_100_VIP":
#          user.tier = "vip"
#      else:
#          user.tier = "basic"
