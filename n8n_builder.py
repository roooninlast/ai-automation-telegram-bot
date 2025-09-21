from typing import Dict, Any, List, Optional
import uuid
import copy
from datetime import datetime

def _ensure_id(node: Dict[str, Any]) -> None:
    """التأكد من وجود معرف فريد للعقدة"""
    if not node.get("id"):
        node["id"] = str(uuid.uuid4())[:8]

def _index_by_id(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """فهرسة العقد بواسطة المعرف"""
    return {n["id"]: n for n in nodes}

def _ensure_required_fields(node: Dict[str, Any]) -> Dict[str, Any]:
    """التأكد من وجود الحقول المطلوبة لكل عقدة"""
    required_defaults = {
        "parameters": {},
        "typeVersion": 1,
        "position": [200, 200],
        "name": node.get("type", "Node").replace("n8n-nodes-base.", "").title()
    }
    
    for field, default_value in required_defaults.items():
        if field not in node:
            node[field] = default_value
    
    return node

def _fix_node_parameters(node: Dict[str, Any]) -> Dict[str, Any]:
    """إصلاح parameters العقد حسب نوعها"""
    node_type = node.get("type", "")
    parameters = node.get("parameters", {})
    
    # إصلاحات خاصة بكل نوع عقدة
    if node_type == "n8n-nodes-base.webhook":
        if "path" not in parameters:
            parameters["path"] = "webhook"
        if "responseMode" not in parameters:
            parameters["responseMode"] = "onReceived"
        if "httpMethod" not in parameters:
            parameters["httpMethod"] = "POST"
            
    elif node_type == "n8n-nodes-base.googleSheets":
        if "resource" not in parameters:
            parameters["resource"] = "spreadsheet"
        if "operation" not in parameters:
            parameters["operation"] = "appendOrUpdate"
        if "documentId" not in parameters:
            parameters["documentId"] = "={{$env.GOOGLE_SHEET_ID}}"
            
    elif node_type == "n8n-nodes-base.gmail":
        if "operation" not in parameters:
            parameters["operation"] = "send"
            
    elif node_type == "n8n-nodes-base.slack":
        if "operation" not in parameters:
            parameters["operation"] = "postMessage"
        if "channel" not in parameters:
            parameters["channel"] = "={{$env.SLACK_CHANNEL}}"
            
    elif node_type == "n8n-nodes-base.cron":
        if "rule" not in parameters:
            parameters["rule"] = {"hour": 9, "minute": 0}
            
    elif node_type == "n8n-nodes-base.httpRequest":
        if "method" not in parameters:
            parameters["method"] = "GET"
        if "url" not in parameters:
            parameters["url"] = "={{$env.API_ENDPOINT}}"
    
    node["parameters"] = parameters
    return node

def _generate_positions(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """إنشاء مواضع منطقية للعقد"""
    for i, node in enumerate(nodes):
        x = 240 + (i * 220)  # توزيع أفقي
        y = 300  # نفس الارتفاع
        node["position"] = [x, y]
    
    return nodes

def _validate_connections(connections: Dict[str, Any], node_ids: set) -> Dict[str, Any]:
    """التحقق من صحة الاتصالات بين العقد"""
    validated_connections = {}
    
    for source_id, connection_data in connections.items():
        if source_id not in node_ids:
            continue  # تجاهل العقد غير الموجودة
            
        main_connections = connection_data.get("main", [])
        valid_main = []
        
        for lane in main_connections:
            valid_lane = []
            for edge in lane:
                target_id = edge.get("node")
                if target_id in node_ids:
                    # تأكد من وجود الحقول المطلوبة
                    if "type" not in edge:
                        edge["type"] = "main"
                    if "index" not in edge:
                        edge["index"] = 0
                    valid_lane.append(edge)
            
            if valid_lane:
                valid_main.append(valid_lane)
        
        if valid_main:
            validated_connections[source_id] = {"main": valid_main}
    
    return validated_connections

def _create_default_connections(nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """إنشاء اتصالات افتراضية بين العقد"""
    if len(nodes) < 2:
        return {}
    
    connections = {}
    for i in range(len(nodes) - 1):
        source_id = nodes[i]["id"]
        target_id = nodes[i + 1]["id"]
        
        connections[source_id] = {
            "main": [[{
                "node": target_id,
                "type": "main", 
                "index": 0
            }]]
        }
    
    return connections

def make_minimal_valid_n8n(name: str, description: str = "") -> Dict[str, Any]:
    """إنشاء workflow أساسي صالح لـ n8n"""
    return {
        "name": name or "Generated Workflow",
        "nodes": [
            {
                "parameters": {},
                "id": "manual_trigger",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "keepOnlySet": True,
                    "values": {
                        "string": [{
                            "name": "note",
                            "value": description[:500] if description else "Generated by AI Bot"
                        }]
                    }
                },
                "id": "set_data",
                "name": "Set Data",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [460, 300]
            }
        ],
        "connections": {
            "manual_trigger": {
                "main": [[{
                    "node": "set_data",
                    "type": "main",
                    "index": 0
                }]]
            }
        },
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "settings": {
            "timezone": "UTC",
            "saveManualExecutions": True
        },
        "staticData": None,
        "tags": ["generated", "basic"],
        "triggerCount": 1,
        "versionId": "1"
    }

def validate_n8n_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """التحقق الشامل من صحة JSON الخاص بـ n8n وإصلاح الأخطاء"""
    if not isinstance(data, dict):
        print("[WARNING] Invalid workflow data, creating minimal workflow")
        return make_minimal_valid_n8n("Invalid Workflow")
    
    # نسخ البيانات لتجنب تعديل الأصل
    workflow = copy.deepcopy(data)
    
    # الحقول الأساسية المطلوبة
    required_fields = {
        "name": workflow.get("name") or "Generated Workflow",
        "nodes": workflow.get("nodes") or [],
        "connections": workflow.get("connections") or {},
        "settings": workflow.get("settings") or {"timezone": "UTC"},
        "tags": workflow.get("tags") or ["generated"],
        "createdAt": workflow.get("createdAt") or datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "staticData": workflow.get("staticData"),
        "triggerCount": len([n for n in workflow.get("nodes", []) if is_trigger_node(n)]) or 1,
        "versionId": workflow.get("versionId") or "1"
    }
    
    workflow.update(required_fields)
    
    # التحقق من العقد
    nodes = workflow["nodes"]
    if not nodes:
        print("[WARNING] No nodes found, creating minimal workflow")
        return make_minimal_valid_n8n(workflow["name"])
    
    # معالجة كل عقدة
    processed_nodes = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
            
        # إضافة المعرف
        _ensure_id(node)
        
        # التأكد من الحقول المطلوبة
        node = _ensure_required_fields(node)
        
        # إصلاح parameters
        node = _fix_node_parameters(node)
        
        processed_nodes.append(node)
    
    if not processed_nodes:
        print("[WARNING] No valid nodes after processing")
        return make_minimal_valid_n8n(workflow["name"])
    
    # إعادة تعيين المواضع
    processed_nodes = _generate_positions(processed_nodes)
    workflow["nodes"] = processed_nodes
    
    # التحقق من الاتصالات
    node_ids = {node["id"] for node in processed_nodes}
    connections = workflow.get("connections", {})
    
    if connections:
        validated_connections = _validate_connections(connections, node_ids)
        workflow["connections"] = validated_connections
    else:
        # إنشاء اتصالات افتراضية
        workflow["connections"] = _create_default_connections(processed_nodes)
    
    # التحقق من وجود trigger
    has_trigger = any(is_trigger_node(node) for node in processed_nodes)
    if not has_trigger:
        print("[WARNING] No trigger node found")
        # يمكن إضافة trigger افتراضي هنا إذا لزم الأمر
    
    # تنظيف البيانات النهائي
    workflow = _cleanup_workflow(workflow)
    
    print(f"[INFO] Workflow validated: {len(processed_nodes)} nodes, {len(workflow['connections'])} connections")
    return workflow

def _cleanup_workflow(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """تنظيف نهائي للـ workflow"""
    # إزالة الحقول الفارغة أو None
    cleaned = {}
    for key, value in workflow.items():
        if value is not None:
            if isinstance(value, dict) and not value:
                continue  # تجاهل القواميس الفارغة
            elif isinstance(value, list) and not value:
                if key in ["nodes"]:  # العقد مطلوبة حتى لو فارغة
                    cleaned[key] = value
                else:
                    continue
            else:
                cleaned[key] = value
    
    return cleaned

def is_trigger_node(node: Dict[str, Any]) -> bool:
    """التحقق من كون العقدة trigger"""
    trigger_types = [
        "n8n-nodes-base.webhook",
        "n8n-nodes-base.cron", 
        "n8n-nodes-base.manualTrigger",
        "n8n-nodes-base.emailTrigger",
        "n8n-nodes-base.fileTrigger",
        "n8n-nodes-base.intervalTrigger"
    ]
    
    return node.get("type") in trigger_types

def get_workflow_stats(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """الحصول على إحصائيات الـ workflow"""
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", {})
    
    node_types = {}
    trigger_count = 0
    
    for node in nodes:
        node_type = node.get("type", "unknown")
        base_type = node_type.replace("n8n-nodes-base.", "")
        node_types[base_type] = node_types.get(base_type, 0) + 1
        
        if is_trigger_node(node):
            trigger_count += 1
    
    return {
        "name": workflow.get("name", "Unknown"),
        "total_nodes": len(nodes),
        "total_connections": sum(len(conn.get("main", [])) for conn in connections.values()),
        "trigger_count": trigger_count,
        "node_types": node_types,
        "has_valid_structure": bool(nodes and (connections or len(nodes) == 1))
    }

def export_workflow_summary(workflow: Dict[str, Any]) -> str:
    """إنشاء ملخص للـ workflow"""
    stats = get_workflow_stats(workflow)
    
    summary = f"""📊 **ملخص Workflow:**

**اسم الـ Workflow:** {stats['name']}
**عدد العقد:** {stats['total_nodes']}
**عدد الاتصالات:** {stats['total_connections']}
**عدد المشغلات:** {stats['trigger_count']}

**أنواع العقد:**"""
    
    for node_type, count in stats['node_types'].items():
        summary += f"\n• {node_type}: {count}"
    
    summary += f"\n\n**صالح للاستيراد:** {'✅ نعم' if stats['has_valid_structure'] else '❌ لا'}"
    
    return summary

def validate_environment_variables(workflow: Dict[str, Any]) -> List[str]:
    """استخراج متغيرات البيئة المطلوبة"""
    import re
    
    env_vars = set()
    workflow_str = str(workflow)
    
    # البحث عن patterns مثل {{$env.VARIABLE_NAME}}
    env_pattern = r'\{\{\$env\.([A-Z_][A-Z0-9_]*)\}\}'
    matches = re.findall(env_pattern, workflow_str)
    env_vars.update(matches)
    
    return sorted(list(env_vars))

def suggest_credentials(workflow: Dict[str, Any]) -> List[str]:
    """اقتراح الاتصالات المطلوبة للـ workflow"""
    credentials = set()
    
    for node in workflow.get("nodes", []):
        node_type = node.get("type", "")
        
        if "googleSheets" in node_type:
            credentials.add("Google Sheets API")
        elif "gmail" in node_type:
            credentials.add("Gmail API") 
        elif "slack" in node_type:
            credentials.add("Slack API")
        elif "httpRequest" in node_type:
            credentials.add("HTTP Authentication")
    
    return sorted(list(credentials))
