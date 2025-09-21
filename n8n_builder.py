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
    workflow.setdefault("id", "1")
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
    
    # إصلاح العقد
    for node in workflow["nodes"]:
        if not node.get("id"):
            node["id"] = str(uuid.uuid4())
        
        node.setdefault("parameters", {})
        node.setdefault("typeVersion", 1)
        node.setdefault("position", [240, 300])
        
        if not node.get("name"):
            node["name"] = "Node"
    
    # تحديث عدد المشغلات
    trigger_types = ["n8n-nodes-base.webhook", "n8n-nodes-base.cron", "n8n-nodes-base.manualTrigger"]
    trigger_count = sum(1 for node in workflow["nodes"] if node.get("type") in trigger_types)
    workflow["triggerCount"] = max(trigger_count, 1)
    
    return workflow

def make_minimal_valid_n8n(name: str, description: str = "") -> Dict[str, Any]:
    """إنشاء workflow أساسي صالح"""
    node_id = str(uuid.uuid4())
    
    return {
        "active": True,
        "connections": {},
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "id": "1",
        "name": name or "Generated Workflow",
        "nodes": [
            {
                "parameters": {},
                "id": node_id,
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [240, 300]
            }
        ],
        "pinData": {},
        "settings": {"executionOrder": "v1"},
        "staticData": {},
        "tags": [],
        "triggerCount": 1,
        "versionId": "1"
    }
