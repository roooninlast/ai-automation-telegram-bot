import os, json, httpx
from typing import Dict, Any, Tuple, List
import copy
import uuid
from datetime import datetime

# إعدادات Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# قوالب n8n محدثة ومتوافقة 100% مع الإصدارات الحديثة
N8N_TEMPLATES = {
    "webhook_to_sheets": {
        "active": True,
        "connections": {
            "webhook_node": {
                "main": [
                    [
                        {
                            "node": "sheets_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "sheets_node": {
                "main": [
                    [
                        {
                            "node": "respond_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
        "id": "1",
        "name": "Contact Form to Google Sheets",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "contact-form",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": "webhook_node",
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": "webhook_node"
            },
            {
                "parameters": {
                    "resource": "sheet",
                    "operation": "appendOrUpdate",
                    "documentId": {
                        "__rl": True,
                        "value": "={{$env.GOOGLE_SHEET_ID}}",
                        "mode": "id"
                    },
                    "sheetName": {
                        "__rl": True,
                        "value": "Sheet1",
                        "mode": "list"
                    },
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Phone": "={{ $json.phone || 'N/A' }}",
                            "Message": "={{ $json.message }}",
                            "Timestamp": "={{ new Date().toISOString() }}"
                        },
                        "matchingColumns": [],
                        "schema": []
                    },
                    "options": {}
                },
                "id": "sheets_node",
                "name": "Google Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "respondBody": "{\"success\": true, \"message\": \"Form submitted successfully\"}",
                    "options": {}
                },
                "id": "respond_node",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300]
            }
        ],
        "pinData": {},
        "settings": {
            "executionOrder": "v1"
        },
        "staticData": {},
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    },
    
    "webhook_sheets_email": {
        "active": True,
        "connections": {
            "webhook_node": {
                "main": [
                    [
                        {
                            "node": "sheets_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "sheets_node": {
                "main": [
                    [
                        {
                            "node": "email_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "email_node": {
                "main": [
                    [
                        {
                            "node": "respond_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
        "id": "1",
        "name": "Form with Email Notification",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "contact-form",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": "webhook_node",
                "name": "Form Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": "webhook_node"
            },
            {
                "parameters": {
                    "resource": "sheet",
                    "operation": "appendOrUpdate",
                    "documentId": {
                        "__rl": True,
                        "value": "={{$env.GOOGLE_SHEET_ID}}",
                        "mode": "id"
                    },
                    "sheetName": {
                        "__rl": True,
                        "value": "Contacts",
                        "mode": "list"
                    },
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Message": "={{ $json.message }}",
                            "Date": "={{ new Date().toISOString() }}"
                        },
                        "matchingColumns": [],
                        "schema": []
                    },
                    "options": {}
                },
                "id": "sheets_node",
                "name": "Save to Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "send",
                    "toEmail": "={{ $json.email }}",
                    "subject": "Thank you for contacting us!",
                    "emailType": "text",
                    "message": "Dear {{ $json.name }},\\n\\nThank you for your message. We will get back to you soon.\\n\\nBest regards,\\nYour Team",
                    "options": {}
                },
                "id": "email_node",
                "name": "Send Welcome Email",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "respondBody": "{\"success\": true, \"message\": \"Form submitted and email sent\"}",
                    "options": {}
                },
                "id": "respond_node",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 300]
            }
        ],
        "pinData": {},
        "settings": {
            "executionOrder": "v1"
        },
        "staticData": {},
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    },
    
    "schedule_report": {
        "active": True,
        "connections": {
            "cron_node": {
                "main": [
                    [
                        {
                            "node": "http_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "http_node": {
                "main": [
                    [
                        {
                            "node": "code_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "code_node": {
                "main": [
                    [
                        {
                            "node": "email_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
        "id": "1",
        "name": "Daily Report Scheduler",
        "nodes": [
            {
                "parameters": {
                    "rule": {
                        "interval": [
                            {
                                "field": "hour",
                                "value": 9
                            },
                            {
                                "field": "minute",
                                "value": 0
                            }
                        ]
                    }
                },
                "id": "cron_node",
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
                    "genericAuthType": "httpHeaderAuth",
                    "options": {}
                },
                "id": "http_node",
                "name": "Fetch Data",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "jsCode": "const data = $input.all();\\nconst summary = {\\n  total_records: data.length,\\n  processed_at: new Date().toISOString(),\\n  summary: data.slice(0, 3)\\n};\\nreturn [summary];",
                    "options": {}
                },
                "id": "code_node",
                "name": "Process Data",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "send",
                    "toEmail": "={{$env.REPORT_EMAIL}}",
                    "subject": "Daily Report - {{ new Date().toDateString() }}",
                    "emailType": "text",
                    "message": "Daily report summary:\\n\\nTotal records: {{ $json.total_records }}\\nProcessed at: {{ $json.processed_at }}",
                    "options": {}
                },
                "id": "email_node",
                "name": "Send Report",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [900, 300]
            }
        ],
        "pinData": {},
        "settings": {
            "executionOrder": "v1"
        },
        "staticData": {},
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    },
    
    "slack_notification": {
        "active": True,
        "connections": {
            "webhook_node": {
                "main": [
                    [
                        {
                            "node": "slack_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "slack_node": {
                "main": [
                    [
                        {
                            "node": "respond_node",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
        "id": "1",
        "name": "Webhook to Slack Notification",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "slack-notify",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": "webhook_node",
                "name": "Notification Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": "webhook_node"
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "post",
                    "channel": "={{$env.SLACK_CHANNEL}}",
                    "text": "New notification:\\n{{ $json.message }}\\nFrom: {{ $json.source || 'Unknown' }}\\nTime: {{ new Date().toLocaleString() }}",
                    "otherOptions": {}
                },
                "id": "slack_node",
                "name": "Send to Slack",
                "type": "n8n-nodes-base.slack",
                "typeVersion": 2,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "respondBody": "{\"success\": true, \"message\": \"Notification sent to Slack\"}",
                    "options": {}
                },
                "id": "respond_node",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300]
            }
        ],
        "pinData": {},
        "settings": {
            "executionOrder": "v1"
        },
        "staticData": {},
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    }
}

# System prompts محسنة
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

SYS_WORKFLOW_CUSTOMIZER = """أنت مطور workflows خبير في n8n. مهمتك تخصيص workflow ليناسب طلب المستخدم.

قواعد التخصيص:
1. اختر القالب الأنسب من: webhook_to_sheets, webhook_sheets_email, schedule_report, slack_notification
2. عدّل اسم الـ workflow ليكون وصفياً ومناسباً للطلب
3. لا تعدّل بنية JSON الأساسية - فقط الاسم والوصف

أجب بالتنسيق التالي فقط:
TEMPLATE: [اسم القالب]
WORKFLOW_NAME: [اسم مخصص للـ workflow]"""

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
            "maxOutputTokens": 2000,
            "topP": 0.8,
            "topK": 40
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code != 200:
                print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")
                raise RuntimeError(f"Gemini API returned {response.status_code}")
            
            data = response.json()
            
            if not data.get("candidates") or not data["candidates"][0].get("content"):
                print(f"[ERROR] Invalid Gemini response: {data}")
                raise RuntimeError("No valid response from Gemini")
            
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return content.strip()
            
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")
        raise RuntimeError(f"Gemini API call failed: {str(e)}")

def analyze_user_request_locally(user_prompt: str) -> Dict[str, str]:
    """تحليل محلي دقيق لطلب المستخدم"""
    prompt_lower = user_prompt.lower()
    
    # تحديد نوع التشغيل
    if any(word in prompt_lower for word in ["form", "submit", "webhook", "receive", "post"]):
        trigger = "webhook"
    elif any(word in prompt_lower for word in ["daily", "schedule", "cron", "every", "automatically", "time"]):
        trigger = "schedule"
    else:
        trigger = "webhook"
    
    # تحديد الخدمات
    services = []
    if any(word in prompt_lower for word in ["google sheets", "spreadsheet", "sheet", "جدول"]):
        services.append("sheets")
    if any(word in prompt_lower for word in ["gmail", "email", "mail", "إيميل", "رسالة"]):
        services.append("email")
    if any(word in prompt_lower for word in ["slack", "سلاك"]):
        services.append("slack")
    
    # اختيار القالب المناسب
    if "sheets" in services and "email" in services:
        template = "webhook_sheets_email"
        workflow_name = "Form Submission with Email & Sheets"
    elif "sheets" in services:
        template = "webhook_to_sheets"
        workflow_name = "Contact Form to Google Sheets"
    elif "slack" in services:
        template = "slack_notification"
        workflow_name = "Slack Notification System"
    elif trigger == "schedule":
        template = "schedule_report"
        workflow_name = "Automated Daily Report"
    else:
        template = "webhook_to_sheets"
        workflow_name = "Basic Webhook Automation"
    
    return {
        "trigger": trigger,
        "services": ", ".join(services) if services else "basic",
        "template": template,
        "workflow_name": workflow_name,
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
        local_analysis = analyze_user_request_locally(user_prompt)
        
        detailed_plan = f"""🔍 **تحليل طلب الأتمتة:**

**التحليل بواسطة Gemini AI:**
{analysis}

**التحليل المحلي:**
- المشغل: {local_analysis['trigger']}
- الخدمات: {local_analysis['services']}
- القالب المقترح: {local_analysis['template']}
- اسم الـ Workflow: {local_analysis['workflow_name']}

**طلب المستخدم الأصلي:**
{user_prompt}
"""
        
        return detailed_plan, True
        
    except Exception as e:
        print(f"[WARNING] AI analysis failed: {e}")
        
        # تحليل احتياطي محلي
        local_analysis = analyze_user_request_locally(user_prompt)
        fallback_plan = f"""📋 **تحليل محلي (Gemini غير متاح):**

- نوع المشغل: {local_analysis['trigger']}
- الخدمات: {local_analysis['services']}
- القالب المقترح: {local_analysis['template']}
- اسم الـ Workflow: {local_analysis['workflow_name']}

**طلب المستخدم:**
{user_prompt}
"""
        
        return fallback_plan, False

def customize_workflow_name(template: Dict[str, Any], custom_name: str) -> Dict[str, Any]:
    """تخصيص اسم الـ workflow وتحديث التواريخ"""
    customized = copy.deepcopy(template)
    customized["name"] = custom_name
    customized["updatedAt"] = datetime.now().isoformat()
    
    # إنشاء معرفات جديدة للعقد
    node_id_mapping = {}
    for node in customized["nodes"]:
        old_id = node["id"]
        new_id = str(uuid.uuid4())[:8]
        node_id_mapping[old_id] = new_id
        node["id"] = new_id
        
        # تحديث webhookId إذا كان موجوداً
        if "webhookId" in node:
            node["webhookId"] = new_id
    
    # تحديث الاتصالات بالمعرفات الجديدة
    new_connections = {}
    for source_id, connections in customized["connections"].items():
        new_source_id = node_id_mapping.get(source_id, source_id)
        new_connection_data = {"main": []}
        
        for connection_list in connections["main"]:
            new_connection_list = []
            for connection in connection_list:
                old_target = connection["node"]
                new_target = node_id_mapping.get(old_target, old_target)
                new_connection_list.append({
                    "node": new_target,
                    "type": connection["type"],
                    "index": connection["index"]
                })
            new_connection_data["main"].append(new_connection_list)
        
        new_connections[new_source_id] = new_connection_data
    
    customized["connections"] = new_connections
    return customized

async def draft_n8n_json_with_ai(plan: str) -> Tuple[str, bool]:
    """إنشاء workflow n8n متوافق 100% مع النظام"""
    try:
        # استخراج القالب من الخطة
        template_name = "webhook_to_sheets"
        workflow_name = "Generated Workflow"
        
        # البحث عن القالب في الخطة
        for template_key in ["webhook_sheets_email", "schedule_report", "slack_notification", "webhook_to_sheets"]:
            if template_key in plan.lower():
                template_name = template_key
                break
        
        # تخصيص اسم الـ workflow باستخدام Gemini إذا كان متاحاً
        if GEMINI_API_KEY:
            try:
                customization_prompt = f"""
قم بتخصيص هذا الـ workflow بناءً على الخطة:

{plan}

اختر القالب الأنسب وأعطه اسماً وصفياً باللغة الإنجليزية.
"""
                
                customization = await _call_gemini_api(customization_prompt, SYS_WORKFLOW_CUSTOMIZER)
                
                # استخراج المعلومات من الاستجابة
                lines = customization.strip().split('\n')
                for line in lines:
                    if line.startswith("TEMPLATE:"):
                        suggested_template = line.split(":", 1)[1].strip()
                        if suggested_template in ["webhook_to_sheets", "webhook_sheets_email", "schedule_report", "slack_notification"]:
                            template_name = suggested_template
                    elif line.startswith("WORKFLOW_NAME:"):
                        workflow_name = line.split(":", 1)[1].strip()
                
                print(f"[SUCCESS] AI customization: template={template_name}, name={workflow_name}")
                        
            except Exception as e:
                print(f"[WARNING] AI customization failed: {e}")
        
        # استخراج اسم من التحليل المحلي كاحتياط
        if "اسم الـ Workflow:" in plan:
            try:
                workflow_name = plan.split("اسم الـ Workflow:")[1].split("\n")[0].strip()
            except:
                pass
        
        print(f"[INFO] Building workflow: template={template_name}, name={workflow_name}")
        
        # الحصول على القالب وتخصيصه
        base_template = N8N_TEMPLATES[template_name]
        customized_workflow = customize_workflow_name(base_template, workflow_name)
        
        print("[SUCCESS] Generated valid n8n workflow")
        return json.dumps(customized_workflow, ensure_ascii=False, indent=2), True
        
    except Exception as e:
        print(f"[ERROR] Workflow generation failed: {e}")
        
        # إنشاء workflow احتياطي
        fallback_template = N8N_TEMPLATES["webhook_to_sheets"]
        fallback_workflow = customize_workflow_name(fallback_template, "Basic Automation Workflow")
        return json.dumps(fallback_workflow, ensure_ascii=False, indent=2), False

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
    """الحصول على قائمة القوالب المتاحة مع أوصافها"""
    return {
        "webhook_to_sheets": "Contact form to Google Sheets - Basic form data collection",
        "webhook_sheets_email": "Form with email notification - Saves to sheets and sends welcome email", 
        "schedule_report": "Daily automated report - Fetches data and emails summary",
        "slack_notification": "Webhook to Slack - Sends notifications to Slack channel"
    }
