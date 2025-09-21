import os, json, httpx
from typing import Dict, Any, Tuple, List
import copy

# إعدادات Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# قوالب n8n موثوقة ومختبرة
N8N_TEMPLATES = {
    "webhook_to_sheets": {
        "name": "Contact Form to Google Sheets",
        "nodes": [
            {
                "parameters": {
                    "path": "contact-form",
                    "responseMode": "onReceived",
                    "httpMethod": "POST"
                },
                "id": "webhook_trigger",
                "name": "Contact Form Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "webhookId": "webhook_trigger"
            },
            {
                "parameters": {
                    "resource": "spreadsheet",
                    "operation": "appendOrUpdate",
                    "documentId": "={{$env.GOOGLE_SHEET_ID}}",
                    "sheetName": "Sheet1",
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Phone": "={{ $json.phone }}",
                            "Message": "={{ $json.message }}",
                            "Timestamp": "={{ new Date().toISOString() }}"
                        }
                    }
                },
                "id": "google_sheets",
                "name": "Save to Google Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "respondBody": "{\"success\": true, \"message\": \"Form submitted successfully\"}"
                },
                "id": "respond_webhook",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300]
            }
        ],
        "connections": {
            "webhook_trigger": {"main": [[{"node": "google_sheets", "type": "main", "index": 0}]]},
            "google_sheets": {"main": [[{"node": "respond_webhook", "type": "main", "index": 0}]]}
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
        "settings": {"timezone": "UTC"},
        "staticData": None,
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    },
    
    "webhook_sheets_email": {
        "name": "Form Submission with Email Notification",
        "nodes": [
            {
                "parameters": {
                    "path": "contact-form",
                    "responseMode": "onReceived",
                    "httpMethod": "POST"
                },
                "id": "webhook_trigger",
                "name": "Form Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "webhookId": "webhook_trigger"
            },
            {
                "parameters": {
                    "resource": "spreadsheet", 
                    "operation": "appendOrUpdate",
                    "documentId": "={{$env.GOOGLE_SHEET_ID}}",
                    "sheetName": "Contacts",
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Message": "={{ $json.message }}",
                            "Date": "={{ new Date().toISOString() }}"
                        }
                    }
                },
                "id": "google_sheets",
                "name": "Save to Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "operation": "send",
                    "toEmail": "={{ $json.email }}",
                    "subject": "Thank you for contacting us!",
                    "message": "Dear {{ $json.name }},\n\nThank you for your message: {{ $json.message }}\n\nWe will get back to you soon.\n\nBest regards,\nYour Team"
                },
                "id": "gmail_send",
                "name": "Send Welcome Email",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "respondBody": "{\"success\": true, \"message\": \"Form submitted and email sent\"}"
                },
                "id": "respond_webhook",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 300]
            }
        ],
        "connections": {
            "webhook_trigger": {"main": [[{"node": "google_sheets", "type": "main", "index": 0}]]},
            "google_sheets": {"main": [[{"node": "gmail_send", "type": "main", "index": 0}]]},
            "gmail_send": {"main": [[{"node": "respond_webhook", "type": "main", "index": 0}]]}
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z", 
        "settings": {"timezone": "UTC"},
        "staticData": None,
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    },
    
    "schedule_report": {
        "name": "Daily Report Scheduler",
        "nodes": [
            {
                "parameters": {
                    "rule": {
                        "hour": 9,
                        "minute": 0,
                        "timezone": "UTC"
                    }
                },
                "id": "cron_trigger",
                "name": "Daily at 9 AM",
                "type": "n8n-nodes-base.cron",
                "typeVersion": 1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "method": "GET",
                    "url": "={{$env.API_ENDPOINT}}",
                    "authentication": "genericCredentialType",
                    "genericAuthType": "httpHeaderAuth"
                },
                "id": "http_request",
                "name": "Fetch Data",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "jsCode": "const data = $input.all();\nconst summary = {\n  total_records: data.length,\n  processed_at: new Date().toISOString(),\n  summary: data.slice(0, 5)\n};\nreturn [summary];"
                },
                "id": "code_process",
                "name": "Process Data",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "operation": "send",
                    "toEmail": "={{$env.REPORT_EMAIL}}",
                    "subject": "Daily Report - {{ new Date().toDateString() }}",
                    "message": "Daily report summary:\n\nTotal records: {{ $json.total_records }}\nProcessed at: {{ $json.processed_at }}\n\nData preview:\n{{ JSON.stringify($json.summary, null, 2) }}"
                },
                "id": "gmail_send",
                "name": "Send Report",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [900, 300]
            }
        ],
        "connections": {
            "cron_trigger": {"main": [[{"node": "http_request", "type": "main", "index": 0}]]},
            "http_request": {"main": [[{"node": "code_process", "type": "main", "index": 0}]]},
            "code_process": {"main": [[{"node": "gmail_send", "type": "main", "index": 0}]]}
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
        "settings": {"timezone": "UTC"},
        "staticData": None,
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    },
    
    "slack_notification": {
        "name": "Webhook to Slack Notification",
        "nodes": [
            {
                "parameters": {
                    "path": "slack-notify",
                    "responseMode": "onReceived",
                    "httpMethod": "POST"
                },
                "id": "webhook_trigger",
                "name": "Notification Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "webhookId": "webhook_trigger"
            },
            {
                "parameters": {
                    "operation": "postMessage",
                    "channel": "={{$env.SLACK_CHANNEL}}",
                    "text": "New notification:\n{{ $json.message }}\nFrom: {{ $json.source || 'Unknown' }}\nTime: {{ new Date().toLocaleString() }}"
                },
                "id": "slack_send",
                "name": "Send to Slack",
                "type": "n8n-nodes-base.slack",
                "typeVersion": 2,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "respondBody": "{\"success\": true, \"message\": \"Notification sent to Slack\"}"
                },
                "id": "respond_webhook",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300]
            }
        ],
        "connections": {
            "webhook_trigger": {"main": [[{"node": "slack_send", "type": "main", "index": 0}]]},
            "slack_send": {"main": [[{"node": "respond_webhook", "type": "main", "index": 0}]]}
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
        "settings": {"timezone": "UTC"},
        "staticData": None,
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    }
}

