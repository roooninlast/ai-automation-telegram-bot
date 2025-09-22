import os, json, httpx, re
from typing import Dict, Any, Tuple, List, Optional
import copy
import uuid
from datetime import datetime
from dataclasses import dataclass

# إعدادات Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

@dataclass
class WorkflowAnalysis:
    """تحليل شامل لطلب المستخدم"""
    trigger_type: str
    services: List[str]
    operations: List[str]
    data_fields: Dict[str, str]
    custom_names: Dict[str, str]  # أسماء مخصصة للجداول، القنوات، إلخ
    business_logic: List[str]
    complexity_score: int
    confidence_level: str
    suggested_templates: List[str]

# نظام تحليل الطلبات المتقدم
ADVANCED_ANALYZER_PROMPT = """أنت خبير في تحليل طلبات الأتمتة وتحويلها لـ workflows n8n عالية الجودة.

مهمتك: تحليل الطلب بعمق شديد واستخراج كل التفاصيل المطلوبة.

استخرج:
1. نوع التشغيل (webhook/schedule/manual/email)
2. الخدمات المطلوبة مع تفاصيلها
3. أسماء مخصصة (جداول، قنوات، حقول)
4. منطق العمل والشروط
5. البيانات المطلوب معالجتها
6. التخصيصات المطلوبة

أجب بتنسيق JSON دقيق:
{
  "trigger_type": "...",
  "services": ["service1", "service2"],
  "operations": ["operation1", "operation2"],
  "data_fields": {"field1": "description", "field2": "description"},
  "custom_names": {"sheet_name": "العملاء الجدد", "channel": "#sales"},
  "business_logic": ["generate unique ID", "send welcome message"],
  "complexity_score": 1-10,
  "confidence_level": "high/medium/low",
  "suggested_templates": ["template1", "template2"]
}

كن دقيقاً جداً في استخراج الأسماء المخصصة والتفاصيل."""

WORKFLOW_CUSTOMIZER_PROMPT = """أنت مطور workflows خبير في n8n. مهمتك إنشاء workflow مخصص 100% حسب التحليل.

قواعد التخصيص المتقدمة:
1. اربط كل عقدة بالتحليل المقدم
2. خصص parameters بناءً على التفاصيل المحددة
3. أضف عقد إضافية حسب الحاجة (Set, Function, IF)
4. استخدم الأسماء المخصصة من التحليل
5. طبق منطق العمل المطلوب
6. أضف معالجة أخطاء متقدمة

أنتج JSON كامل وصالح للاستيراد في n8n.
استخدم أحدث إصدارات العقد وأفضل الممارسات."""

class AdvancedWorkflowLibrary:
    """مكتبة workflows متقدمة مع نظام بحث ذكي"""
    
    def __init__(self):
        self.workflows = []
        self.indexed_patterns = {}
        self.load_library()
    
    def load_library(self):
        """تحميل مكتبة الـ 100 workflow"""
        try:
            # تحميل من ملف JSON أو قاعدة البيانات
            library_path = os.path.join(os.path.dirname(__file__), "workflows_library.json")
            if os.path.exists(library_path):
                with open(library_path, "r", encoding="utf-8") as f:
                    self.workflows = json.load(f)
                self.index_workflows()
                print(f"[INFO] Loaded {len(self.workflows)} workflows from library")
            else:
                print("[WARNING] Workflows library not found, creating sample data")
                self.create_sample_library()
        except Exception as e:
            print(f"[ERROR] Failed to load workflows library: {e}")
            self.create_sample_library()
    
    def create_sample_library(self):
        """إنشاء عينة من المكتبة للاختبار"""
        self.workflows = [
            {
                "name": "Advanced Contact Form with Email Automation",
                "description": "Webhook receives form data, saves to custom Google Sheet, sends personalized email with ticket number",
                "tags": ["webhook", "google-sheets", "gmail", "form", "automation"],
                "trigger_types": ["webhook"],
                "services": ["google-sheets", "gmail"],
                "complexity": "medium",
                "pattern_keywords": ["form", "contact", "email", "sheet", "ticket", "number"],
                "json_template": {
                    # Template workflow structure...
                }
            }
            # المزيد من الـ workflows...
        ]
        self.index_workflows()
    
    def index_workflows(self):
        """فهرسة الـ workflows للبحث السريع"""
        self.indexed_patterns = {}
        for i, workflow in enumerate(self.workflows):
            # فهرسة بناءً على الكلمات المفتاحية
            for keyword in workflow.get("pattern_keywords", []):
                if keyword not in self.indexed_patterns:
                    self.indexed_patterns[keyword] = []
                self.indexed_patterns[keyword].append(i)
    
    def find_relevant_workflows(self, analysis: WorkflowAnalysis, max_results=5) -> List[Dict]:
        """البحث عن workflows مناسبة بناءً على التحليل"""
        relevant = []
        scores = {}
        
        # البحث في الفهرس
        search_terms = (
            analysis.services + 
            analysis.operations + 
            [analysis.trigger_type] +
            list(analysis.custom_names.keys()) +
            list(analysis.custom_names.values())
        )
        
        for term in search_terms:
            term_lower = term.lower()
            for keyword, workflow_indices in self.indexed_patterns.items():
                if term_lower in keyword.lower() or keyword.lower() in term_lower:
                    for idx in workflow_indices:
                        if idx not in scores:
                            scores[idx] = 0
                        scores[idx] += 1
        
        # ترتيب النتائج وإرجاع الأفضل
        sorted_workflows = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for idx, score in sorted_workflows[:max_results]:
            workflow = copy.deepcopy(self.workflows[idx])
            workflow["relevance_score"] = score
            relevant.append(workflow)
        
        return relevant

