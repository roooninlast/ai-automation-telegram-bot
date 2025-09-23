import os, json, asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from datetime import datetime
from io import BytesIO

# استيراد نظام AI الجديد  
try:
    from ai import (
        plan_workflow_with_ai,
        draft_n8n_json_with_ai, 
        test_gemini_connection,
        get_available_templates
    )
    from n8n_builder import validate_n8n_json, make_minimal_valid_n8n
    AI_SYSTEM_AVAILABLE = True
    print("[INFO] AI system loaded successfully")
except ImportError as e:
    print(f"[WARNING] AI system not available: {e}")
    AI_SYSTEM_AVAILABLE = False

# إنشاء FastAPI app
app = FastAPI(title="AI n8n Automation Bot with Gemini")

# متغيرات البيئة
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

async def send_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """إرسال رسالة نصية مع تقسيم الرسائل الطويلة"""
    if not TELEGRAM_BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN not set")
        return False
    
    max_length = 4000
    if len(text) > max_length:
        parts = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        for i, part in enumerate(parts):
            await asyncio.sleep(0.5)
            success = await _send_single_message(chat_id, f"({i+1}/{len(parts)})\n{part}", parse_mode)
            if not success:
                return False
        return True
    else:
        return await _send_single_message(chat_id, text, parse_mode)

async def _send_single_message(chat_id: int, text: str, parse_mode: str) -> bool:
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
                return True
            else:
                print(f"[ERROR] Telegram message error: {response.status_code}")
                return False
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
        return False

async def send_document(chat_id: int, filename: str, content: bytes, caption: str = ""):
    """إرسال ملف عبر Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN not set")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    
    try:
        files = {
            'document': (filename, BytesIO(content), 'application/json')
        }
        data = {
            'chat_id': chat_id,
            'caption': caption[:1024] if caption else ""  # تحديد طول الوصف
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, data=data, files=files)
            if response.status_code == 200:
                print(f"[SUCCESS] File sent: {filename}")
                return True
            else:
                print(f"[ERROR] Failed to send document: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"[ERROR] Exception sending document: {e}")
        return False

async def handle_text_message(chat_id: int, text: str):
    """معالج الرسائل النصية مع إرسال ملف n8n"""
    try:
        print(f"[INFO] Processing automation request: {text[:100]}...")
        
        # رسالة بداية المعالجة
        await send_message(chat_id, "⏳ جاري تحليل طلبك وإنشاء workflow مخصص...")
        
        # التحقق من توفر النظام
        if not AI_SYSTEM_AVAILABLE:
            await send_message(chat_id, 
                "❌ **نظام AI غير متوفر**\n\n"
                "تحقق من وجود ملفات النظام المطلوبة."
            )
            return
        
        # تحليل الطلب وإنشاء الخطة
        plan, ai_used_for_plan = await plan_workflow_with_ai(text)
        
        # إرسال تحليل الطلب
        analysis_status = "🤖 **بواسطة Gemini AI**" if ai_used_for_plan else "📋 **تحليل محلي**"
        plan_message = f"📊 **تحليل الطلب** {analysis_status}\n\n{plan}"
        await send_message(chat_id, plan_message)
        
        # إنشاء workflow
        await send_message(chat_id, "⚙️ جاري إنشاء n8n workflow...")
        workflow_json, ai_used_for_workflow = await draft_n8n_json_with_ai(plan)
        
        # التحقق من صحة JSON والتنظيف
        try:
            workflow_data = json.loads(workflow_json)
            validated_workflow = validate_n8n_json(workflow_data)
            final_json = json.dumps(validated_workflow, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARNING] JSON validation failed: {e}")
            # إنشاء workflow احتياطي
            fallback_workflow = make_minimal_valid_n8n(
                "Generated Automation", 
                f"Created for: {text[:200]}"
            )
            final_json = json.dumps(fallback_workflow, ensure_ascii=False, indent=2)
            ai_used_for_workflow = False
        
        # إعداد معلومات الملف
        try:
            workflow_info = json.loads(final_json)
            workflow_name = workflow_info.get('name', 'automation_workflow')
            # تنظيف اسم الملف
            safe_filename = "".join(c for c in workflow_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_filename}.json"
        except:
            filename = "n8n_workflow.json"
        
        # إعداد وصف الملف
        workflow_status = "🤖 **مخصص بواسطة AI**" if ai_used_for_workflow else "📄 **من القوالب الأساسية**"
        
        file_caption = f"""💻 **n8n Workflow** {workflow_status}

📄 **الملف:** {filename}
🔧 **جاهز للاستيراد في n8n**

**تعليمات الاستخدام:**
1. حمّل الملف المرفق
2. افتح n8n وانتقل إلى Workflows  
3. اضغط "Import from file"
4. ارفع الملف المحمل
5. اضبط المتغيرات والاتصالات
6. اختبر الـ workflow قبل التفعيل

