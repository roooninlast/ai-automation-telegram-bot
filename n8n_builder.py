# n8n_builder.py - محسن للنظام الجديد
from typing import Dict, Any, List
import uuid
import copy
from datetime import datetime

def validate_n8n_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """التحقق من صحة JSON وإصلاحه ليكون متوافق مع n8n"""
    if not isinstance(data, dict):
        return make_minimal_valid_n8n("Invalid Workflow")
    
    # نسخ البيانات
    workflow = copy.deepcopy(data)
    
    # الحقول الأساسية المطلوبة
    workflow.setdefault("active", True)
    workflow.setdefault("connections", {})
    workflow.setdefault("createdAt", datetime.now().isoformat())
    workflow["updatedAt"] = datetime.now().isoformat()
    workflow.setdefault("id", str(uuid.uuid4()))
    workflow.setdefault("name", "Generated Workflow")
    workflow.setdefault("nodes", [])
    workflow.setdefault("pinData", {})
    workflow.setdefault("settings", {"executionOrder": "v1"})
    workflow.setdefault("staticData", {})
    workflow.setdefault("tags", [])
    workflow.setdefault("triggerCount", 1)
    workflow.setdefault("versionId", "1")
    
    # التحقق من العقد
    if not workflow["nodes"]:
        return make_minimal_valid_n8n(workflow["name"])
    
    # إصلاح العقد مع تحسينات جديدة
    for node in workflow["nodes"]:
        enhance_node(node)
    
    # تحديث عدد المشغلات
    trigger_types = ["n8n-nodes-base.webhook", "n8n-nodes-base.cron", "n8n-nodes-base.manualTrigger"]
    trigger_count = sum(1 for node in workflow["nodes"] if node.get("type") in trigger_types)
    workflow["triggerCount"] = max(trigger_count, 1)
    
    # التحقق من الاتصالات
    validate_connections(workflow)
    
    return workflow

def enhance_node(node: Dict[str, Any]):
    """تحسين وإصلاح عقدة واحدة"""
    if not node.get("id"):
        node["id"] = str(uuid.uuid4())[:8]
    
    node.setdefault("parameters", {})
    node.setdefault("typeVersion", get_latest_type_version(node.get("type", "")))
    node.setdefault("position", [240, 300])
    
    if not node.get("name"):
        node["name"] = generate_node_name(node.get("type", ""))
    
    # تحسينات خاصة بنوع العقدة
    node_type = node.get("type", "").lower()
    
    if "webhook" in node_type:
        enhance_webhook_node(node)
    elif "googlesheets" in node_type:
        enhance_sheets_node(node)
    elif "gmail" in node_type:
        enhance_gmail_node(node)
    elif "set" in node_type:
        enhance_set_node(node)

def enhance_webhook_node(node: Dict[str, Any]):
    """تحسين عقدة Webhook"""
    params = node.setdefault("parameters", {})
    
    # إعدادات افتراضية محسنة
    params.setdefault("httpMethod", "POST")
    params.setdefault("path", "webhook")
    params.setdefault("responseMode", "onReceived")
    params.setdefault("options", {})
    
    # إضافة webhookId إذا لم يكن موجود
    if not node.get("webhookId"):
        node["webhookId"] = node["id"]

def enhance_sheets_node(node: Dict[str, Any]):
    """تحسين عقدة Google Sheets"""
    params = node.setdefault("parameters", {})
    
    # إعدادات افتراضية
    params.setdefault("resource", "sheet")
    params.setdefault("operation", "appendOrUpdate")
    
    # إعداد الجدول
    if not params.get("documentId"):
        params["documentId"] = {
            "__rl": True,
            "value": "={{$env.GOOGLE_SHEET_ID}}",
            "mode": "id"
        }
    
    if not params.get("sheetName"):
        params["sheetName"] = {
            "__rl": True,
            "value": "Sheet1",
            "mode": "list"
        }
    
    # التأكد من وجود إعداد الأعمدة
    if not params.get("columns"):
        params["columns"] = {
            "mappingMode": "defineBelow",
            "value": {
                "Name": "={{ $json.name }}",
                "Email": "={{ $json.email }}",
                "Message": "={{ $json.message }}",
                "Timestamp": "={{ new Date().toISOString() }}"
            },
            "matchingColumns": [],
            "schema": []
        }

