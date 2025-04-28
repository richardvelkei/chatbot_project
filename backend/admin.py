import csv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from crud import get_user, get_all_users
from auth import get_current_user
from models_sql import User
from sqlalchemy import func
from models_sql import ChatLog
from fastapi.responses import StreamingResponse
from io import StringIO

admin_router = APIRouter()

def is_admin(user: User):
    # Egyszerű admin ellenőrzés email alapján
    return user.id == "gangster@example.com"

@admin_router.get("/admin/users")
def list_users(user=Depends(get_current_user)):
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Csak admin érheti el.")
    db = SessionLocal()
    return get_all_users(db)

@admin_router.post("/admin/users/{user_id}/activate")
def manual_activate(user_id: str, user=Depends(get_current_user)):
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Csak admin érheti el.")
    db = SessionLocal()
    target = get_user(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User nem található.")
    target.subscription_active = True
    db.commit()
    return {"message": f"{user_id} előfizetése aktiválva."}

@admin_router.get("/admin/stats")
def get_stats(user=Depends(get_current_user)):
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Csak admin érheti el.")
    db = SessionLocal()
    all_users = get_all_users(db)
    total = len(all_users)
    active = len([u for u in all_users if u.subscription_active])
    return {
        "total_users": total,
        "active_subscriptions": active
    }

@admin_router.get("/admin/stats/questions-per-day")
def questions_per_day(user=Depends(get_current_user)):
    if not is_admin(user):
        raise HTTPException(status_code=403)

    db = SessionLocal()
    result = db.query(
        func.date(ChatLog.timestamp).label("day"),
        func.count(ChatLog.id).label("count")
    ).group_by(func.date(ChatLog.timestamp)).order_by(func.date(ChatLog.timestamp).desc()).all()

    return [{"day": str(r.day), "count": r.count} for r in result]

@admin_router.get("/admin/chatlog/export")
def export_chatlog(user=Depends(get_current_user)):
    if not is_admin(user):
        raise HTTPException(status_code=403)

    db = SessionLocal()
    logs = db.query(ChatLog).order_by(ChatLog.timestamp.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "user_id", "question", "answer"])

    for log in logs:
        writer.writerow([log.timestamp, log.user_id, log.question, log.answer])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=chatlog.csv"
    })