**حالة AI:** {'✅ متصل' if ai_used_for_plan and ai_used_for_workflow else '⚠️ محدود'}"""
        
        # إرسال الملف
        file_content = final_json.encode('utf-8')
        file_sent = await send_document(chat_id, filename, file_content, file_caption)
        
        if file_sent:
            # إرسال تعليمات إضافية
            instructions = """📚 **معلومات إضافية:**

**متغيرات البيئة الشائعة:**
• `GOOGLE_SHEET_ID` - معرف جدول Google Sheets
• `SLACK_CHANNEL` - قناة Slack (مثل: #general)
• `REPORT_EMAIL` - البريد الإلكتروني للتقارير
• `API_ENDPOINT` - رابط API للبيانات

**الاتصالات المطلوبة:**
• Google Sheets API - لحفظ البيانات
• Gmail API - لإرسال الرسائل  
• Slack API - للإشعارات

**نصائح:**
• اختبر كل عقدة منفرداً قبل تشغيل الـ workflow كاملاً
• راجع الـ logs في حال حدوث أخطاء
• استخدم Test Workflow لاختبار البيانات

**للمساعدة:** أرسل /help"""
            
            await send_message(chat_id, instructions)
        else:
            # في حال فشل إرسال الملف، أرسل JSON كنص
            await send_message(chat_id, 
                "⚠️ فشل إرسال الملف. إليك الكود للنسخ:\n\n"
                f"```json\n{final_json[:3500]}\n```"
            )
        
    except Exception as e:
        print(f"[ERROR] handle_text_message failed: {e}")
        error_msg = f"""❌ **حدث خطأ أثناء المعالجة**

**الخطأ:** {str(e)[:200]}

**الحلول المحتملة:**
• تحقق من صحة GEMINI_API_KEY
• تأكد من الاتصال بالإنترنت  
• حاول مرة أخرى بعد دقائق قليلة
• تأكد من وضوح وصف طلب الأتمتة

**للمساعدة:** أرسل /help"""
        await send_message(chat_id, error_msg)

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
                welcome_msg = f"""🤖 **مرحباً بك في بوت n8n الذكي!**

أنا بوت متخصص في إنشاء workflows للأتمتة باستخدام n8n وتقنية Gemini AI.

**كيف أعمل:**
1. أرسل لي وصفاً مفصلاً للأتمتة المطلوبة
2. أحلل طلبك وأحدد أفضل حل
3. أنشئ workflow مخصص وأرسله كملف JSON
4. تستورد الملف مباشرة في n8n

**أمثلة للطلبات:**
• "عند ملء نموذج الاتصال، احفظ البيانات في Google Sheets وأرسل email ترحيب"
• "كل يوم الساعة 9 صباحاً، اجلب تقرير المبيعات وأرسله للفريق عبر Slack"
• "عند إضافة منتج جديد في المتجر، أشعر القناة المخصصة"

**الأوامر:**
/help - دليل الاستخدام التفصيلي
/test - اختبار الاتصال بـ Gemini
/templates - عرض القوالب المتاحة
/status - حالة النظام

**حالة AI:** {'✅ Gemini متصل' if GEMINI_API_KEY else '❌ غير متوفر'}

ابدأ بوصف الأتمتة التي تريدها!"""
                await send_message(chat_id, welcome_msg)
                
            elif text.startswith("/test"):
                await send_message(chat_id, "🔍 جاري اختبار الاتصال بـ Gemini...")
                
                if AI_SYSTEM_AVAILABLE:
                    test_result = await test_gemini_connection()
                    if test_result["success"]:
                        await send_message(chat_id, 
                            f"✅ **اختبار ناجح!**\n\n"
                            f"**النموذج:** {test_result.get('model', 'غير محدد')}\n"
                            f"**الاستجابة:** {test_result['response'][:200]}"
                        )
                    else:
                        await send_message(chat_id,
                            f"❌ **اختبار فاشل!**\n\n"
                            f"**الخطأ:** {test_result['error']}"
                        )
                else:
                    await send_message(chat_id, "❌ نظام AI غير متوفر")
                    
            elif text.startswith("/templates"):
                if AI_SYSTEM_AVAILABLE:
                    templates = get_available_templates()
                    template_list = "\n".join([f"• **{name}**: {desc}" for name, desc in templates.items()])
                    
                    await send_message(chat_id, 
                        f"📋 **القوالب المتاحة:**\n\n{template_list}\n\n"
                        f"هذه القوالب تُستخدم كأساس لإنشاء workflows مخصصة حسب طلبك."
                    )
                else:
                    await send_message(chat_id, "❌ النظام غير متوفر لعرض القوالب")
                    
            elif text.startswith("/help"):
                help_msg = """📚 **دليل الاستخدام الشامل**

**كيفية كتابة طلب ممتاز:**

**1. حدد المشغل (Trigger):**
• "عند ملء نموذج..." → Webhook
• "كل يوم/ساعة..." → Schedule  
• "عند إضافة..." → Webhook/Database

**2. حدد البيانات:**
• ما المعلومات المطلوبة؟
• من أين تأتي؟
• كيف يجب معالجتها؟

**3. حدد الإجراءات:**
• حفظ في Google Sheets
• إرسال email عبر Gmail
• إشعار في Slack
• استدعاء API خارجي

**أمثلة ممتازة:**
✅ "عندما يرسل عميل نموذج طلب خدمة، احفظ بياناته (الاسم، الإيميل، نوع الخدمة) في جدول Google Sheets واسمه 'العملاء الجدد'، ثم أرسل له رسالة ترحيب عبر Gmail تتضمن رقم الطلب"

✅ "كل يوم الساعة 8 صباحاً، اجلب عدد الطلبات الجديدة من API المتجر، وأرسل تقرير مختصر للقناة #sales في Slack"

**تجنب هذه الأخطاء:**
❌ "أريد أتمتة" (غامض جداً)
❌ "أتمتة الإيميلات" (غير محدد)

**بعد الحصول على الملف:**
1. حمّل الملف .json
2. في n8n: Import → From file  
3. ارفع الملف
4. اضبط Credentials للخدمات
5. تعيين Environment Variables
6. اختبار ثم تفعيل

**للمساعدة التقنية:**
/status - حالة النظام
/test - اختبار AI  
/templates - القوالب المتاحة"""
                
                await send_message(chat_id, help_msg)
                
            elif text.startswith("/status"):
                status_info = f"""📊 **حالة النظام**

**Gemini AI:**
• الحالة: {'✅ متصل' if GEMINI_API_KEY else '❌ غير مُعرف'}  
• النموذج: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}

