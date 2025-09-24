# n8n_builder.py - النسخة المصححة والكاملة
from typing import Dict, Any, List
import uuid
import copy
from datetime import datetime

def validate_n8n_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """التحقق من صحة JSON وإصلاحه ليكون متوافق مع n8n Cloud"""
    if not isinstance(data, dict):
        print("[WARNING] Invalid workflow data, creating fallback")
        return make_minimal_valid_n8n("Invalid Workflow")
    
    # نسخ البيانات
    workflow = copy.deepcopy(data)
    print(f"[INFO] Validating workflow: {workflow.get('name', 'Unnamed')}")
    
    # الحقول الأساسية المطلوبة لـ n8n Cloud
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
    workflow.setdefault("versionId", str(uuid.uuid4()))
    
    # إضافة meta إذا لم تكن موجودة
    if "meta" not in workflow:
        workflow["meta"] = {
            "templateCreatedBy": "Enhanced AI Bot",
            "instanceId": str(uuid.uuid4())
        }
    
    # التحقق من العقد
    if not workflow["nodes"]:
        print("[WARNING] No nodes found, creating minimal workflow")
        return make_minimal_valid_n8n(workflow["name"])
    
    # إصلاح العقد مع تحسينات جديدة
    fixed_nodes = 0
    for node in workflow["nodes"]:
        if enhance_node(node):
            fixed_nodes += 1
    
    print(f"[INFO] Enhanced {fixed_nodes} nodes")
    
    # تحديث عدد المشغلات
    trigger_types = ["n8n-nodes-base.webhook", "n8n-nodes-base.cron", "n8n-nodes-base.manualTrigger"]
    trigger_count = sum(1 for node in workflow["nodes"] if node.get("type") in trigger_types)
    workflow["triggerCount"] = max(trigger_count, 1)
    
    # التحقق من الاتصالات
    validate_connections(workflow)
    
    # التأكد من تنسيق Tags لـ n8n Cloud
    ensure_modern_tags_format(workflow)
    
    print(f"[SUCCESS] Workflow validated: {len(workflow['nodes'])} nodes, {trigger_count} triggers")
    return workflow

def enhance_node(node: Dict[str, Any]) -> bool:
    """تحسين وإصلاح عقدة واحدة"""
    enhanced = False
    
    if not node.get("id"):
        node["id"] = str(uuid.uuid4())
        enhanced = True
    
    node.setdefault("parameters", {})
    node.setdefault("typeVersion", get_latest_type_version(node.get("type", "")))
    node.setdefault("position", [240, 300])
    
    if not node.get("name"):
        node["name"] = generate_node_name(node.get("type", ""))
        enhanced = True
    
    # تحسينات خاصة بنوع العقدة
    node_type = node.get("type", "").lower()
    
    if "webhook" in node_type:
        if enhance_webhook_node(node):
            enhanced = True
    elif "googlesheets" in node_type:
        if enhance_sheets_node(node):
            enhanced = True
    elif "gmail" in node_type:
        if enhance_gmail_node(node):
            enhanced = True
    elif "set" in node_type:
        if enhance_set_node(node):
            enhanced = True
    
    return enhanced

def enhance_webhook_node(node: Dict[str, Any]) -> bool:
    """تحسين عقدة Webhook"""
    params = node.setdefault("parameters", {})
    enhanced = False
    
    # إعدادات افتراضية محسنة
    if not params.get("httpMethod"):
        params["httpMethod"] = "POST"
        enhanced = True
    
    if not params.get("path"):
        params["path"] = "webhook"
        enhanced = True
        
    if not params.get("responseMode"):
        params["responseMode"] = "onReceived"
        enhanced = True
        
    params.setdefault("options", {})
    
    # إضافة webhookId إذا لم يكن موجود
    if not node.get("webhookId"):
        node["webhookId"] = node["id"]
        enhanced = True
    
    return enhanced