class AdvancedN8NBuilder:
    """بناء workflows n8n متقدمة ومخصصة"""
    
    def __init__(self):
        self.library = AdvancedWorkflowLibrary()
    
    def build_custom_workflow(self, analysis: WorkflowAnalysis, relevant_workflows: List[Dict]) -> Dict[str, Any]:
        """بناء workflow مخصص بناءً على التحليل والمراجع"""
        
        # اختيار أفضل قالب كأساس
        base_template = self._select_best_template(analysis, relevant_workflows)
        
        # تخصيص الـ workflow
        customized = self._customize_workflow(base_template, analysis)
        
        # إضافة عقد إضافية حسب الحاجة
        enhanced = self._enhance_workflow(customized, analysis)
        
        # التحقق النهائي والتنظيف
        final_workflow = self._finalize_workflow(enhanced, analysis)
        
        return final_workflow
    
    def _select_best_template(self, analysis: WorkflowAnalysis, relevant_workflows: List[Dict]) -> Dict[str, Any]:
        """اختيار أفضل قالب أساسي"""
        if relevant_workflows:
            # استخدام الأكثر ملاءمة من المكتبة
            best_match = relevant_workflows[0]
            return best_match.get("json_template", self._get_fallback_template(analysis))
        else:
            # استخدام قالب احتياطي
            return self._get_fallback_template(analysis)
    
    def _get_fallback_template(self, analysis: WorkflowAnalysis) -> Dict[str, Any]:
        """قالب احتياطي أساسي"""
        if analysis.trigger_type == "webhook" and "google-sheets" in analysis.services:
            return self._create_webhook_sheets_template()
        elif analysis.trigger_type == "schedule":
            return self._create_schedule_template()
        else:
            return self._create_minimal_template()
    
    def _customize_workflow(self, template: Dict[str, Any], analysis: WorkflowAnalysis) -> Dict[str, Any]:
        """تخصيص شامل للـ workflow"""
        workflow = copy.deepcopy(template)
        
        # تحديث معلومات الـ workflow
        workflow["name"] = self._generate_workflow_name(analysis)
        workflow["updatedAt"] = datetime.now().isoformat()
        
        # تخصيص العقد
        for node in workflow.get("nodes", []):
            self._customize_node(node, analysis)
        
        return workflow
    
    def _customize_node(self, node: Dict[str, Any], analysis: WorkflowAnalysis):
        """تخصيص عقدة واحدة بناءً على التحليل"""
        node_type = node.get("type", "")
        
        if "googleSheets" in node_type:
            self._customize_sheets_node(node, analysis)
        elif "gmail" in node_type:
            self._customize_gmail_node(node, analysis)
        elif "slack" in node_type:
            self._customize_slack_node(node, analysis)
        elif "webhook" in node_type:
            self._customize_webhook_node(node, analysis)
    
    def _customize_sheets_node(self, node: Dict[str, Any], analysis: WorkflowAnalysis):
        """تخصيص عقدة Google Sheets"""
        params = node.setdefault("parameters", {})
        
        # استخدام اسم الجدول المخصص
        if "sheet_name" in analysis.custom_names:
            params["sheetName"] = {
                "__rl": True,
                "value": analysis.custom_names["sheet_name"],
                "mode": "list"
            }
        
        # تخصيص الأعمدة بناءً على البيانات المطلوبة
        if analysis.data_fields:
            columns_mapping = {}
            for field_key, field_desc in analysis.data_fields.items():
                # تحويل اسم الحقل لاسم عمود مناسب
                column_name = field_desc.title() if field_desc else field_key.title()
                columns_mapping[column_name] = f"={{{{ $json.{field_key} }}}}"
            
            # إضافة حقول إضافية حسب منطق العمل
            if "generate unique ID" in analysis.business_logic:
                columns_mapping["Request_ID"] = "={{ 'REQ-' + new Date().getTime().toString() }}"
            
            if "timestamp" not in columns_mapping:
                columns_mapping["Timestamp"] = "={{ new Date().toISOString() }}"
            
            params["columns"] = {
                "mappingMode": "defineBelow",
                "value": columns_mapping,
                "matchingColumns": [],
                "schema": []
            }
    
    def _customize_gmail_node(self, node: Dict[str, Any], analysis: WorkflowAnalysis):
        """تخصيص عقدة Gmail"""
        params = node.setdefault("parameters", {})
        
        # تخصيص موضوع الرسالة
        if "welcome" in analysis.business_logic:
            params["subject"] = "مرحباً بك! تم استلام طلبك"
        
        # تخصيص محتوى الرسالة بناءً على البيانات
        message_parts = ["عزيزي/عزيزتي {{ $json.name || 'العميل' }}،\n\n"]
        
        if "generate unique ID" in analysis.business_logic:
            message_parts.append("رقم طلبك: {{ 'REQ-' + new Date().getTime().toString() }}\n\n")
        
        message_parts.extend([
            "شكراً لك على تواصلك معنا. سيتم الرد عليك قريباً.\n\n",
            "تفاصيل طلبك:\n"
        ])
        
        # إضافة تفاصيل الطلب
        for field_key, field_desc in analysis.data_fields.items():
            if field_key != "name":
                message_parts.append(f"- {field_desc}: {{{{ $json.{field_key} }}}}\n")
        
        message_parts.append("\n\nمع أطيب التحيات،\nفريق الدعم")
        
        params["message"] = "".join(message_parts)
    
    def _enhance_workflow(self, workflow: Dict[str, Any], analysis: WorkflowAnalysis) -> Dict[str, Any]:
        """تحسين الـ workflow بإضافة عقد إضافية"""
        
        # إضافة عقدة Set لمعالجة البيانات إذا لزم الأمر
        if self._needs_data_processing(analysis):
            self._add_set_node(workflow, analysis)
        
        # إضافة عقدة IF للشروط المنطقية
        if self._needs_conditional_logic(analysis):
            self._add_if_node(workflow, analysis)
        
        # إضافة معالجة الأخطاء
        self._add_error_handling(workflow)
        
        return workflow
    
    def _needs_data_processing(self, analysis: WorkflowAnalysis) -> bool:
        """تحديد إذا كان هناك حاجة لمعالجة البيانات"""
        return any(logic in analysis.business_logic for logic in 
                  ["generate unique ID", "transform data", "calculate", "format"])
    
    def _add_set_node(self, workflow: Dict[str, Any], analysis: WorkflowAnalysis):
        """إضافة عقدة Set لمعالجة البيانات"""
        set_node = {
            "parameters": {
                "values": {},
                "options": {}
            },
            "id": str(uuid.uuid4())[:8],
            "name": "Process Data",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3,
            "position": [340, 300]
        }
        
        # تكوين القيم المطلوب معالجتها
        values = {}
        if "generate unique ID" in analysis.business_logic:
            values["request_id"] = "={{ 'REQ-' + new Date().getTime().toString() }}"
        
        set_node["parameters"]["values"] = {"string": [{"name": k, "value": v} for k, v in values.items()]}
        
        # إدراج العقدة في الموقع المناسب
        workflow["nodes"].insert(1, set_node)
        self._update_connections_for_new_node(workflow, set_node["id"], 1)
    
    def _finalize_workflow(self, workflow: Dict[str, Any], analysis: WorkflowAnalysis) -> Dict[str, Any]:
        """التشطيب النهائي للـ workflow"""
        
        # تحديث معرفات العقد
        self._update_node_ids(workflow)
        
        # تحديث الاتصالات
        self._validate_connections(workflow)
        
        # إضافة metadata
        workflow.setdefault("tags", []).extend(analysis.services)
        workflow["description"] = f"Custom workflow for: {', '.join(analysis.operations)}"
        
        return workflow
    
    # Helper methods for template creation
    def _create_webhook_sheets_template(self) -> Dict[str, Any]:
        """قالب webhook إلى sheets أساسي"""
        return {
            "active": True,
            "connections": {},
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "id": "1",
            "name": "Custom Webhook to Sheets",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "contact-form",
                        "responseMode": "onReceived",
                        "options": {}
                    },
                    "id": str(uuid.uuid4())[:8],
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "webhookId": str(uuid.uuid4())[:8]
                }
            ],
            "pinData": {},
            "settings": {"executionOrder": "v1"},
            "staticData": {},
            "tags": [],
            "triggerCount": 1,
            "versionId": "1"
        }
    
    def _generate_workflow_name(self, analysis: WorkflowAnalysis) -> str:
        """توليد اسم مناسب للـ workflow"""
        name_parts = []
        
        if analysis.trigger_type == "webhook":
            name_parts.append("Form")
        elif analysis.trigger_type == "schedule":
            name_parts.append("Scheduled")
        
        if "google-sheets" in analysis.services:
            name_parts.append("to Sheets")
        
        if "gmail" in analysis.services:
            name_parts.append("with Email")
        
        if "slack" in analysis.services:
            name_parts.append("Slack Notification")
        
        # إضافة التخصيص إذا وجد
        if analysis.custom_names:
            custom_part = list(analysis.custom_names.values())[0]
            name_parts.append(f"({custom_part})")
        
        return " ".join(name_parts) or "Custom Automation"

