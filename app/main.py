import os, json, asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from datetime import datetime

# تحسين إعدادات AI
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")  # نموذج أفضل
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# تحسين الـ system prompts
SYS_PLANNER = """You are an expert n8n workflow architect specializing in business automation.

TASK: Analyze the user's automation request and create a detailed, actionable plan.

RULES:
1. Be specific about triggers (webhook, schedule, email, etc.)
2. Break down into clear sequential steps
3. Mention specific n8n nodes to use
4. Include data transformations needed
5. Consider error handling
6. Write in English for technical accuracy

OUTPUT FORMAT:
**Trigger:** [specific trigger type and configuration]
**Steps:**
1. [Node type] - [specific purpose]
2. [Node type] - [specific purpose]
3. [Node type] - [specific purpose]
**Data Flow:** [how data moves between nodes]
**Environment Variables:** [list any needed env vars]
**Error Handling:** [error scenarios to handle]

Be practical and implementable in n8n."""

SYS_JSONER = """You are an expert n8n workflow JSON generator.

TASK: Convert the workflow plan into a complete, working n8n JSON that can be imported directly.

REQUIREMENTS:
1. Valid JSON structure with: name, nodes, connections, settings, tags
2. Unique node IDs (use descriptive names like "webhook_trigger", "process_data", etc.)
3. Proper node types (use correct n8n node names)
4. Accurate connections between nodes
5. Realistic parameters for each node
6. Use environment variables for sensitive data: {{$env.API_KEY}}
7. Include proper positioning for visual layout

COMMON N8N NODES:
- n8n-nodes-base.webhook (for HTTP triggers)
- n8n-nodes-base.httpRequest (for API calls)
- n8n-nodes-base.googleSheets (for Google Sheets)
- n8n-nodes-base.gmail (for email)
- n8n-nodes-base.slack (for Slack)
- n8n-nodes-base.code (for JavaScript processing)
- n8n-nodes-base.if (for conditions)
- n8n-nodes-base.set (for data manipulation)

OUTPUT: Valid n8n JSON only, no explanation."""

async def _chat(system: str, user: str, debug_context: str = "") -> str:
    """محسن مع debugging شامل"""
    if not OPENROUTER_API_KEY:
        print(f"[ERROR] {debug_context}: OPENROUTER_API_KEY not set!")
        raise RuntimeError("NO_OPENROUTER_KEY")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("RENDER_EXTERNAL_URL", ""),
        "X-Title": "AI Automation Telegram Bot",
    }
    
    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
    }
    
    print(f"[DEBUG] {debug_context}: Making API call to OpenRouter...")
    print(f"[DEBUG] Model: {OPENROUTER_MODEL}")
    print(f"[DEBUG] User prompt length: {len(user)} chars")
    
    start_time = datetime.now()
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(OPENROUTER_URL, headers=headers, json=body)
            
            duration = (datetime.now() - start_time).total_seconds()
            print(f"[DEBUG] {debug_context}: API call completed in {duration:.2f}s")
            print(f"[DEBUG] Response status: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"[ERROR] {debug_context}: API error {resp.status_code}: {resp.text}")
                raise httpx.HTTPStatusError(f"API returned {resp.status_code}", request=resp.request, response=resp)
            
            data = resp.json()
            
            if "choices" not in data or not data["choices"]:
                print(f"[ERROR] {debug_context}: No choices in response: {data}")
                raise RuntimeError("Invalid API response structure")
            
            content = data["choices"][0]["message"]["content"]
            print(f"[SUCCESS] {debug_context}: Got response, length: {len(content)} chars")
            print(f"[DEBUG] Response preview: {content[:200]}...")
            
            # تحقق من استخدام الرصيد
            if "usage" in data:
                usage = data["usage"]
                print(f"[INFO] Token usage - Prompt: {usage.get('prompt_tokens', 0)}, Completion: {usage.get('completion_tokens', 0)}")
            
            return content
            
    except httpx.TimeoutException:
        print(f"[ERROR] {debug_context}: Request timeout after 120s")
        raise RuntimeError("API request timeout")
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] {debug_context}: HTTP error: {e}")
        raise RuntimeError(f"API HTTP error: {e.response.status_code}")
    except Exception as e:
        print(f"[ERROR] {debug_context}: Unexpected error: {type(e).__name__}: {e}")
        raise RuntimeError(f"API call failed: {str(e)}")

