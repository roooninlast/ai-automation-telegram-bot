import os, json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from ai import plan_workflow_with_ai, draft_n8n_json_with_ai

app = FastAPI(title="AI Automation Telegram Bot")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

# معالج الرسائل النصية
async def handle_text_message(chat_id: int, text: str):
    """معالج الرسائل النصية - ينشئ workflow من الوصف"""
    try:
        # إنشاء خطة العمل
        plan = await plan_workflow_with_ai(text)
        
        # إنشاء JSON للـ workflow
        workflow_json = await draft_n8n_json_with_ai(plan)
        
        # إرسال الخطة أولاً
        plan_message = f"📋 **خطة العمل:**\n```\n{plan}\n```"
        await send_message(chat_id, plan_message)
        
        # إرسال الـ workflow JSON
        json_message = f"⚙️ **n8n Workflow:**\n```json\n{workflow_json}\n```"
        await send_message(chat_id, json_message)
        
    except Exception as e:
        error_msg = f"❌ حدث خطأ: {str(e)}"
        await send_message(chat_id, error_msg)

# إرسال رسالة عبر Telegram API
async def send_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """إرسال رسالة إلى المستخدم"""
    if not TELEGRAM_BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN not set")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

# معالج التحديثات الرئيسي
async def handle_update(update: dict):
    """معالج التحديثات من Telegram"""
    try:
        # التحقق من وجود رسالة
        if "message" not in update:
            return
        
        message = update["message"]
        chat_id = message["chat"]["id"]
        
        # رسالة البداية
        if "text" in message:
            text = message["text"].strip()
            
            if text.startswith("/start"):
                welcome_msg = (
                    "🤖 **مرحباً بك في بوت أتمتة الذكاء الاصطناعي!**\n\n"
                    "أرسل لي وصفاً لعملية الأتمتة التي تريد إنشاءها وسأقوم بإنتاج workflow جاهز لـ n8n.\n\n"
                    "**أمثلة:**\n"
                    "- عند استلام إيميل جديد، احفظ البيانات في Google Sheets\n"
                    "- عند إضافة منتج جديد، أرسل إشعار في Slack\n"
                    "- اربط نموذج الويب بقاعدة البيانات"
                )
                await send_message(chat_id, welcome_msg)
                
            elif text.startswith("/"):
                # أوامر أخرى
                await send_message(chat_id, "❓ أمر غير معروف. أرسل /start للبداية.")
            else:
                # معالجة الرسالة كطلب workflow
                await handle_text_message(chat_id, text)
        
    except Exception as e:
        print(f"[ERROR] handle_update failed: {e}")
        # محاولة إرسال رسالة خطأ للمستخدم
        try:
            if "message" in update and "chat" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                await send_message(chat_id, "❌ حدث خطأ تقني. حاول مرة أخرى لاحقاً.")
        except:
            pass

@app.get("/")
async def root():
    return {"ok": True, "service": "ai-automation-telegram-bot"}

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        print(f"[INFO] Received update: {json.dumps(update, ensure_ascii=False)}")
    except Exception as e:
        print(f"[ERROR] Invalid JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # معالجة التحديث
    try:
        await handle_update(update)
    except Exception as e:
        print(f"[ERROR] handle_update failed: {e}")
    
    return JSONResponse({"ok": True})

# إعداد الـ webhook عند بدء التشغيل
@app.on_event("startup")
async def set_webhook():
    """إعداد webhook مع Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("[WARNING] TELEGRAM_BOT_TOKEN not set - webhook setup skipped")
        return
    
    # الحصول على URL العام
    public_url = os.getenv("PUBLIC_APP_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if not public_url:
        print("[WARNING] No public URL found - webhook setup skipped")
        return
    
    webhook_url = f"{public_url.rstrip('/')}{WEBHOOK_PATH}"
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(telegram_api_url, json={
                "url": webhook_url,
                "drop_pending_updates": True
            })
            
            result = response.json()
            if result.get("ok"):
                print(f"[INFO] Webhook set successfully: {webhook_url}")
            else:
                print(f"[ERROR] Webhook setup failed: {result}")
                
    except Exception as e:
        print(f"[ERROR] Failed to set webhook: {e}")

# إعداد الملفات الثابتة
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.isdir(static_dir):
    app.mount("/docs", StaticFiles(directory=static_dir, html=True), name="docs")

# endpoint للتحقق من حالة البوت
@app.get("/bot-info")
async def bot_info():
    """معلومات البوت والحالة"""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not configured"}
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
            bot_data = response.json()
            
            webhook_response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo")
            webhook_data = webhook_response.json()
            
            return {
                "bot": bot_data,
                "webhook": webhook_data,
                "configured_webhook_path": WEBHOOK_PATH
            }
    except Exception as e:
        return {"error": str(e)}
