import os, json, httpx
from typing import Dict, Any, Tuple, List
import copy
import uuid
from datetime import datetime

# إعدادات Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def generate_node_id() -> str:
    """إنشاء معرف فريد للعقدة متوافق مع n8n"""
    return str(uuid.uuid4())

def generate_webhook_id() -> str:
    """إنشاء معرف webhook فريد"""
    return str(uuid.uuid4())

# قوالب n8n موثوقة ومتوافقة 100%
N8N_TEMPLATES = {
    "webhook_to_sheets": {
        "active": True,
        "connections": {},  # سيتم ملؤها ديناميكياً
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
        "id": "1",
        "name": "Contact Form to Google Sheets",
        "nodes": [],  # سيتم ملؤها ديناميكياً
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

def create_webhook_node(node_id: str, webhook_id: str, path: str = "contact-form") -> Dict[str, Any]:
    """إنشاء عقدة webhook صحيحة"""
    return {
        "parameters": {
            "httpMethod": "POST",
            "path": path,
            "responseMode": "onReceived",
            "options": {}
        },
        "id": node_id,
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [240, 300],
        "webhookId": webhook_id
    }

def create_google_sheets_node(node_id: str) -> Dict[str, Any]:
    """إنشاء عقدة Google Sheets صحيحة"""
    return {
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
        "id": node_id,
        "name": "Google Sheets",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4,
        "position": [460, 300]
    }

def create_gmail_node(node_id: str) -> Dict[str, Any]:
    """إنشاء عقدة Gmail صحيحة"""
    return {
        "parameters": {
            "resource": "message",
            "operation": "send",
            "toEmail": "={{ $json.email }}",
            "subject": "Thank you for contacting us!",
            "emailType": "text",
            "message": "Dear {{ $json.name }},\n\nThank you for your message. We have received your inquiry and will get back to you soon.\n\nBest regards,\nYour Team",
            "options": {}
        },
        "id": node_id,
        "name": "Gmail",
        "type": "n8n-nodes-base.gmail",
        "typeVersion": 2,
        "position": [680, 300]
    }

def create_slack_node(node_id: str) -> Dict[str, Any]:
    """إنشاء عقدة Slack صحيحة"""
    return {
        "parameters": {
            "resource": "message",
            "operation": "post",
            "channel": "={{$env.SLACK_CHANNEL}}",
            "text": "New contact form submission:\n• Name: {{ $json.name }}\n• Email: {{ $json.email }}\n• Message: {{ $json.message }}\n• Time: {{ new Date().toLocaleString() }}",
            "otherOptions": {}
        },
        "id": node_id,
        "name": "Slack",
        "type": "n8n-nodes-base.slack",
        "typeVersion": 2,
        "position": [900, 300]
    }

def create_cron_node(node_id: str, hour: int = 9, minute: int = 0) -> Dict[str, Any]:
    """إنشاء عقدة cron صحيحة"""
    return {
        "parameters": {
            "rule": {
                "interval": [
                    {
                        "field": "hour",
                        "value": hour
                    },
                    {
                        "field": "minute", 
                        "value": minute
                    }
                ]
            }
        },
        "id": node_id,
        "name": "Schedule Trigger",
        "type": "n8n-nodes-base.cron",
        "typeVersion": 1,
        "position": [240, 300]
    }

def create_http_request_node(node_id: str) -> Dict[str, Any]:
    """إنشاء عقدة HTTP Request صحيحة"""
    return {
        "parameters": {
            "method": "GET",
            "url": "={{$env.API_ENDPOINT}}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "id": node_id,
        "name": "HTTP Request",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": [460, 300]
    }

def create_code_node(node_id: str, code: str) -> Dict[str, Any]:
    """إنشاء عقدة Code صحيحة"""
    return {
        "parameters": {
            "jsCode": code,
            "options": {}
        },
        "id": node_id,
        "name": "Code",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [680, 300]
    }

def create_respond_webhook_node(node_id: str) -> Dict[str, Any]:
    """إنشاء عقدة Respond to Webhook صحيحة"""
    return {
        "parameters": {
            "respondBody": JSON.stringify({
                "success": True,
                "message": "Request processed successfully",
                "timestamp": "{{ new Date().toISOString() }}"
            }),
            "options": {}
        },
        "id": node_id,
        "name": "Respond to Webhook",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1,
        "position": [1120, 300]
    }

def create_connections(node_ids: List[str]) -> Dict[str, Any]:
    """إنشاء اتصالات صحيحة بين العقد"""
    connections = {}
    
    for i in range(len(node_ids) - 1):
        source_id = node_ids[i]
        target_id = node_ids[i + 1]
        
        connections[source_id] = {
            "main": [
                [
                    {
                        "node": target_id,
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    
    return connections

def build_complete_workflow(template_name: str, custom_name: str = None) -> Dict[str, Any]:
    """بناء workflow كامل ومتوافق مع n8n"""
    
    # نسخة أساسية من القالب
    workflow = copy.deepcopy(N8N_TEMPLATES["webhook_to_sheets"])
    
    # تحديث الاسم
    if custom_name:
        workflow["name"] = custom_name
    
    # تحديث التواريخ
    now = datetime.now().isoformat()
    workflow["updatedAt"] = now
    
    # إنشاء معرفات فريدة
    webhook_id = generate_webhook_id()
    node_ids = [generate_node_id() for _ in range(4)]  # 4 عقد أساسية
    
    if template_name == "webhook_to_sheets":
        # بناء العقد
        nodes = [
            create_webhook_node(node_ids[0], webhook_id),
            create_google_sheets_node(node_ids[1]),
            create_respond_webhook_node(node_ids[2])
        ]
        used_node_ids = node_ids[:3]
        
    elif template_name == "webhook_sheets_email":
        nodes = [
            create_webhook_node(node_ids[0], webhook_id),
            create_google_sheets_node(node_ids[1]),
            create_gmail_node(node_ids[2]),
            create_respond_webhook_node(node_ids[3])
        ]
        used_node_ids = node_ids[:4]
        
    elif template_name == "schedule_report":
        code = """const data = $input.all();
const summary = {
  total_records: data.length,
  processed_at: new Date().toISOString(),
  sample_data: data.slice(0, 3)
};
return [summary];"""
        
        nodes = [
            create_cron_node(node_ids[0]),
            create_http_request_node(node_ids[1]),
            create_code_node(node_ids[2], code),
            create_gmail_node(node_ids[3])
        ]
        used_node_ids = node_ids[:4]
        
    elif template_name == "slack_notification":
        nodes = [
            create_webhook_node(node_ids[0], webhook_id, "slack-notify"),
            create_slack_node(node_ids[1]),
            create_respond_webhook_node(node_ids[2])
        ]
        used_node_ids = node_ids[:3]
        
    else:
        # fallback للقالب الأساسي
        nodes = [
            create_webhook_node(node_ids[0], webhook_id),
            create_respond_webhook_node(node_ids[1])
        ]
        used_node_ids = node_ids[:2]
    
    # إضافة العقد للـ workflow
    workflow["nodes"] = nodes
    
    # إنشاء الاتصالات
    workflow["connections"] = create_connections(used_node_ids)
    
    # تحديث عدد المشغلات
    trigger_count = sum(1 for node in nodes if node["type"] in [
        "n8n-nodes-base.webhook", 
        "n8n-nodes-base.cron", 
        "n8n-nodes-base.manualTrigger"
    ])
    workflow["triggerCount"] = trigger_count
    
    return workflow

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
        
        # بناء الـ workflow الكامل
        workflow = build_complete_workflow(template_name, workflow_name)
        
        # التحقق من صحة البنية
        if validate_workflow_structure(workflow):
            print("[SUCCESS] Generated valid n8n workflow")
            return json.dumps(workflow, ensure_ascii=False, indent=2), True
        else:
            print("[WARNING] Workflow validation failed, using fallback")
            raise ValueError("Invalid workflow structure")
        
    except Exception as e:
        print(f"[ERROR] Workflow generation failed: {e}")
        
        # إنشاء workflow احتياطي أساسي
        fallback_workflow = build_complete_workflow("webhook_to_sheets", "Basic Automation Workflow")
        return json.dumps(fallback_workflow, ensure_ascii=False, indent=2), False

def validate_workflow_structure(workflow: Dict[str, Any]) -> bool:
    """التحقق من صحة بنية الـ workflow"""
    required_fields = ["name", "nodes", "connections", "active", "createdAt", "updatedAt", "id", "versionId"]
    
    for field in required_fields:
        if field not in workflow:
            print(f"[ERROR] Missing required field: {field}")
            return False
    
    # التحقق من العقد
    if not isinstance(workflow["nodes"], list) or len(workflow["nodes"]) == 0:
        print("[ERROR] Invalid nodes structure")
        return False
    
    # التحقق من معرفات العقد
    node_ids = set()
    for node in workflow["nodes"]:
        if "id" not in node or not node["id"]:
            print("[ERROR] Node missing ID")
            return False
        if node["id"] in node_ids:
            print(f"[ERROR] Duplicate node ID: {node['id']}")
            return False
        node_ids.add(node["id"])
    
    # التحقق من الاتصالات
    for source_id, connections in workflow["connections"].items():
        if source_id not in node_ids:
            print(f"[ERROR] Connection source not found: {source_id}")
            return False
        
        for connection_list in connections.get("main", []):
            for connection in connection_list:
                target_id = connection.get("node")
                if target_id not in node_ids:
                    print(f"[ERROR] Connection target not found: {target_id}")
                    return False
    
    print("[SUCCESS] Workflow structure validation passed")
    return True

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
