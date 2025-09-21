import os, json, asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx

# تعريف دوال AI محلياً لتجنب مشاكل الاستيراد
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYS_PLANNER = (
    "You are an automation architect for n8n. "
    "Your job: extract missing details via assumptions (be sane), propose a clear trigger + steps, "
    "and output a concise plan describing each node purpose and edges."
)
SYS_JSONER = (
    "You are an expert n8n workflow generator. "
    "Output MUST be a single valid JSON for n8n import with keys: name, nodes, connections, settings, tags. "
    "IDs must be unique. Use env refs like {{$env.SHEET_ID}}. Ensure connections match node IDs."
)

async def _chat(system: str, user: str) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("NO_OPENROUTER_KEY")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("PUBLIC_APP_URL", ""),
        "X-Title": "AI Automation Telegram Bot",
    }
    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(OPENROUTER_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

async def plan_workflow_with_ai(user_prompt: str) -> str:
    try:
        return await _chat(SYS_PLANNER, user_prompt)
    except Exception as e:
        print("[AI] planner fallback due to:", repr(e))
        return f"Trigger: decide based on prompt.\nSteps: parse → fetch/process → output.\nUserPrompt: {user_prompt}"

async def draft_n8n_json_with_ai(plan: str) -> str:
    fallback = {
        "name": "Webhook → Google Sheets (Sample)",
        "nodes": [
            {
                "id": "wh1",
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [200, 200],
                "parameters": {"path": "auto_generate", "responseMode": "onReceived"}
            },
            {
                "id": "gs1",
                "name": "Append to Sheet",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 1,
                "position": [520, 200],
                "parameters": {
                    "operation": "append",
                    "sheetId": "={{$env.SHEET_ID}}",
                    "range": "={{$env.SHEET_RANGE}}"
                }
            }
        ],
        "connections": {"wh1": {"main": [[{"node": "gs1", "type": "main", "index": 0}]]}},
        "settings": {},
        "tags": ["generated", "sample"]
    }
    try:
        return await _chat(SYS_JSONER, plan)
    except Exception as e:
        print("[AI] json fallback due to:", repr(e))
        return json.dumps(fallback, indent=2)

# إنشاء FastAPI app
app = FastAPI(title="AI Automation Telegram Bot")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

# إرسال رسالة عبر Telegram API
async def send_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """إرسال رسالة إلى المستخدم"""
    if not TELEGRAM_BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN not set")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4000],  # حد أقصى للنص
        "parse_mode": parse_mode
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[ERROR] Telegram API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
        return None

# معالج الرسائل النصية
async def handle_text_message(chat_id: int, text: str):
    """معالج الرسائل النصية - ينشئ workflow من الوصف"""
    try:
        # إرسال رسالة "جاري المعالجة"
        await send_message(chat_id, "⏳ جاري إنشاء الـ workflow... قد يستغرق بضع ثوانٍ")
        
        # إنشاء خطة العمل
        plan = await plan_workflow_with_ai(text)
        
        # إنشاء JSON للـ workflow
        workflow_json = await draft_n8n_json_with_ai(plan)
        
        # إرسال الخطة أولاً
        plan_message = f"📋 **خطة العمل:**\n```\n{plan[:3000]}\n```"
        await send_message(chat_id, plan_message)
        
        # إرسال الـ workflow JSON
        if len(workflow_json) > 3500:
            # إذا كان النص طويلاً، أرسله على أجزاء
            await send_message(chat_id, "⚙️ **n8n Workflow (جزء 1):**\n```json\n" + workflow_json[:3000] + "\n```")
            await send_message(chat_id, "⚙️ **n8n Workflow (جزء 2):**\n```json\n" + workflow_json[3000:] + "\n```")
        else:
            json_message = f"⚙️ **n8n Workflow:**\n```json\n{workflow_json}\n```"
            await send_message(chat_id, json_message)
            
        # رسالة الإرشادات
        instructions = (
            "📝 **كيفية الاستخدام:**\n"
            "1. انسخ الـ JSON أعلاه\n"
            "2. اذهب إلى n8n واختر Import from clipboard\n"
            "3. الصق الكود والصق\n"
            "4. اضبط متغيرات البيئة المطلوبة\n"
            "5. فعّل الـ workflow"
        )
        await send_message(chat_id, instructions)
        
    except Exception as e:
        print(f"[ERROR] handle_text_message failed: {e}")
        error_msg = f"❌ حدث خطأ أثناء المعالجة: {str(e)[:200]}"
        await send_message(chat_id, error_msg)

# معالج التحديثات الرئيسي
async def handle_update(update: dict):
    """معالج التحديثات من Telegram"""
    try:
        # التحقق من وجود رسالة
        if "message" not in update:
            print("[INFO] Update without message, skipping")
            return
        
        message = update["message"]
        if "chat" not in message:
            print("[INFO] Message without chat, skipping")
            return
            
        chat_id = message["chat"]["id"]
        print(f"[INFO] Processing message from chat_id: {chat_id}")
        
        # رسالة نصية
        if "text" in message:
            text = message["text"].strip()
            print(f"[INFO] Received text: {text[:100]}")
            
            if text.startswith("/start"):
                welcome_msg = (
                    "🤖 **مرحباً بك في بوت أتمتة الذكاء الاصطناعي!**\n\n"
                    "أرسل لي وصفاً لعملية الأتمتة التي تريد إنشاءها وسأقوم بإنتاج workflow جاهز لـ n8n.\n\n"
                    "**أمثلة:**\n"
                    "• عند استلام إيميل جديد، احفظ البيانات في Google Sheets\n"
                    "• عند إضافة منتج جديد، أرسل إشعار في Slack\n"
                    "• اربط نموذج الويب بقاعدة البيانات\n\n"
                    "**ملاحظة:** تأكد من إعداد OPENROUTER_API_KEY في متغيرات البيئة."
                )
                await send_message(chat_id, welcome_msg)
                
            elif text.startswith("/help"):
                help_msg = (
                    "ℹ️ **كيفية الاستخدام:**\n\n"
                    "1. أرسل وصفاً واضحاً للأتمتة المطلوبة\n"
                    "2. سأقوم بإنشاء خطة عمل\n"
                    "3. ثم سأنتج workflow JSON لـ n8n\n"
                    "4. انسخ والصق في n8n\n\n"
                    "**مثال جيد:**\n"
                    "\"عندما يتم ملء نموذج على الموقع، أرسل بيانات العميل إلى Google Sheets وأرسل رسالة ترحيب عبر البريد الإلكتروني\""
                )
                await send_message(chat_id, help_msg)
                
            elif text.startswith("/"):
                await send_message(chat_id, "❓ أمر غير معروف. أرسل /help للمساعدة.")
            else:
                # معالجة الرسالة كطلب workflow
                if not OPENROUTER_API_KEY:
                    await send_message(chat_id, "❌ خطأ: OPENROUTER_API_KEY غير مُعرف في متغيرات البيئة")
                    return
                await handle_text_message(chat_id, text)
        else:
            await send_message(chat_id, "📝 أرسل لي نصاً يصف الأتمتة المطلوبة")
        
    except Exception as e:
        print(f"[ERROR] handle_update failed: {e}")
        # محاولة إرسال رسالة خطأ للمستخدم
        try:
            if "message" in update and "chat" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                await send_message(chat_id, "❌ حدث خطأ تقني. حاول مرة أخرى لاحقاً.")
        except Exception as send_error:
            print(f"[ERROR] Failed to send error message: {send_error}")

@app.get("/")
async def root():
    return {"ok": True, "service": "ai-automation-telegram-bot", "status": "running"}

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        print(f"[INFO] Received webhook update")
    except Exception as e:
        print(f"[ERROR] Invalid JSON in webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # معالجة التحديث في background task
    try:
        # استخدام asyncio.create_task بدلاً من await مباشرة
        asyncio.create_task(handle_update(update))
    except Exception as e:
        print(f"[ERROR] Failed to create task for update: {e}")
    
    # إرجاع استجابة فورية لـ Telegram
    return JSONResponse({"ok": True})

# إعداد الـ webhook عند بدء التشغيل
@app.on_event("startup")
async def set_webhook():
    """إعداد webhook مع Telegram"""
    print("[INFO] Starting webhook setup...")
    
    if not TELEGRAM_BOT_TOKEN:
        print("[WARNING] TELEGRAM_BOT_TOKEN not set - webhook setup skipped")
        return
    
    # الحصول على URL العام
    public_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("PUBLIC_APP_URL")
    if not public_url:
        print("[WARNING] No public URL found - webhook setup skipped")
        return
    
    webhook_url = f"{public_url.rstrip('/')}{WEBHOOK_PATH}"
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            print(f"[INFO] Setting webhook to: {webhook_url}")
            response = await client.post(telegram_api_url, json={
                "url": webhook_url,
                "drop_pending_updates": True
            })
            
            result = response.json()
            if result.get("ok"):
                print(f"[SUCCESS] Webhook set successfully: {webhook_url}")
            else:
                print(f"[ERROR] Webhook setup failed: {result}")
                
    except Exception as e:
        print(f"[ERROR] Failed to set webhook: {e}")

# endpoint للتحقق من حالة البوت
@app.get("/bot-info")
async def bot_info():
    """معلومات البوت والحالة"""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not configured"}
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # معلومات البوت
            bot_response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
            bot_data = bot_response.json()
            
            # معلومات الـ webhook
            webhook_response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo")
            webhook_data = webhook_response.json()
            
            return {
                "bot": bot_data,
                "webhook": webhook_data,
                "configured_webhook_path": WEBHOOK_PATH,
                "openrouter_configured": bool(OPENROUTER_API_KEY),
                "public_url": os.getenv("RENDER_EXTERNAL_URL") or os.getenv("PUBLIC_APP_URL")
            }
    except Exception as e:
        return {"error": str(e)}

# إعداد الملفات الثابتة (إن وجدت)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.isdir(static_dir):
    app.mount("/docs", StaticFiles(directory=static_dir, html=True), name="docs")
