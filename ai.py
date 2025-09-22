# ai_enhanced.py - النظام المحسن الكامل
import os, json, httpx, re
from typing import Dict, Any, Tuple, List, Optional
import copy
import uuid
from datetime import datetime
from dataclasses import dataclass

# إعدادات Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# مكتبة workflows أساسية للتشغيل
BASIC_WORKFLOWS = {
    "webhook_to_sheets": {
        "active": True,
        "connections": {
            "webhook_node": {
                "main": [[{"node": "sheets_node", "type": "main", "index": 0}]]
            }
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z", 
        "id": "1",
        "name": "Enhanced Form to Google Sheets",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "contact-form",
                    "responseMode": "onReceived"
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
                    "documentId": {"__rl": True, "value": "={{$env.GOOGLE_SHEET_ID}}", "mode": "id"},
                    "sheetName": {"__rl": True, "value": "Sheet1", "mode": "list"},
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Message": "={{ $json.message }}",
                            "Request_ID": "={{ 'REQ-' + new Date().getTime().toString() }}",
                            "Timestamp": "={{ new Date().toISOString() }}"
                        }
                    }
                },
                "id": "sheets_node",
                "name": "Save to Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [460, 300]
            }
        ],
        "settings": {"executionOrder": "v1"},
        "staticData": {},
        "tags": ["form", "webhook", "sheets"],
        "triggerCount": 1,
        "versionId": "1"
    }
}

class SimpleWorkflowLibrary:
    """مكتبة workflows مبسطة للتشغيل الأساسي"""
    
    def __init__(self):
        self.workflows = []
        self.load_basic_library()
    
    def load_basic_library(self):
        """تحميل مكتبة أساسية"""
        for name, workflow in BASIC_WORKFLOWS.items():
            processed = {
                'name': workflow['name'],
                'raw_workflow': workflow,
                'services': ['google-sheets'] if 'sheets' in name else ['basic'],
                'trigger_types': ['webhook'] if 'webhook' in name else ['manual'],
                'keywords': name.split('_'),
                'complexity': 'medium',
                'active': True,
                'relevance_score': 1
            }
            self.workflows.append(processed)
    
    def search_workflows(self, query: str, services: List[str] = None, max_results: int = 5):
        """بحث مبسط في المكتبة"""
        return self.workflows[:max_results]
    
    def get_stats(self):
        """إحصائيات أساسية"""
        return {
            'total_workflows': len(self.workflows),
            'active_workflows': len([w for w in self.workflows if w['active']]),
            'unique_services': 2,
            'available_services': ['google-sheets', 'gmail', 'slack'],
            'available_triggers': ['webhook', 'schedule', 'manual'],
            'complexity_distribution': {'medium': len(self.workflows)}
        }

