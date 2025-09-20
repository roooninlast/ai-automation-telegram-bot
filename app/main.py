import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI Automation Telegram Bot")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

@app.get("/")
async def root():
    return {"ok": True, "service": "ai-automation-telegram-bot"}

# Dummy handler (the full project had handle_update; here we ensure 200 even without it)
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Always return 200, never fail webhook
    try:
        # placeholder for actual processing
        pass
    except Exception as e:
        print("[ERROR] handle_update failed:", repr(e))
    return JSONResponse({"ok": True})

static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.isdir(static_dir):
    app.mount("/docs", StaticFiles(directory=static_dir, html=True), name="docs")
    