async def plan_workflow_with_ai(user_prompt: str) -> tuple[str, bool]:
    """إنشاء خطة العمل مع تتبع المصدر"""
    try:
        print(f"[INFO] Planning workflow for prompt: {user_prompt[:100]}...")
        
        # إضافة سياق إضافي للطلب
        enhanced_prompt = f"""
USER REQUEST: {user_prompt}

Please analyze this automation request and create a detailed technical plan for n8n implementation.
Consider:
- What specific trigger makes most sense?
- What APIs or services might be involved?
- What data transformations are needed?
- How to handle errors and edge cases?
- What environment variables or credentials are needed?

Create a step-by-step technical plan that a developer can follow to build this in n8n.
"""
        
        result = await _chat(SYS_PLANNER, enhanced_prompt, "PLANNER")
        return result, True  # True = من الذكاء الاصطناعي
        
    except Exception as e:
        print(f"[WARNING] Planning fallback due to: {repr(e)}")
        fallback = f"""**FALLBACK PLAN** (AI unavailable)
        
**Trigger:** Webhook or Schedule (based on user request)
**Steps:**
1. Trigger Node - Receive input data
2. Processing Node - Transform/validate data  
3. Action Node - Execute the main task
4. Response Node - Send confirmation/result

**User Request:** {user_prompt}

**Note:** This is a basic template. For detailed workflow, ensure OPENROUTER_API_KEY is configured properly."""
        
        return fallback, False  # False = fallback