# النظام المحسن
class EnhancedAISystem:
    """نظام AI محسن مع مكتبة أساسية"""
    
    def __init__(self):
        self.library = SimpleWorkflowLibrary()
        print(f"[INFO] Enhanced AI system initialized with {len(self.library.workflows)} workflows")
    
    async def analyze_request_with_ai(self, user_prompt: str) -> Dict[str, Any]:
        """تحليل الطلب مع AI أو احتياطي محلي"""
        if GEMINI_API_KEY:
            try:
                return await self._gemini_analysis(user_prompt)
            except Exception as e:
                print(f"[WARNING] Gemini analysis failed: {e}")
        
        return self._local_analysis(user_prompt)
    
    async def _gemini_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """تحليل باستخدام Gemini"""
        analysis_prompt = f"""
تحليل طلب الأتمتة:
"{user_prompt}"

استخرج المعلومات وأجب بـ JSON:
{{
  "trigger_type": "webhook/schedule/manual",
  "services": ["service1", "service2"],
  "operations": ["operation1", "operation2"],
  "custom_names": {{"sheet_name": "اسم مخصص"}},
  "business_logic": ["generate_id", "send_email"],
  "data_fields": {{"name": "Name", "email": "Email"}}
}}
"""
        
        response = await _call_gemini_api(analysis_prompt)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return self._local_analysis(user_prompt)
    
    def _local_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """تحليل محلي احتياطي محسن"""
        text = user_prompt.lower()
        
        # تحديد المشغل
        trigger = 'webhook'
        if any(word in text for word in ['schedule', 'daily', 'every', 'time']):
            trigger = 'schedule'
        
        # تحديد الخدمات
        services = []
        if any(word in text for word in ['sheet', 'جدول', 'spreadsheet']):
            services.append('google-sheets')
        if any(word in text for word in ['email', 'mail', 'gmail', 'إيميل']):
            services.append('gmail')
        if 'slack' in text:
            services.append('slack')
        
        if not services:
            services = ['google-sheets']  # افتراضي
        
        # استخراج أسماء مخصصة بسيطة
        custom_names = {}
        
        # البحث عن أنماط الأسماء
        sheet_patterns = [
            r"جدول['\s]*['\"]([^'\"]+)['\"]",
            r"sheet['\s]*['\"]([^'\"]+)['\"]",
            r"في\s+['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in sheet_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                custom_names['sheet_name'] = match.group(1)
                break
        
        # منطق أعمال أساسي
        business_logic = []
        if any(word in text for word in ['رقم', 'id', 'identifier']):
            business_logic.append('generate_id')
        if any(word in text for word in ['email', 'إيميل', 'رسالة']):
            business_logic.append('send_email')
        
        return {
            'trigger_type': trigger,
            'services': services,
            'operations': ['save_data', 'process_form'],
            'custom_names': custom_names,
            'business_logic': business_logic,
            'data_fields': {'name': 'Name', 'email': 'Email', 'message': 'Message'}
        }

# النظام الرئيسي
enhanced_ai_system = EnhancedAISystem()

async def _call_gemini_api(prompt: str, system_instruction: str = "") -> str:
    """استدعاء Gemini API"""
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
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload)
        
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API returned {response.status_code}")
        
        data = response.json()
        
        if not data.get("candidates") or not data["candidates"][0].get("content"):
            raise RuntimeError("No valid response from Gemini")
        
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

def customize_workflow_from_analysis(base_workflow: Dict, analysis: Dict) -> Dict:
    """تخصيص workflow بناءً على التحليل"""
    customized = copy.deepcopy(base_workflow)
    
    # تحديث الاسم
    custom_names = analysis.get('custom_names', {})
    if custom_names:
        first_custom = list(custom_names.values())[0]
        customized['name'] = f"Custom Form to {first_custom}"
    
    # تخصيص عقدة الجدول
    for node in customized.get('nodes', []):
        if 'googleSheets' in node.get('type', ''):
            params = node.setdefault('parameters', {})
            
            # استخدام اسم الجدول المخصص
            if 'sheet_name' in custom_names:
                params['sheetName'] = {
                    "__rl": True,
                    "value": custom_names['sheet_name'],
                    "mode": "list"
                }
            
            # تخصيص الأعمدة
            data_fields = analysis.get('data_fields', {})
            if data_fields:
                columns = {}
                for field_key, field_name in data_fields.items():
                    columns[field_name] = f"={{{{ $json.{field_key} }}}}"
                
                # إضافة حقول تلقائية
                business_logic = analysis.get('business_logic', [])
                if 'generate_id' in business_logic:
                    columns['Request_ID'] = "={{ 'REQ-' + new Date().getTime().toString() }}"
                
                columns['Timestamp'] = "={{ new Date().toISOString() }}"
                
                params['columns'] = {
                    "mappingMode": "defineBelow",
                    "value": columns
                }
    
    # تحديث التواريخ
    customized['updatedAt'] = datetime.now().isoformat()
    customized['id'] = str(uuid.uuid4())
    
    return customized

