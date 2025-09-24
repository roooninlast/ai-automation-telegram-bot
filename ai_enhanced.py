# ai_enhanced.py - النظام المحسن الكامل
import os, json, httpx, re
from typing import Dict, Any, Tuple, List, Optional
import copy
import uuid
from datetime import datetime

# إعدادات Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def create_modern_webhook_to_sheets(custom_data: Dict = None) -> Dict[str, Any]:
    """قالب حديث متوافق مع n8n Cloud"""
    
    webhook_id = str(uuid.uuid4())
    sheets_id = str(uuid.uuid4())
    
    sheet_name = "Sheet1"
    workflow_name = "Enhanced Form to Google Sheets"
    
    if custom_data:
        sheet_name = custom_data.get('sheet_name', sheet_name)
        if sheet_name != "Sheet1":
            workflow_name = f"Custom Form to {sheet_name}"
    
    # بناء الأعمدة
    columns_value = {
        "Name": "={{ $json.name }}",
        "Email": "={{ $json.email }}",
        "Message": "={{ $json.message }}",
        "Request_ID": "={{ 'REQ-' + new Date().getTime().toString() }}",
        "Timestamp": "={{ new Date().toISOString() }}"
    }
    
    # إضافة حقول مخصصة
    if custom_data and 'data_fields' in custom_data:
        for field_key, field_name in custom_data['data_fields'].items():
            if field_key not in ['name', 'email', 'message']:
                columns_value[field_name] = f"={{{{ $json.{field_key} }}}}"
    
    return {
        "meta": {
            "templateCreatedBy": "Enhanced AI Bot v2.0",
            "instanceId": str(uuid.uuid4())
        },
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "contact-form",
                    "responseMode": "onReceived",
                    "options": {}
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
                        "value": columns_value,
                        "matchingColumns": [],
                        "schema": []
                    },
                    "options": {}
                },
                "id": sheets_id,
                "name": "Save to Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [460, 300]
            }
        ],
        "connections": {
            webhook_id: {
                "main": [
                    [
                        {
                            "node": sheets_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {
            "executionOrder": "v1"
        },
        "versionId": str(uuid.uuid4()),
        "id": str(uuid.uuid4()),
        "name": workflow_name,
        "tags": [
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "form"
            }
        ],
        "pinData": {},
        "staticData": {},
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "triggerCount": 1
    }

def create_modern_form_with_email(custom_data: Dict = None) -> Dict[str, Any]:
    """نموذج مع إيميل - متوافق مع n8n Cloud الحديث"""
    
    webhook_id = str(uuid.uuid4())
    process_id = str(uuid.uuid4())
    sheets_id = str(uuid.uuid4())
    email_id = str(uuid.uuid4())
    
    sheet_name = "Service Requests"
    workflow_name = "Service Request with Email Confirmation"
    
    if custom_data:
        sheet_name = custom_data.get('sheet_name', sheet_name)
        if sheet_name != "Service Requests":
            workflow_name = f"Form to {sheet_name} with Email"
    
    return {
        "meta": {
            "templateCreatedBy": "Enhanced AI Bot v2.0",
            "instanceId": str(uuid.uuid4())
        },
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST", 
                    "path": "service-request",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": webhook_id,
                "name": "Service Request",
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
                                "value": "={{ $json.budget && parseInt($json.budget) > 10000 ? 'High' : 'Normal' }}"
                            }
                        ]
                    },
                    "options": {}
                },
                "id": process_id,
                "name": "Process Request Data",
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
                            "Ticket_ID": "={{ $('Process Request Data').item.json.ticket_id }}",
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Company": "={{ $json.company }}",
                            "Service_Type": "={{ $json.service_type }}",
                            "Budget": "={{ $json.budget }}",
                            "Priority": "={{ $('Process Request Data').item.json.priority }}",
                            "Submitted_At": "={{ new Date().toISOString() }}",
                            "Status": "New"
                        },
                        "matchingColumns": [],
                        "schema": []
                    },
                    "options": {}
                },
                "id": sheets_id,
                "name": "Save Service Request", 
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "send",
                    "toEmail": "={{ $json.email }}",
                    "subject": "تأكيد استلام طلب الخدمة - {{ $('Process Request Data').item.json.ticket_id }}",
                    "emailType": "text",
                    "message": "عزيزي/عزيزتي {{ $json.name }},\\n\\nتم استلام طلب الخدمة الخاص بك بنجاح.\\n\\nرقم الطلب: {{ $('Process Request Data').item.json.ticket_id }}\\n\\nشكراً لثقتك بنا،\\nفريق الخدمات",
                    "options": {}
                },
                "id": email_id,
                "name": "Send Confirmation Email",
                "type": "n8n-nodes-base.gmail", 
                "typeVersion": 2,
                "position": [900, 300]
            }
        ],
        "connections": {
            webhook_id: {
                "main": [
                    [
                        {
                            "node": process_id,
                            "type": "main", 
                            "index": 0
                        }
                    ]
                ]
            },
            process_id: {
                "main": [
                    [
                        {
                            "node": sheets_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            sheets_id: {
                "main": [
                    [
                        {
                            "node": email_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {
            "executionOrder": "v1"
        },
        "versionId": str(uuid.uuid4()),
        "id": str(uuid.uuid4()),
        "name": workflow_name,
        "tags": [
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "service"
            }
        ],
        "pinData": {},
        "staticData": {},
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "triggerCount": 1
    }

# القوالب الحديثة المتوافقة مع n8n Cloud
MODERN_TEMPLATES = {
    "webhook_to_sheets": create_modern_webhook_to_sheets,
    "form_with_email": create_modern_form_with_email
}

class SimpleWorkflowLibrary:
    """مكتبة workflows مبسطة للتشغيل الأساسي"""
    
    def __init__(self):
        self.workflows = []
        self.load_basic_library()
    
    def load_basic_library(self):
        """تحميل مكتبة أساسية"""
        for name, template_func in MODERN_TEMPLATES.items():
            template = template_func()
            processed = {
                'name': template['name'],
                'raw_workflow': template,
                'services': ['google-sheets', 'gmail'] if 'email' in name else ['google-sheets'],
                'trigger_types': ['webhook'],
                'keywords': name.split('_'),
                'complexity': 'medium',
                'active': True,
                'relevance_score': 1
            }
            self.workflows.append(processed)
        print(f"[INFO] Loaded {len(self.workflows)} basic templates")
    
    def search_workflows(self, query: str, services: List[str] = None, max_results: int = 5):
        """بحث مبسط في المكتبة"""
        return self.workflows[:max_results]
    
    def get_stats(self):
        """إحصائيات أساسية"""
        return {
            'total_workflows': len(self.workflows),
            'active_workflows': len([w for w in self.workflows if w['active']]),
            'unique_services': 3,
            'available_services': ['google-sheets', 'gmail', 'slack'],
            'available_triggers': ['webhook', 'schedule', 'manual'],
            'complexity_distribution': {'medium': len(self.workflows)}
        }

# النظام المحسن
class EnhancedAISystem:
    """نظام AI محسن مع قوالب متوافقة مع n8n Cloud الحديث"""
    
    def __init__(self):
        self.library = SimpleWorkflowLibrary()
        print(f"[INFO] Enhanced AI system initialized with {len(self.library.workflows)} modern workflows")
    
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
  "trigger_type": "webhook",
  "services": ["google-sheets"],
  "operations": ["save_data"],
  "custom_names": {{"sheet_name": "اسم مخصص"}},
  "business_logic": ["generate_id"],
  "data_fields": {{"name": "Name", "email": "Email"}}
}}
"""
        
        response = await _call_gemini_api(analysis_prompt)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                return self._local_analysis(user_prompt)
        else:
            return self._local_analysis(user_prompt)
    
    def _local_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """تحليل محلي احتياطي محسن"""
        text = user_prompt.lower()
        print(f"[INFO] Local analysis for: {text[:50]}...")
        
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
        
        if not services:
            services = ['google-sheets']  # افتراضي
        
        # استخراج أسماء مخصصة محسنة
        custom_names = {}
        
        # البحث عن أنماط الأسماء المختلفة
        patterns = [
            r"جدول['\s]*['\"]([^'\"]+)['\"]",
            r"sheet['\s]*named['\s]*['\"]([^'\"]+)['\"]",
            r"في\s+['\"]([^'\"]+)['\"]",
            r"اسمه\s+['\"]([^'\"]+)['\"]",
            r"يسمى\s+['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_prompt, re.IGNORECASE)
            if match:
                custom_names['sheet_name'] = match.group(1)
                print(f"[INFO] Found custom sheet name: {match.group(1)}")
                break
        
        # منطق أعمال محسن
        business_logic = []
        if any(word in text for word in ['رقم', 'id', 'identifier', 'ticket']):
            business_logic.append('generate_id')
        if any(word in text for word in ['email', 'إيميل', 'رسالة', 'تأكيد']):
            business_logic.append('send_email')
        
        # تحديد حقول البيانات المتقدمة
        data_fields = {'name': 'Name', 'email': 'Email'}
        
        if 'company' in text or 'شركة' in text:
            data_fields['company'] = 'Company'
        if 'service' in text or 'خدمة' in text:
            data_fields['service_type'] = 'Service Type'  
        if 'budget' in text or 'ميزانية' in text:
            data_fields['budget'] = 'Budget'
        if 'message' in text or 'رسالة' in text:
            data_fields['message'] = 'Message'
        
        result = {
            'trigger_type': trigger,
            'services': services,
            'operations': ['save_data', 'process_form'],
            'custom_names': custom_names,
            'business_logic': business_logic,
            'data_fields': data_fields
        }
        
        print(f"[INFO] Analysis result: {json.dumps(result, ensure_ascii=False)}")
        return result

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

async def plan_workflow_with_ai(user_prompt: str) -> Tuple[str, bool]:
    """تخطيط workflow محسن مع قوالب حديثة"""
    try:
        print(f"[INFO] Enhanced analysis with modern templates...")
        
        # تحليل الطلب
        analysis = await enhanced_ai_system.analyze_request_with_ai(user_prompt)
        
        # البحث في المكتبة
        relevant_workflows = enhanced_ai_system.library.search_workflows(
            user_prompt, 
            analysis.get('services', []),
            max_results=2
        )
        
        # تحضير التقرير
        plan_parts = [
            "🔍 **تحليل محسن للطلب (n8n Cloud متوافق):**",
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
        
        data_fields = analysis.get('data_fields', {})
        if len(data_fields) > 2:  # أكثر من name وemail
            plan_parts.extend([
                "",
                f"**حقول البيانات:** {', '.join(data_fields.values())}"
            ])
        
        if relevant_workflows:
            plan_parts.extend([
                "",
                f"**قوالب n8n Cloud متوافقة ({len(relevant_workflows)}):**"
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
        fallback_plan = f"""📋 **تحليل أساسي (n8n Cloud متوافق):**

**المشغل:** webhook  
**الخدمات:** google-sheets
**العمليات:** حفظ البيانات
**التوافق:** n8n Cloud format

**طلب المستخدم:**
{user_prompt}

(استخدام النظام الأساسي - للحصول على أفضل النتائج، تأكد من GEMINI_API_KEY)"""
        return fallback_plan, False

async def draft_n8n_json_with_ai(plan: str) -> Tuple[str, bool]:
    """إنشاء workflow مخصص متوافق مع n8n Cloud الحديث"""
    try:
        print(f"[INFO] Generating modern n8n workflow...")
        
        # استخراج طلب المستخدم من الخطة
        user_request = plan.split("طلب المستخدم:")[-1].strip()
        
        # تحليل الطلب
        analysis = await enhanced_ai_system.analyze_request_with_ai(user_request)
        
        # تحديد نوع القالب
        services = analysis.get('services', [])
        template_type = "webhook_to_sheets"
        
        if 'gmail' in services:
            template_type = "form_with_email"
        
        print(f"[INFO] Using template: {template_type}")
        print(f"[INFO] Custom data: {json.dumps(analysis, ensure_ascii=False)}")
        
        # إنشاء workflow من القالب الحديث
        if template_type in MODERN_TEMPLATES:
            customized_workflow = MODERN_TEMPLATES[template_type](analysis)
        else:
            customized_workflow = create_modern_webhook_to_sheets(analysis)
        
        print(f"[SUCCESS] Generated modern n8n Cloud compatible workflow using {template_type}")
        final_json = json.dumps(customized_workflow, ensure_ascii=False, indent=2)
        print(f"[INFO] Generated JSON length: {len(final_json)} characters")
        
        return final_json, True
        
    except Exception as e:
        print(f"[ERROR] Modern workflow generation failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        
        # احتياطي حديث
        fallback = create_modern_webhook_to_sheets()
        fallback['name'] = "Enhanced Custom Automation (Fallback)"
        
        return json.dumps(fallback, ensure_ascii=False, indent=2), False

async def test_gemini_connection() -> Dict[str, Any]:
    """اختبار اتصال Gemini"""
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "error": "GEMINI_API_KEY not configured"
        }
    
    try:
        result = await _call_gemini_api("قل 'النظام المحسن مع n8n Cloud يعمل!'")
        return {
            "success": True,
            "response": result,
            "model": GEMINI_MODEL,
            "compatibility": "n8n Cloud Ready"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_available_templates() -> Dict[str, str]:
    """القوالب المتاحة المتوافقة مع n8n Cloud"""
    return {
        "modern_webhook_form": "Modern form with custom fields (n8n Cloud compatible)",
        "service_request_email": "Service request with email automation (n8n Cloud)",
        "enhanced_automation": "Advanced workflow with business logic (n8n Cloud)"
    }

def get_library_stats() -> Dict[str, Any]:
    """إحصائيات المكتبة المحسنة"""
    stats = enhanced_ai_system.library.get_stats()
    stats['compatibility'] = 'n8n Cloud Ready'
    stats['format_version'] = 'Modern'
    return stats

def search_library_candidates(query: str, top_k: int = 3) -> List[Dict]:
    """البحث في المكتبة"""
    return enhanced_ai_system.library.search_workflows(query, max_results=top_k)

# تصدير الوظائف للاستخدام
__all__ = [
    'plan_workflow_with_ai',
    'draft_n8n_json_with_ai', 
    'test_gemini_connection',
    'get_available_templates',
    'get_library_stats',
    'search_library_candidates',
    'enhanced_ai_system'
]