async def _call_gemini_api(prompt: str, system_instruction: str = "") -> str:
    """استدعاء Gemini API محسن"""
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
            "temperature": 0.1,  # أقل للحصول على نتائج أكثر دقة
            "maxOutputTokens": 4000,  # أكثر للـ workflows المعقدة
            "topP": 0.8,
            "topK": 40
        }
    }
    
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(url, json=payload)
        
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API returned {response.status_code}")
        
        data = response.json()
        
        if not data.get("candidates") or not data["candidates"][0].get("content"):
            raise RuntimeError("No valid response from Gemini")
        
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

async def analyze_user_request_advanced(user_prompt: str) -> WorkflowAnalysis:
    """تحليل متقدم لطلب المستخدم"""
    try:
        analysis_prompt = f"""
طلب المستخدم: "{user_prompt}"

حلل هذا الطلب بعمق واستخرج كل التفاصيل المطلوبة.
ركز على:
- الأسماء المحددة (أسماء الجداول، القنوات، الحقول)
- منطق العمل المطلوب
- البيانات المطلوب معالجتها
- التخصيصات المحددة

أجب بـ JSON صالح فقط بدون أي نص إضافي.
"""
        
        response = await _call_gemini_api(analysis_prompt, ADVANCED_ANALYZER_PROMPT)
        
        # استخراج JSON من الاستجابة
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            analysis_data = json.loads(json_match.group())
            return WorkflowAnalysis(**analysis_data)
        else:
            raise ValueError("Failed to extract JSON from AI response")
            
    except Exception as e:
        print(f"[WARNING] Advanced analysis failed: {e}")
        # تحليل احتياطي مبسط
        return _fallback_analysis(user_prompt)