def enhance_sheets_node(node: Dict[str, Any]) -> bool:
    """تحسين عقدة Google Sheets"""
    params = node.setdefault("parameters", {})
    enhanced = False
    
    # إعدادات افتراضية
    if not params.get("resource"):
        params["resource"] = "sheet"
        enhanced = True
        
    if not params.get("operation"):
        params["operation"] = "appendOrUpdate"
        enhanced = True
    
    # إعداد الجدول
    if not params.get("documentId"):
        params["documentId"] = {
            "__rl": True,
            "value": "={{$env.GOOGLE_SHEET_ID}}",
            "mode": "id"
        }
        enhanced = True
    
    if not params.get("sheetName"):
        params["sheetName"] = {
            "__rl": True,
            "value": "Sheet1",
            "mode": "list"
        }
        enhanced = True
    
    # التأكد من وجود إعداد الأعمدة
    if not params.get("columns"):
        params["columns"] = {
            "mappingMode": "defineBelow",
            "value": {
                "Name": "={{ $json.name }}",
                "Email": "={{ $json.email }}",
                "Message": "={{ $json.message }}",
                "Request_ID": "={{ 'REQ-' + new Date().getTime().toString() }}",
                "Timestamp": "={{ new Date().toISOString() }}"
            },
            "matchingColumns": [],
            "schema": []
        }
        enhanced = True
    
    params.setdefault("options", {})
    
    return enhanced

def enhance_gmail_node(node: Dict[str, Any]) -> bool:
    """تحسين عقدة Gmail"""
    params = node.setdefault("parameters", {})
    enhanced = False
    
    # إعدادات افتراضية
    if not params.get("resource"):
        params["resource"] = "message"
        enhanced = True
        
    if not params.get("operation"):
        params["operation"] = "send"
        enhanced = True
        
    if not params.get("emailType"):
        params["emailType"] = "text"
        enhanced = True
    
    # رسالة افتراضية محسنة
    if not params.get("message"):
        params["message"] = """عزيزي {{ $json.name || 'العميل' }},

شكراً لتواصلك معنا. تم استلام رسالتك بنجاح.

تفاصيل الطلب:
{{ $json.message }}

سيتم الرد عليك في أقرب وقت ممكن.

مع أطيب التحيات،
فريق الدعم"""
        enhanced = True
    
    params.setdefault("options", {})
    
    return enhanced

def enhance_set_node(node: Dict[str, Any]) -> bool:
    """تحسين عقدة Set"""
    params = node.setdefault("parameters", {})
    enhanced = False
    
    if not params.get("values"):
        params["values"] = {
            "string": [
                {
                    "name": "processed_at",
                    "value": "={{ new Date().toISOString() }}"
                }
            ]
        }
        enhanced = True
    
    params.setdefault("options", {})
    
    return enhanced

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
                if isinstance(connection_list, list):
                    for connection in connection_list:
                        if isinstance(connection, dict):
                            target_node = connection.get("node")
                            if target_node in node_ids:
                                valid_list.append(connection)
                
                valid_main.append(valid_list)
            
            if valid_main and any(valid_main):
                valid_connections[source_id] = {"main": valid_main}
    
    workflow["connections"] = valid_connections
    print(f"[INFO] Validated {len(valid_connections)} connections")

def ensure_modern_tags_format(workflow: Dict[str, Any]):
    """التأكد من تنسيق Tags الحديث لـ n8n Cloud"""
    tags = workflow.get("tags", [])
    
    # تحويل tags إلى تنسيق n8n Cloud الحديث
    modern_tags = []
    for tag in tags:
        if isinstance(tag, str):
            # تحويل من string إلى object
            modern_tags.append({
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": tag
            })
        elif isinstance(tag, dict) and "name" in tag:
            # التأكد من وجود الحقول المطلوبة
            if "id" not in tag:
                tag["id"] = str(uuid.uuid4())
            if "createdAt" not in tag:
                tag["createdAt"] = datetime.now().isoformat()
            if "updatedAt" not in tag:
                tag["updatedAt"] = datetime.now().isoformat()
            modern_tags.append(tag)
    
    workflow["tags"] = modern_tags

def make_minimal_valid_n8n(name: str, description: str = "") -> Dict[str, Any]:
    """إنشاء workflow أساسي صالح ومتوافق مع n8n Cloud"""
    webhook_id = str(uuid.uuid4())
    sheets_id = str(uuid.uuid4())
    
    return {
        "meta": {
            "templateCreatedBy": "Enhanced AI Bot v2.0",
            "instanceId": str(uuid.uuid4())
        },
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
        "tags": [
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "custom"
            },
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "enhanced"
            }
        ],
        "triggerCount": 1,
        "versionId": str(uuid.uuid4())
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

# تصدير الوظائف المطلوبة
__all__ = [
    'validate_n8n_json',
    'make_minimal_valid_n8n',
    'enhance_node',
    'validate_connections',
    'create_enhanced_workflow_template',
    'optimize_workflow_performance'
    ]