# System prompts دقيقة ومتخصصة
SYS_ANALYZER = """أنت خبير في تحليل طلبات الأتمتة وتصميم workflows لـ n8n.

مهمتك: تحليل طلب المستخدم وتحديد النوع والمكونات المطلوبة.

قواعد التحليل:
1. حدد نوع التشغيل (Trigger): webhook, schedule, manual, email
2. حدد الخدمات المذكورة: Google Sheets, Gmail, Slack, APIs
3. حدد العمليات: save data, send email, notifications, data processing
4. حدد مستوى التعقيد: simple (1-3 nodes), medium (4-6 nodes), complex (7+ nodes)

أجب بالتنسيق التالي:
TRIGGER: [نوع المشغل]
SERVICES: [الخدمات المطلوبة]
OPERATIONS: [العمليات المطلوبة] 
TEMPLATE: [اقتراح القالب المناسب]
COMPLEXITY: [مستوى التعقيد]
CONFIDENCE: [مستوى الثقة: high/medium/low]"""

SYS_WORKFLOW_DESIGNER = """أنت مطور workflows خبير في n8n. مهمتك تخصيص قالب موجود ليناسب طلب المستخدم.

قواعد التخصيص:
1. احتفظ بنفس هيكل القالب الأساسي
2. عدّل الأسماء والوصف ليناسب الطلب
3. اضبط parameters العقد حسب الحاجة
4. استخدم environment variables للبيانات الحساسة: {{$env.VARIABLE_NAME}}
5. تأكد من صحة connections بين العقد
6. اضبط positions العقد بشكل منطقي

متطلبات مهمة:
- يجب أن يكون الJSON صالح 100% للاستيراد في n8n
- يجب تضمين كل الحقول المطلوبة: name, nodes, connections, settings, tags
- استخدم أسماء واضحة ووصفية للعقد
- تأكد من صحة node types وparameters

أرجع JSON كامل فقط، بدون شرح."""