def enhance_gmail_node(node: Dict[str, Any]):
    """تحسين عقدة Gmail"""
    params = node.setdefault("parameters", {})
    
    # إعدادات افتراضية
    params.setdefault("resource", "message")
    params.setdefault("operation", "send")
    params.setdefault("emailType", "text")
    
    # رسالة افتراضية محسنة
    if not params.get("message"):
        params["message"] = """عزيزي {{ $json.name || 'العميل' }},

شكراً لتواصلك معنا. تم استلام رسالتك بنجاح.

تفاصيل الطلب:
{{ $json.message }}

سيتم الرد عليك في أقرب وقت ممكن.

مع أطيب التحيات،
فريق الدعم"""

def enhance_set_node(node: Dict[str, Any]):
    """تحسين عقدة Set"""
    params = node.setdefault("parameters", {})
    
    if not params.get("values"):
        params["values"] = {
            "string": [
                {
                    "name": "processed_at",
                    "value": "={{ new Date().toISOString() }}"
                }
            ]
        }
    
    params.setdefault("options", {})

def get_latest_type_version(node_type: str) -> int:
    """الحصول على أحدث إصدار للعقدة"""
    version_mapping = {
        "n8n-nodes-base.webhook": 2,
        "n8n-nodes-base.googleSheets": 4,
        "n8n-nodes-base.gmail": 2,
        "n8n-nodes-base.set": 3,
        "n8n-nodes-base.cron": 1,
        "n8n-nodes-base.httpRequest": 4,
        "n8n-nodes-base.slack": 2,
        "n8n-nodes-base.respondToWebhook": 1,
        "n8n-nodes-base.code": 2,
        "n8n-nodes-base.if": 2
    }
    
    return version_mapping.get(node_type, 1)

def generate_node_name(node_type: str) -> str:
    """توليد اسم مناسب للعقدة"""
    name_mapping = {
        "n8n-nodes-base.webhook": "Webhook Trigger",
        "n8n-nodes-base.googleSheets": "Google Sheets",
        "n8n-nodes-base.gmail": "Gmail",
        "n8n-nodes-base.set": "Set Data",
        "n8n-nodes-base.cron": "Schedule Trigger",
        "n8n-nodes-base.httpRequest": "HTTP Request",
        "n8n-nodes-base.slack": "Slack",
        "n8n-nodes-base.respondToWebhook": "Respond",
        "n8n-nodes-base.code": "Code",
        "n8n-nodes-base.if": "IF Condition"
    }
    
    return name_mapping.get(node_type, "Node")

def validate_connections(workflow: Dict[str, Any]):
    """التحقق من صحة الاتصالات وإصلاحها"""
    nodes = workflow.get("nodes", [])
    connections = workflow.setdefault("connections", {})
    
    # إنشاء فهرس للعقد
    node_ids = {node["id"] for node in nodes}
    
    # تنظيف الاتصالات غير الصالحة
    valid_connections = {}
    for source_id, connection_data in connections.items():
        if source_id in node_ids:
            main_connections = connection_data.get("main", [])
            valid_main = []
            
            for connection_list in main_connections:
                valid_list = []
                for connection in connection_list:
                    target_node = connection.get("node")
                    if target_node in node_ids:
                        valid_list.append(connection)
                
                valid_main.append(valid_list)
            
            if valid_main and any(valid_main):
                valid_connections[source_id] = {"main": valid_main}
    
    workflow["connections"] = valid_connections

def make_minimal_valid_n8n(name: str, description: str = "") -> Dict[str, Any]:
    """إنشاء workflow أساسي صالح محسن"""
    webhook_id = str(uuid.uuid4())[:8]
    sheets_id = str(uuid.uuid4())[:8]
    
    return {
        "active": True,
        "connections": {
            webhook_id: {
                "main": [[{"node": sheets_id, "type": "main", "index": 0}]]
            }
        },
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "id": str(uuid.uuid4()),
        "name": name or "Enhanced Custom Workflow",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "custom-webhook",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": webhook_id,
                "name": "Custom Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": webhook_id
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
                        "value": "Custom Data",
                        "mode": "list"
                    },
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Message": "={{ $json.message }}",
                            "Request_ID": "={{ 'REQ-' + new Date().getTime().toString() }}",
                            "Timestamp": "={{ new Date().toISOString() }}",
                            "Status": "New"
                        },
                        "matchingColumns": [],
                        "schema": []
                    },
                    "options": {}
                },
                "id": sheets_id,
                "name": "Save to Custom Sheet",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [460, 300]
            }
        ],
        "pinData": {},
        "settings": {"executionOrder": "v1"},
        "staticData": {},
        "tags": ["custom", "enhanced", "fallback"],
        "triggerCount": 1,
        "versionId": "1",
        "meta": {
            "templateCreatedBy": "Enhanced AI System",
            "description": description or "Fallback workflow created by enhanced system"
        }
    }

