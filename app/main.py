# app/main.py
# FastAPI + Webhook لتلقي تحديثات تيليغرام في Render (خدمة ويب واحدة)
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.telegram_router import handle_update
from app.library_loader import ensure_library_loaded

app = FastAPI(title="AI Automation Telegram Bot")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")  # لحماية المسار
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

@app.on_event("startup")
async def startup():
    # حمّل مكتبة الوركفلو الجاهزة (اختياري)
    ensure_library_loaded()

@app.get("/")
async def root():
    return {"ok": True, "service": "ai-automation-telegram-bot"}

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Missing TELEGRAM_BOT_TOKEN")

    await handle_update(update)
    return JSONResponse({"ok": True})