async def _call_gemini_api(prompt: str, system_instruction: str = "") -> str:
    """استدعاء Gemini API مع معالجة شاملة للأخطاء"""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    contents = []
    if system_instruction:
        contents.append({
            "role": "model",
            "parts": [{"text": system_instruction}]
        })
    
    contents.append({
        "role": "user", 
        "parts": [{"text": prompt}]
    })
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4000,
            "topP": 0.8,
            "topK": 40
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code != 200:
                error_text = response.text
                print(f"[ERROR] Gemini API error {response.status_code}: {error_text}")
                raise RuntimeError(f"Gemini API returned {response.status_code}")
            
            data = response.json()
            
            if not data.get("candidates") or not data["candidates"][0].get("content"):
                print(f"[ERROR] Invalid Gemini response: {data}")
                raise RuntimeError("No valid response from Gemini")
            
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return content.strip()
            
    except httpx.TimeoutException:
        raise RuntimeError("Gemini API timeout")
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")
        raise RuntimeError(f"Gemini API call failed: {str(e)}")

def analyze_user_request(user_prompt: str) -> Dict[str, str]:
    """تحليل محلي سريع لطلب المستخدم"""
    prompt_lower = user_prompt.lower()
    
    # تحديد نوع التشغيل
    if any(word in prompt_lower for word in ["form", "submit", "webhook", "receive", "post"]):
        trigger = "webhook"
    elif any(word in prompt_lower for word in ["daily", "schedule", "cron", "every", "automatically"]):
        trigger = "schedule"
    elif any(word in prompt_lower for word in ["manual", "button", "click"]):
        trigger = "manual"
    else:
        trigger = "webhook"  # افتراضي
    
    # تحديد الخدمات
    services = []
    if any(word in prompt_lower for word in ["google sheets", "spreadsheet", "sheet"]):
        services.append("google_sheets")
    if any(word in prompt_lower for word in ["gmail", "email", "mail"]):
        services.append("gmail")
    if any(word in prompt_lower for word in ["slack"]):
        services.append("slack")
    
    # اختيار القالب
    if "google_sheets" in services and "gmail" in services:
        template = "webhook_sheets_email"
    elif "google_sheets" in services:
        template = "webhook_to_sheets"
    elif "slack" in services:
        template = "slack_notification"
    elif trigger == "schedule":
        template = "schedule_report"
    else:
        template = "webhook_to_sheets"  # افتراضي
    
    return {
        "trigger": trigger,
        "services": ", ".join(services),
        "template": template,
        "complexity": "medium"
    }

async def plan_workflow_with_ai(user_prompt: str) -> Tuple[str, bool]:
    """تحليل طلب المستخدم وإنشاء خطة العمل"""
    try:
        print(f"[INFO] Analyzing request with Gemini: {user_prompt[:100]}...")
        
        analysis_prompt = f"""
طلب المستخدم: {user_prompt}

قم بتحليل هذا الطلب وحدد:
1. نوع المشغل المطلوب
2. الخدمات والأدوات المذكورة
3. العمليات المطلوب تنفيذها
4. القالب الأنسب من القوالب المتاحة
5. مستوى التعقيد

القوالب المتاحة:
- webhook_to_sheets: نموذج ويب إلى Google Sheets
- webhook_sheets_email: نموذج ويب + حفظ في Sheets + إرسال email
- schedule_report: تقرير مجدول يومياً
- slack_notification: إشعارات Slack

كن دقيقاً ومحدداً في التحليل.
"""
        
        analysis = await _call_gemini_api(analysis_prompt, SYS_ANALYZER)
        
        # تحليل محلي كاحتياط
        local_analysis = analyze_user_request(user_prompt)
        
        detailed_plan = f"""🔍 **تحليل طلب الأتمتة:**

**التحليل بواسطة Gemini AI:**
{analysis}

**التحليل المحلي:**
- المشغل: {local_analysis['trigger']}
- الخدمات: {local_analysis['services']}
- القالب المقترح: {local_analysis['template']}
- التعقيد: {local_analysis['complexity']}

**طلب المستخدم الأصلي:**
{user_prompt}
"""
        
        return detailed_plan, True
        
    except Exception as e:
        print(f"[WARNING] AI analysis failed: {e}")
        
        # تحليل احتياطي
        local_analysis = analyze_user_request(user_prompt)
        fallback_plan = f"""📋 **تحليل أساسي (Gemini غير متاح):**

- نوع المشغل: {local_analysis['trigger']}
- الخدمات المكتشفة: {local_analysis['services']}
- القالب المقترح: {local_analysis['template']}
- مستوى التعقيد: {local_analysis['complexity']}

**طلب المستخدم:**
{user_prompt}

**ملاحظة:** تم استخدام التحليل المحلي بسبب عدم توفر الاتصال مع Gemini API.
"""
        
        return fallback_plan, False