def _fallback_analysis(user_prompt: str) -> WorkflowAnalysis:
    """تحليل احتياطي مبسط"""
    return WorkflowAnalysis(
        trigger_type="webhook",
        services=["google-sheets"] if "sheet" in user_prompt.lower() else ["basic"],
        operations=["save_data"],
        data_fields={"name": "Name", "email": "Email", "message": "Message"},
        custom_names={},
        business_logic=[],
        complexity_score=5,
        confidence_level="medium",
        suggested_templates=["webhook_to_sheets"]
    )

async def plan_workflow_with_ai_advanced(user_prompt: str) -> Tuple[str, bool]:
    """تخطيط workflow متقدم"""
    try:
        print(f"[INFO] Advanced analysis starting: {user_prompt[:100]}...")
        
        # تحليل شامل للطلب
        analysis = await analyze_user_request_advanced(user_prompt)
        
        # تحضير تقرير التحليل
        plan = f"""🔍 **تحليل متقدم للطلب:**

**نوع التشغيل:** {analysis.trigger_type}
**الخدمات المطلوبة:** {', '.join(analysis.services)}
**العمليات:** {', '.join(analysis.operations)}

**الأسماء المخصصة:**
{json.dumps(analysis.custom_names, ensure_ascii=False, indent=2) if analysis.custom_names else 'لا توجد أسماء مخصصة'}

**حقول البيانات:**
{json.dumps(analysis.data_fields, ensure_ascii=False, indent=2)}

**منطق العمل:**
{chr(10).join(f"- {logic}" for logic in analysis.business_logic) if analysis.business_logic else 'منطق أساسي'}

**مستوى التعقيد:** {analysis.complexity_score}/10
**مستوى الثقة:** {analysis.confidence_level}

**طلب المستخدم الأصلي:**
{user_prompt}
"""
        
        return plan, True
        
    except Exception as e:
        print(f"[ERROR] Advanced planning failed: {e}")
        # خطة احتياطية
        return f"تحليل احتياطي للطلب: {user_prompt}", False