**Telegram Bot:**
• البوت: {'✅ نشط' if TELEGRAM_BOT_TOKEN else '❌ غير مُعرف'}
• Webhook: {os.getenv('RENDER_EXTERNAL_URL', 'غير محدد')}

**النظام:**
• AI System: {'✅ متوفر' if AI_SYSTEM_AVAILABLE else '❌ غير متوفر'}
• وقت التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**للحصول على Gemini API Key:**
1. اذهب إلى https://makersuite.google.com/app/apikey
2. أنشئ مفتاح جديد
3. اضبطه في متغيرات البيئة: GEMINI_API_KEY"""
                
                await send_message(chat_id, status_info)
                
            elif text.startswith("/"):
                await send_message(chat_id, "❓ أمر غير معروف. أرسل /help للمساعدة.")
            else:
                # معالجة طلب الأتمتة
                await handle_text_message(chat_id, text)
        else:
            await send_message(chat_id, "📝 أرسل لي وصفاً نصياً للأتمتة المطلوبة")
        
    except Exception as e:
        print(f"[ERROR] handle_update failed: {e}")
        try:
            if "message" in update and "chat" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                await send_message(chat_id, "❌ حدث خطأ تقني. جرب مرة أخرى.")
        except:
            pass

# FastAPI endpoints
@app.get("/")
async def root():
    return {
        "ok": True, 
        "service": "AI n8n Automation Bot",
        "ai_system": AI_SYSTEM_AVAILABLE,
        "gemini_configured": bool(GEMINI_API_KEY)
    }

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        print(f"[INFO] Received webhook update")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        asyncio.create_task(handle_update(update))
    except Exception as e:
        print(f"[ERROR] Failed to create task: {e}")
    
    return JSONResponse({"ok": True})

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
    """معلومات البوت والحالة التفصيلية"""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not configured"}
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            bot_response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
            webhook_response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo")
            
            # اختبار Gemini إذا كان متاحاً
            gemini_status = {"configured": bool(GEMINI_API_KEY), "working": False}
            if GEMINI_API_KEY and AI_SYSTEM_AVAILABLE:
                try:
                    test_result = await test_gemini_connection()
                    gemini_status["working"] = test_result["success"]
                    if not test_result["success"]:
                        gemini_status["error"] = test_result["error"]
                except Exception as e:
                    gemini_status["error"] = str(e)
            
            return {
                "bot": bot_response.json(),
                "webhook": webhook_response.json(), 
                "ai_system": {
                    "available": AI_SYSTEM_AVAILABLE,
                    "gemini": gemini_status,
                    "templates_count": len(get_available_templates()) if AI_SYSTEM_AVAILABLE else 0
                },
                "webhook_path": WEBHOOK_PATH,
                "environment": {
                    "render_url": os.getenv("RENDER_EXTERNAL_URL"),
                    "gemini_model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                }
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-gemini")
async def test_gemini_endpoint():
    """اختبار Gemini API عبر HTTP endpoint"""
    if not AI_SYSTEM_AVAILABLE:
        return {"success": False, "error": "AI system not available"}
    
    return await test_gemini_connection()

# Static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.isdir(static_dir):
    app.mount("/docs", StaticFiles(directory=static_dir, html=True), name="docs")