async def plan_workflow_with_ai(user_prompt: str) -> Tuple[str, bool]:
    """تخطيط workflow محسن"""
    try:
        print(f"[INFO] Enhanced analysis starting...")
        
        # تحليل الطلب
        analysis = await enhanced_ai_system.analyze_request_with_ai(user_prompt)
        
        # البحث في المكتبة
        relevant_workflows = enhanced_ai_system.library.search_workflows(
            user_prompt, 
            analysis.get('services', []),
            max_results=3
        )
        
        # تحضير التقرير
        plan_parts = [
            "🔍 **تحليل محسن للطلب:**",
            "",
            f"**المشغل:** {analysis.get('trigger_type', 'webhook')}",
            f"**الخدمات:** {', '.join(analysis.get('services', ['أساسية']))}",
            f"**العمليات:** {', '.join(analysis.get('operations', ['معالجة بيانات']))}",
        ]
        
        custom_names = analysis.get('custom_names', {})
        if custom_names:
            plan_parts.extend([
                "",
                "**الأسماء المخصصة:**",
                json.dumps(custom_names, ensure_ascii=False, indent=2)
            ])
        
        business_logic = analysis.get('business_logic', [])
        if business_logic:
            plan_parts.extend([
                "",
                f"**منطق الأعمال:** {', '.join(business_logic)}"
            ])
        
        if relevant_workflows:
            plan_parts.extend([
                "",
                f"**قوالب مشابهة ({len(relevant_workflows)}):**"
            ])
            for i, wf in enumerate(relevant_workflows, 1):
                plan_parts.append(f"{i}. {wf['name']}")
        
        plan_parts.extend([
            "",
            "**طلب المستخدم:**",
            user_prompt
        ])
        
        return "\n".join(plan_parts), True
        
    except Exception as e:
        print(f"[WARNING] Enhanced planning failed: {e}")
        
        # خطة احتياطية
        fallback_plan = f"""📋 **تحليل أساسي:**

**المشغل:** webhook  
**الخدمات:** google-sheets
**العمليات:** حفظ البيانات

**طلب المستخدم:**
{user_prompt}

(استخدام النظام الأساسي - للحصول على أفضل النتائج، تأكد من GEMINI_API_KEY)"""
        
        return fallback_plan, False

async def draft_n8n_json_with_ai(plan: str) -> Tuple[str, bool]:
    """إنشاء workflow مخصص"""
    try:
        # استخراج طلب المستخدم من الخطة
        user_request = plan.split("طلب المستخدم:")[-1].strip()
        
        # تحليل الطلب
        analysis = await enhanced_ai_system.analyze_request_with_ai(user_request)
        
        # اختيار قالب مناسب
        base_workflow = BASIC_WORKFLOWS['webhook_to_sheets']
        
        # تخصيص الـ workflow
        customized_workflow = customize_workflow_from_analysis(base_workflow, analysis)
        
        print("[SUCCESS] Generated enhanced custom workflow")
        return json.dumps(customized_workflow, ensure_ascii=False, indent=2), True
        
    except Exception as e:
        print(f"[ERROR] Enhanced workflow generation failed: {e}")
        
        # احتياطي
        fallback = copy.deepcopy(BASIC_WORKFLOWS['webhook_to_sheets'])
        fallback['name'] = "Basic Custom Automation"
        fallback['updatedAt'] = datetime.now().isoformat()
        
        return json.dumps(fallback, ensure_ascii=False, indent=2), False

async def test_gemini_connection() -> Dict[str, Any]:
    """اختبار اتصال Gemini"""
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "error": "GEMINI_API_KEY not configured"
        }
    
    try:
        result = await _call_gemini_api("قل 'النظام المحسن يعمل!'")
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
    """القوالب المتاحة"""
    return {
        "enhanced_form": "Form with custom fields and auto-generated IDs",
        "basic_automation": "Simple webhook to sheets integration",
        "scheduled_task": "Time-based automation task"
    }

def get_library_stats() -> Dict[str, Any]:
    """إحصائيات المكتبة"""
    return enhanced_ai_system.library.get_stats()

def search_library_candidates(query: str, top_k: int = 3) -> List[Dict]:
    """البحث في المكتبة"""
    return enhanced_ai_system.library.search_workflows(query, max_results=top_k)