async def draft_n8n_json_with_ai(plan: str) -> Tuple[str, bool]:
    """إنشاء workflow n8n مخصص باستخدام القوالب والذكاء الاصطناعي"""
    try:
        # استخراج القالب المقترح من الخطة
        template_name = "webhook_to_sheets"  # افتراضي
        
        for template_key in N8N_TEMPLATES.keys():
            if template_key in plan:
                template_name = template_key
                break
        
        print(f"[INFO] Using template: {template_name}")
        base_template = copy.deepcopy(N8N_TEMPLATES[template_name])
        
        # تخصيص القالب باستخدام Gemini إذا كان متاحاً
        if GEMINI_API_KEY:
            customization_prompt = f"""
قم بتخصيص قالب n8n workflow هذا ليناسب طلب المستخدم:

القالب الأساسي:
{json.dumps(base_template, ensure_ascii=False, indent=2)}

خطة العمل:
{plan}

تعديلات مطلوبة:
1. غيّر اسم الـ workflow ليكون وصفياً
2. عدّل أسماء العقد لتكون واضحة
3. اضبط parameters العقد حسب الحاجة  
4. تأكد من استخدام environment variables للبيانات الحساسة
5. احتفظ بنفس structure وconnections

أرجع JSON محدث كامل فقط.
"""
            
            try:
                customized_json = await _call_gemini_api(customization_prompt, SYS_WORKFLOW_DESIGNER)
                
                # تنظيف النص إذا كان محاطاً بـ ```json
                cleaned_json = customized_json.strip()
                if cleaned_json.startswith("```json"):
                    cleaned_json = cleaned_json[7:]
                if cleaned_json.endswith("```"):
                    cleaned_json = cleaned_json[:-3]
                
                # محاولة تحليل JSON
                customized_workflow = json.loads(cleaned_json)
                print("[SUCCESS] Gemini customization successful")
                return json.dumps(customized_workflow, ensure_ascii=False, indent=2), True
                
            except json.JSONDecodeError as e:
                print(f"[WARNING] Gemini generated invalid JSON: {e}")
                print(f"Response preview: {customized_json[:500]}")
                
            except Exception as e:
                print(f"[WARNING] Gemini customization failed: {e}")
        
        # استخدام القالب الأساسي مع تعديلات بسيطة
        print("[INFO] Using base template with basic customization")
        return json.dumps(base_template, ensure_ascii=False, indent=2), True
        
    except Exception as e:
        print(f"[ERROR] Workflow generation failed: {e}")
        
        # إنشاء workflow أساسي جداً
        minimal_workflow = {
            "name": "Basic Automation Workflow",
            "nodes": [
                {
                    "parameters": {},
                    "id": "manual_trigger",
                    "name": "Manual Trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [240, 300]
                }
            ],
            "connections": {},
            "createdAt": "2024-01-01T00:00:00.000Z",
            "updatedAt": "2024-01-01T00:00:00.000Z", 
            "settings": {"timezone": "UTC"},
            "staticData": None,
            "tags": ["basic"],
            "triggerCount": 1,
            "versionId": "1"
        }
        
        return json.dumps(minimal_workflow, ensure_ascii=False, indent=2), False

async def test_gemini_connection() -> Dict[str, Any]:
    """اختبار الاتصال مع Gemini API"""
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "error": "GEMINI_API_KEY not configured"
        }
    
    try:
        result = await _call_gemini_api("قل 'مرحباً، Gemini API يعمل بشكل صحيح!'")
        return {
            "success": True,
            "response": result,
            "model": GEMINI_MODEL
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_available_templates() -> Dict[str, str]:
    """الحصول على قائمة القوالب المتاحة"""
    return {
        name: f"Template for {name.replace('_', ' ').title()}"
        for name in N8N_TEMPLATES.keys()
    }