def create_enhanced_workflow_template(workflow_type: str, custom_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """إنشاء قوالب workflows محسنة"""
    
    if workflow_type == "form_with_email":
        return create_form_email_template(custom_data or {})
    elif workflow_type == "scheduled_report":
        return create_scheduled_report_template(custom_data or {})
    elif workflow_type == "slack_notification":
        return create_slack_notification_template(custom_data or {})
    else:
        return make_minimal_valid_n8n("Enhanced Custom Workflow")

def create_form_email_template(custom_data: Dict[str, Any]) -> Dict[str, Any]:
    """إنشاء قالب نموذج مع إيميل"""
    webhook_id = str(uuid.uuid4())[:8]
    process_id = str(uuid.uuid4())[:8]
    sheets_id = str(uuid.uuid4())[:8]
    email_id = str(uuid.uuid4())[:8]
    
    sheet_name = custom_data.get('sheet_name', 'Form Submissions')
    
    return {
        "active": True,
        "connections": {
            webhook_id: {
                "main": [[{"node": process_id, "type": "main", "index": 0}]]
            },
            process_id: {
                "main": [[{"node": sheets_id, "type": "main", "index": 0}]]
            },
            sheets_id: {
                "main": [[{"node": email_id, "type": "main", "index": 0}]]
            }
        },
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "id": str(uuid.uuid4()),
        "name": f"Enhanced Form to {sheet_name} with Email",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "enhanced-form",
                    "responseMode": "onReceived"
                },
                "id": webhook_id,
                "name": "Form Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": webhook_id
            },
            {
                "parameters": {
                    "values": {
                        "string": [
                            {
                                "name": "ticket_id",
                                "value": "={{ 'TICKET-' + new Date().getTime().toString() }}"
                            },
                            {
                                "name": "priority",
                                "value": "={{ $json.urgent === true ? 'High' : 'Normal' }}"
                            },
                            {
                                "name": "processed_at",
                                "value": "={{ new Date().toISOString() }}"
                            }
                        ]
                    },
                    "options": {}
                },
                "id": process_id,
                "name": "Process Form Data",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [460, 300]
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
                        "value": sheet_name,
                        "mode": "list"
                    },
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "Ticket_ID": "={{ $('Process Form Data').item.json.ticket_id }}",
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Company": "={{ $json.company || 'N/A' }}",
                            "Message": "={{ $json.message }}",
                            "Priority": "={{ $('Process Form Data').item.json.priority }}",
                            "Submitted_At": "={{ $('Process Form Data').item.json.processed_at }}",
                            "Status": "New"
                        }
                    }
                },
                "id": sheets_id,
                "name": f"Save to {sheet_name}",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "send",
                    "toEmail": "={{ $json.email }}",
                    "subject": "تأكيد استلام طلبك - {{ $('Process Form Data').item.json.ticket_id }}",
                    "emailType": "text",
                    "message": """عزيزي/عزيزتي {{ $json.name }},

تم استلام طلبك بنجاح!

تفاصيل الطلب:
• رقم الطلب: {{ $('Process Form Data').item.json.ticket_id }}
• الأولوية: {{ $('Process Form Data').item.json.priority }}
• تاريخ الاستلام: {{ $('Process Form Data').item.json.processed_at.split('T')[0] }}

{{ $json.message ? 'رسالتك: ' + $json.message : '' }}

سيتم التواصل معك قريباً.

مع التحيات،
فريق الدعم"""
                },
                "id": email_id,
                "name": "Send Confirmation Email",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [900, 300]
            }
        ],
        "settings": {"executionOrder": "v1"},
        "staticData": {},
        "tags": ["enhanced", "form", "email", "automation"],
        "triggerCount": 1,
        "versionId": "1"
    }

