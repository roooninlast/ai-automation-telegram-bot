from typing import Dict, Any, List, Optional
import uuid
import copy
from datetime import datetime

def _ensure_node_id(node: Dict[str, Any]) -> None:
    """التأكد من وجود معرف فريد للعقدة"""
    if not node.get("id"):
        node["id"] = str(uuid.uuid4())

def _index_by_id(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """فهرسة العقد بواسطة المعرف"""
    return {n["id"]: n for n in nodes}

def _ensure_required_node_fields(node: Dict[str, Any]) -> Dict[str, Any]:
    """التأكد من وجود الحقول المطلوبة لكل عقدة في n8n"""
    
    # الحقول الأساسية المطلوبة لكل عقدة
    if "parameters" not in node:
        node["parameters"] = {}
    
    if "typeVersion" not in node:
        node["typeVersion"] = 1
        
    if "position" not in node:
        node["position"] = [200, 200]
        
    if "name" not in node:
        # استخراج اسم من النوع
        node_type