async def draft_n8n_json_with_ai_advanced(plan: str) -> Tuple[str, bool]:
    """إنشاء workflow متقدم ومخصص"""
    try:
        # استخراج التحليل من الخطة
        analysis = await analyze_user_request_advanced(plan.split("طلب المستخدم الأصلي:")[-1].strip())
        
        # إنشاء builder متقدم
        builder = AdvancedN8NBuilder()
        
        # البحث عن workflows مناسبة في المكتبة
        relevant_workflows = builder.library.find_relevant_workflows(analysis)
        
        print(f"[INFO] Found {len(relevant_workflows)} relevant workflows in library")
        
        # بناء workflow مخصص
        custom_workflow = builder.build_custom_workflow(analysis, relevant_workflows)
        
        print("[SUCCESS] Generated advanced custom n8n workflow")
        return json.dumps(custom_workflow, ensure_ascii=False, indent=2), True
        
    except Exception as e:
        print(f"[ERROR] Advanced workflow generation failed: {e}")
        
        # إنشاء workflow احتياطي محسن
        fallback_workflow = _create_enhanced_fallback()
        return json.dumps(fallback_workflow, ensure_ascii=False, indent=2), False

def _create_enhanced_fallback() -> Dict[str, Any]:
    """إنشاء workflow احتياطي محسن"""
    return {
        "active": True,
        "connections": {
            "webhook_node": {
                "main": [[{"node": "process_node", "type": "main", "index": 0}]]
            },
            "process_node": {
                "main": [[{"node": "sheets_node", "type": "main", "index": 0}]]
            }
        },
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "id": "1",
        "name": "Enhanced Custom Automation",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "custom-form",
                    "responseMode": "onReceived"
                },
                "id": "webhook_node",
                "name": "Custom Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "values": {
                        "string": [
                            {"name": "request_id", "value": "={{ 'REQ-' + new Date().getTime().toString() }}"},
                            {"name": "processed_at", "value": "={{ new Date().toISOString() }}"}
                        ]
                    }
                },
                "id": "process_node",
                "name": "Process Data",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "resource": "sheet",
                    "operation": "appendOrUpdate",
                    "documentId": {"__rl": True, "value": "={{$env.GOOGLE_SHEET_ID}}", "mode": "id"},
                    "sheetName": {"__rl": True, "value": "Custom Data", "mode": "list"},
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "Request_ID": "={{ $('Process Data').item.json.request_id }}",
                            "Name": "={{ $json.name }}",
                            "Email": "={{ $json.email }}",
                            "Message": "={{ $json.message }}",
                            "Processed_At": "={{ $('Process Data').item.json.processed_at }}"
                        }
                    }
                },
                "id": "sheets_node",
                "name": "Save to Custom Sheet",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [680, 300]
            }
        ],
        "settings": {"executionOrder": "v1"},
        "staticData": {},
        "tags": ["custom", "enhanced"],
        "triggerCount": 1,
        "versionId": "1"
    }

# تحديث باقي الوظائف
async def test_gemini_connection() -> Dict[str, Any]:
    """اختبار الاتصال مع Gemini API"""
    if not GEMINI_API_KEY:
        return {"success": False, "error": "GEMINI_API_KEY not configured"}
    
    try:
        result = await _call_gemini_api("قل 'النظام المتقدم يعمل بشكل مثالي!'")
        return {"success": True, "response": result, "model": GEMINI_MODEL}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_available_templates() -> Dict[str, str]:
    """الحصول على قائمة القوالب المتاحة"""
    return {
        "advanced_form_automation": "Advanced form with custom fields and email automation",
        "scheduled_reporting": "Intelligent scheduled reports with data processing", 
        "multi_service_integration": "Complex workflows connecting multiple services",
        "conditional_automation": "Smart automation with business logic and conditions"
    }