async def draft_n8n_json_with_ai(plan: str) -> tuple[str, bool]:
    """إنشاء JSON مع تتبع المصدر"""
    
    # JSON احتياطي محسن
    fallback_json = {
        "name": "AI Generated Workflow",
        "nodes": [
            {
                "id": "webhook_trigger",
                "name": "Webhook Trigger", 
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "parameters": {
                    "path": "automation-webhook",
                    "responseMode": "onReceived",
                    "httpMethod": "POST"
                }
            },
            {
                "id": "process_data",
                "name": "Process Data",
                "type": "n8n-nodes-base.code",
                "typeVersion": 1, 
                "position": [460, 300],
                "parameters": {
                    "jsCode": "// Process incoming data\nconst inputData = $input.all();\nconst processedData = inputData.map(item => {\n  return {\n    ...item.json,\n    processed_at: new Date().toISOString(),\n    status: 'processed'\n  };\n});\n\nreturn processedData;"
                }
            },
            {
                "id": "send_response",
                "name": "Send Response",
                "type": "n8n-nodes-base.respondToWebhook", 
                "typeVersion": 1,
                "position": [680, 300],
                "parameters": {
                    "responseBody": "{\\"status\\": \\"success\\", \\"message\\": \\"Automation completed\\"}"
                }
            }
        ],
        "connections": {
            "webhook_trigger": {
                "main": [[{"node": "process_data", "type": "main", "index": 0}]]
            },
            "process_data": {
                "main": [[{"node": "send_response", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "timezone": "UTC"
        },
        "tags": ["ai-generated", "automation"]
    }
    
    try:
        print("[INFO] Generating n8n JSON from plan...")
        
        enhanced_plan = f"""
Based on this workflow plan, generate a complete n8n JSON:

{plan}

Requirements:
1. Create a realistic, working n8n workflow
2. Use proper n8n node types and parameters
3. Include proper error handling where appropriate
4. Use environment variables for sensitive data
5. Ensure all connections are valid
6. Position nodes in a logical flow (left to right)

Generate ONLY valid JSON, no explanations.
"""
        
        result = await _chat(SYS_JSONER, enhanced_plan, "JSON_GENERATOR")
        
        # محاولة التحقق من صحة JSON
        try:
            json.loads(result)
            print("[SUCCESS] Generated valid JSON from AI")
            return result, True
        except json.JSONDecodeError as e:
            print(f"[ERROR] AI generated invalid JSON: {e}")
            # محاولة تنظيف JSON
            cleaned = result.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            try:
                json.loads(cleaned)
                print("[SUCCESS] Fixed JSON formatting")
                return cleaned, True
            except:
                print("[ERROR] Could not fix JSON, using fallback")
                return json.dumps(fallback_json, indent=2), False
        
    except Exception as e:
        print(f"[WARNING] JSON generation fallback due to: {repr(e)}")
        return json.dumps(fallback_json, indent=2), False

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
    
    # تقسيم الرسائل الطويلة
    max_length = 4000
    if len(text) > max_length:
        parts = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        for i, part in enumerate(parts):
            await asyncio.sleep(0.5)  # تأخير بسيط بين الرسائل
            await _send_single_message(chat_id, f"({i+1}/{len(parts)})\n{part}", parse_mode)
    else:
        await _send_single_message(chat_id, text, parse_mode)

async def _send_single_message(chat_id: int, text: str, parse_mode: str):
    """إرسال رسالة واحدة"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
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

# معالج الرسائل النصية المحسن
async def handle_text_message(chat_id: int, text: str):
    """معالج الرسائل النصية - ينشئ workflow من الوصف"""
    try:
        print(f"[INFO] Processing automation request: {text[:100]}...")
        
        # إرسال رسالة "جاري المعالجة"
        await send_message(chat_id, "⏳ جاري تحليل طلبك وإنشاء الـ workflow...")
        
        # تحقق من إعداد API
        if not OPENROUTER_API_KEY:
            await send_message(chat_id, 
                "❌ **خطأ في الإعداد**\n\n"
                "OPENROUTER_API_KEY غير مُعرف في متغيرات البيئة.\n"
                "البوت سيستخدم templates أساسية فقط."
            )
        
        # إنشاء خطة العمل
        plan, ai_generated_plan = await plan_workflow_with_ai(text)
        
        # إرسال الخطة
        plan_status = "🤖 **بواسطة الذكاء الاصطناعي**" if ai_generated_plan else "⚙️ **Template أساسي**"
        plan_message = f"📋 **خطة العمل** {plan_status}\n\n```\n{plan}\n```"
        await send_message(chat_id, plan_message)
        
        # إنشاء JSON للـ workflow
        await send_message(chat_id, "⚙️ جاري إنشاء n8n workflow...")
        workflow_json, ai_generated_json = await draft_n8n_json_with_ai(plan)
        
        # إرسال الـ workflow JSON
        json_status = "🤖 **بواسطة الذكاء الاصطناعي**" if ai_generated_json else "⚙️ **Template أساسي**"
        json_message = f"💻 **n8n Workflow** {json_status}\n\n```json\n{workflow_json}\n```"
        await send_message(chat_id, json_message)
        
        # رسالة الإرشادات
        instructions = (
            "📝 **كيفية الاستخدام:**\n"
            "1. انسخ الـ JSON أعلاه بالكامل\n"
            "2. في n8n اختر: **Import from clipboard**\n"
            "3. الصق الكود واضغط Import\n"
            "4. اضبط متغيرات البيئة والاتصالات المطلوبة\n"
            "5. اختبر الـ workflow قبل التفعيل\n"
            "6. فعّل الـ workflow\n\n"
            f"**حالة AI:** {'✅ متصل' if ai_generated_plan and ai_generated_json else '❌ غير متوفر (استخدام Templates)'}"
        )
        await send_message(chat_id, instructions)
        
    except Exception as e:
        print(f"[ERROR] handle_text_message failed: {e}")
        error_msg = (
            f"❌ **حدث خطأ أثناء المعالجة**\n\n"
            f"**الخطأ:** {str(e)[:200]}\n\n"
            f"**الحلول المحتملة:**\n"
            f"• تحقق من صحة OPENROUTER_API_KEY\n"
            f"• تحقق من الرصيد في OpenRouter\n"
            f"• حاول مرة أخرى بعد دقائق قليلة\n"
            f"• تأكد من الاتصال بالإنترنت"
        )
        await send_message(chat_id, error_msg)

# معالج التحديثات الرئيسي
async def handle_update(update: dict):
    """معالج التحديثات من Telegram"""
    try:
        if "message" not in update:
            return
        
        message = update["message"]
        if "chat" not in message:
            return
            
        chat_id = message["chat"]["id"]
        
        if "text" in message:
            text = message["text"].strip()
            
            if text.startswith("/start"):
                welcome_msg = (
                    "🤖 **مرحباً بك في بوت أتمتة الذكاء الاصطناعي!**\n\n"
                    "أرسل لي وصفاً **مفصلاً ومحدداً** لعملية الأتمتة التي تريد إنشاءها.\n\n"
                    "**أمثلة جيدة:**\n"
                    "• \"عندما يملأ شخص نموذج الاتصال على موقعي، أريد حفظ بياناته في Google Sheets وإرسال رسالة ترحيب تلقائية عبر Gmail\"\n\n"
                    "• \"عند إضافة منتج جديد في WooCommerce، أريد إرسال إشعار في قناة Slack المحددة مع تفاصيل المنتج\"\n\n"
                    "• \"كل يوم في الساعة 9 صباحاً، أريد جلب التقارير من Google Analytics وإرسالها عبر البريد الإلكتروني للفريق\"\n\n"
                    f"**حالة AI:** {'✅ متصل' if OPENROUTER_API_KEY else '❌ غير متوفر'}"
                )
                await send_message(chat_id, welcome_msg)
                
            elif text.startswith("/test"):
                # اختبار الاتصال بـ OpenRouter
                await send_message(chat_id, "🔍 جاري اختبار الاتصال بـ OpenRouter...")
                try:
                    test_result, ai_used = await plan_workflow_with_ai("Test connection")
                    if ai_used:
                        await send_message(chat_id, "✅ **اختبار ناجح!**\nالذكاء الاصطناعي متصل ويعمل بشكل صحيح.")
                    else:
                        await send_message(chat_id, "❌ **اختبار فاشل!**\nيتم استخدام Templates أساسية فقط.")
                except Exception as e:
                    await send_message(chat_id, f"❌ **اختبار فاشل!**\n```\n{str(e)}\n```")
                    
            elif text.startswith("/help"):
                help_msg = (
                    "📚 **دليل الاستخدام المفصل:**\n\n"
                    "**1. كيفية كتابة طلب جيد:**\n"
                    "• كن محدداً: اذكر التطبيقات/الخدمات بالاسم\n"
                    "• اذكر التوقيت: متى يحدث التشغيل؟\n"
                    "• اذكر البيانات: ما المعلومات المطلوبة؟\n"
                    "• اذكر الإجراء: ماذا يجب أن يحدث؟\n\n"
                    "**2. أمثلة للطلبات:**\n"
                    "✅ جيد: \"عند استلام إيميل في Gmail يحتوي على كلمة 'فاتورة'، استخرج المرفقات وارفعها على Google Drive في مجلد 'الفواتير'\"\n\n"
                    "❌ غير واضح: \"أريد أتمتة للإيميلات\"\n\n"
                    "**3. الأوامر المتوفرة:**\n"
                    "• `/start` - البداية\n"
                    "• `/help` - هذا الدليل\n"
                    "• `/test` - اختبار الاتصال بالذكاء الاصطناعي\n"
                    "• `/status` - حالة البوت والإعدادات"
                )
                await send_message(chat_id, help_msg)
                
            elif text.startswith("/status"):
                status_msg = (
                    f"📊 **حالة البوت:**\n\n"
                    f"**OpenRouter API:** {'✅ مُعرف' if OPENROUTER_API_KEY else '❌ غير مُعرف'}\n"
                    f"**النموذج:** {OPENROUTER_MODEL}\n"
                    f"**Webhook:** {'✅ نشط' if TELEGRAM_BOT_TOKEN else '❌ غير مُعرف'}\n"
                    f"**URL:** {os.getenv('RENDER_EXTERNAL_URL', 'غير محدد')}\n\n"
                    "**للحصول على OpenRouter API Key:**\n"
                    "1. اذهب إلى https://openrouter.ai\n"
                    "2. سجل حساب جديد\n"
                    "3. اذهب إلى API Keys\n"
                    "4. أنشئ مفتاح جديد\n"
                    "5. اضبطه في متغيرات البيئة"
                )
                await send_message(chat_id, status_msg)
                
            elif text.startswith("/"):
                await send_message(chat_id, "❓ أمر غير معروف. أرسل `/help` للمساعدة.")
            else:
                # معالجة الطلب
                await handle_text_message(chat_id, text)
        else:
            await send_message(chat_id, "📝 أرسل لي نصاً يصف عملية الأتمتة المطلوبة بالتفصيل")
        
    except Exception as e:
        print(f"[ERROR] handle_update failed: {e}")
        try:
            if "message" in update and "chat" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                await send_message(chat_id, "❌ حدث خطأ تقني. حاول مرة أخرى لاحقاً.")
        except:
            pass

@app.get("/")
async def root():
    return {"ok": True, "service": "ai-automation-telegram-bot", "status": "running"}

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # معالجة التحديث
    try:
        asyncio.create_task(handle_update(update))
    except Exception as e:
        print(f"[ERROR] Failed to create task: {e}")
    
    return JSONResponse({"ok": True})

# إعداد الـ webhook عند بدء التشغيل
@app.on_event("startup")
async def set_webhook():
    """إعداد webhook مع Telegram"""
    print("[INFO] Starting webhook setup...")
    
    if not TELEGRAM_BOT_TOKEN:
        print("[WARNING] TELEGRAM_BOT_TOKEN not set")
        return
    
    public_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("PUBLIC_APP_URL")
    if not public_url:
        print("[WARNING] No public URL found")
        return
    
    webhook_url = f"{public_url.rstrip('/')}{WEBHOOK_PATH}"
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
                json={"url": webhook_url, "drop_pending_updates": True}
            )
            
            result = response.json()
            if result.get("ok"):
                print(f"[SUCCESS] Webhook set: {webhook_url}")
            else:
                print(f"[ERROR] Webhook setup failed: {result}")
                
    except Exception as e:
        print(f"[ERROR] Failed to set webhook: {e}")

@app.get("/bot-info")
async def bot_info():
    """معلومات البوت والحالة"""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not configured"}
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            bot_response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
            webhook_response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo")
            
            return {
                "bot": bot_response.json(),
                "webhook": webhook_response.json(),
                "openrouter_configured": bool(OPENROUTER_API_KEY),
                "model": OPENROUTER_MODEL,
                "webhook_path": WEBHOOK_PATH
            }
    except Exception as e:
        return {"error": str(e)}

# إعداد الملفات الثابتة
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.isdir(static_dir):
    app.mount("/docs", StaticFiles(directory=static_dir, html=True), name="docs")