def add_error_handling_node(workflow: Dict[str, Any], target_node_id: str) -> str:
    """إضافة عقدة معالجة الأخطاء"""
    error_node_id = str(uuid.uuid4())[:8]
    
    error_node = {
        "parameters": {
            "resource": "message",
            "operation": "send",
            "toEmail": "={{$env.ERROR_EMAIL || 'admin@company.com'}}",
            "subject": "Workflow Error - {{ $workflow.name }}",
            "emailType": "text",
            "message": """خطأ في Workflow: {{ $workflow.name }}

تفاصيل الخطأ:
• الوقت: {{ new Date().toISOString() }}
• العقدة: {{ $node.name }}
• الخطأ: {{ $json.error.message }}

يرجى التحقق من الإعدادات."""
        },
        "id": error_node_id,
        "name": "Error Handler",
        "type": "n8n-nodes-base.gmail",
        "typeVersion": 2,
        "position": [680, 500],
        "onError": "continueRegularOutput"
    }
    
    workflow["nodes"].append(error_node)
    
    # إضافة اتصال خطأ
    if target_node_id not in workflow["connections"]:
        workflow["connections"][target_node_id] = {"main": []}
    
    workflow["connections"][target_node_id]["error"] = [
        [{"node": error_node_id, "type": "main", "index": 0}]
    ]
    
    return error_node_id

def optimize_workflow_performance(workflow: Dict[str, Any]):
    """تحسين أداء الـ workflow"""
    
    # إعدادات الأداء
    settings = workflow.setdefault("settings", {})
    settings.update({
        "executionOrder": "v1",
        "saveManualExecutions": True,
        "callerPolicy": "workflowsFromSameOwner",
        "executionTimeout": 3600,  # ساعة واحدة
        "maxExecutionTimeout": 3600
    })
    
    # تحسين العقد للأداء
    for node in workflow.get("nodes", []):
        node_type = node.get("type", "")
        
        if "httpRequest" in node_type:
            # إضافة timeout للطلبات
            options = node.setdefault("parameters", {}).setdefault("options", {})
            options.setdefault("timeout", 30000)  # 30 ثانية
            
        elif "googleSheets" in node_type:
            # تحسين عمليات الجداول
            options = node.setdefault("parameters", {}).setdefault("options", {})
            options.setdefault("useAppend", True)  # أسرع للإضافة

def add_workflow_metadata(workflow: Dict[str, Any], metadata: Dict[str, Any]):
    """إضافة معلومات إضافية للـ workflow"""
    
    workflow.setdefault("meta", {}).update({
        "templateCreatedBy": "Enhanced AI System v2.0",
        "creationDate": datetime.now().isoformat(),
        "estimatedComplexity": metadata.get("complexity", "medium"),
        "requiredCredentials": metadata.get("credentials", []),
        "requiredEnvVars": metadata.get("env_vars", []),
        "description": metadata.get("description", ""),
        "tags": metadata.get("tags", [])
    })
    
    # إضافة تعليقات للمطورين
    if metadata.get("add_comments", True):
        add_developer_comments(workflow)

def add_developer_comments(workflow: Dict[str, Any]):
    """إضافة تعليقات للمطورين"""
    
    for node in workflow.get("nodes", []):
        node_type = node.get("type", "")
        
        if "webhook" in node_type:
            node.setdefault("notes", "نقطة دخول الـ workflow - تأكد من إعداد webhook URL")
            
        elif "googleSheets" in node_type:
            node.setdefault("notes", "تأكد من إعداد GOOGLE_SHEET_ID في environment variables")
            
        elif "gmail" in node_type:
            node.setdefault("notes", "يحتاج Gmail OAuth credentials - راجع إعدادات الحساب")
            
        elif "set" in node_type:
            node.setdefault("notes", "معالجة البيانات - يمكن تعديل القيم حسب الحاجة")

# دوال مساعدة إضافية
def create_backup_workflow(original: Dict[str, Any]) -> Dict[str, Any]:
    """إنشاء نسخة احتياطية مبسطة"""
    backup = copy.deepcopy(original)
    
    # تبسيط الـ workflow للحد الأدنى
    backup["name"] = f"Backup - {original.get('name', 'Workflow')}"
    backup["active"] = False  # إيقاف النسخة الاحتياطية
    
    return backup

def merge_workflows(base: Dict[str, Any], enhancement: Dict[str, Any]) -> Dict[str, Any]:
    """دمج workflows متعددة"""
    merged = copy.deepcopy(base)
    
    # دمج العقد
    merged["nodes"].extend(enhancement.get("nodes", []))

        # دمج الاتصالات
    merged["connections"].update(enhancement.get("connections", {}))
    
    # تحديث المعلومات
    merged["name"] = f"Merged - {base.get('name', 'Workflow')}"
    merged["updatedAt"] = datetime.now().isoformat()
    
    return merged
