# library_loader_enhanced.py
import json
import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

class WorkflowsLibraryLoader:
    """محمل مكتبة الـ workflows مع نظام بحث وفهرسة ذكي"""
    
    def __init__(self):
        self.workflows = []
        self.indexed_data = {
            'keywords': {},
            'services': {},
            'triggers': {},
            'patterns': {}
        }
        self.load_workflows_from_files()
    
    def load_workflows_from_files(self):
        """تحميل workflows من مجلد workflows/"""
        workflows_dir = Path("workflows")
        
        if not workflows_dir.exists():
            print("[WARNING] Workflows directory not found")
            return
        
        loaded_count = 0
        for workflow_file in workflows_dir.glob("*.json"):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                    processed_workflow = self.process_workflow(workflow_data, workflow_file.name)
                    if processed_workflow:
                        self.workflows.append(processed_workflow)
                        loaded_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to load {workflow_file}: {e}")
        
        print(f"[SUCCESS] Loaded {loaded_count} workflows from library")
        self.build_index()
    
    def process_workflow(self, raw_workflow: Dict, filename: str) -> Optional[Dict]:
        """معالجة workflow وتحليل محتوياته"""
        try:
            # استخراج المعلومات الأساسية
            name = raw_workflow.get('name', filename.replace('.json', ''))
            nodes = raw_workflow.get('nodes', [])
            
            if not nodes:
                return None
            
            # تحليل العقد والخدمات
            services = self.extract_services(nodes)
            trigger_types = self.extract_triggers(nodes)
            patterns = self.extract_patterns(name, nodes)
            complexity = self.calculate_complexity(nodes)
            
            # استخراج الكلمات المفتاحية من الاسم والوصف
            description = self.generate_description(name, services, trigger_types)
            keywords = self.extract_keywords(name, description, services)
            
            return {
                'filename': filename,
                'name': name,
                'description': description,
                'raw_workflow': raw_workflow,
                'services': services,
                'trigger_types': trigger_types,
                'patterns': patterns,
                'keywords': keywords,
                'complexity': complexity,
                'node_count': len(nodes),
                'active': raw_workflow.get('active', True)
            }
        except Exception as e:
            print(f"[ERROR] Failed to process workflow {filename}: {e}")
            return None
    
    def extract_services(self, nodes: List[Dict]) -> List[str]:
        """استخراج الخدمات المستخدمة من العقد"""
        services = set()
        service_mapping = {
            'googleSheets': 'google-sheets',
            'gmail': 'gmail',
            'slack': 'slack',
            'webhook': 'webhook',
            'httpRequest': 'http',
            'telegram': 'telegram',
            'discord': 'discord',
            'openai': 'openai',
            'airtable': 'airtable',
            'notion': 'notion',
            'wordpress': 'wordpress',
            'shopify': 'shopify',
            'hubspot': 'hubspot',
            'salesforce': 'salesforce',
            'mailchimp': 'mailchimp',
            'twilio': 'twilio'
        }
        
        for node in nodes:
            node_type = node.get('type', '')
            for service_key, service_name in service_mapping.items():
                if service_key.lower() in node_type.lower():
                    services.add(service_name)
                    break
        
        return list(services)
    
    def extract_triggers(self, nodes: List[Dict]) -> List[str]:
        """استخراج أنواع المشغلات"""
        triggers = set()
        trigger_types = {
            'webhook': 'webhook',
            'cron': 'schedule',
            'manualTrigger': 'manual',
            'emailTrigger': 'email',
            'telegram': 'telegram',
            'discord': 'discord'
        }
        
        for node in nodes:
            node_type = node.get('type', '').lower()
            for trigger_key, trigger_name in trigger_types.items():
                if trigger_key.lower() in node_type:
                    triggers.add(trigger_name)
        
        return list(triggers) if triggers else ['manual']
    
    def extract_patterns(self, name: str, nodes: List[Dict]) -> List[str]:
        """استخراج أنماط الاستخدام"""
        patterns = []
        name_lower = name.lower()
        
        # تحليل أنماط شائعة
        if any(word in name_lower for word in ['form', 'contact', 'submission']):
            patterns.append('form_processing')
        
        if any(word in name_lower for word in ['email', 'mail', 'notification']):
            patterns.append('email_automation')
        
        if any(word in name_lower for word in ['schedule', 'daily', 'cron']):
            patterns.append('scheduled_task')
        
        if any(word in name_lower for word in ['chat', 'bot', 'assistant']):
            patterns.append('chatbot')
        
        if any(word in name_lower for word in ['sync', 'integration', 'connect']):
            patterns.append('data_sync')
        
        # تحليل بناءً على العقد
        node_types = [node.get('type', '').lower() for node in nodes]
        
        if any('sheets' in nt for nt in node_types):
            patterns.append('spreadsheet_integration')
        
        if any('ai' in nt or 'openai' in nt for nt in node_types):
            patterns.append('ai_powered')
        
        return patterns
    
    def calculate_complexity(self, nodes: List[Dict]) -> str:
        """حساب مستوى تعقيد الـ workflow"""
        node_count = len(nodes)
        
        # عوامل التعقيد
        complexity_score = node_count
        
        # إضافة نقاط للعقد المعقدة
        for node in nodes:
            node_type = node.get('type', '').lower()
            if any(complex_type in node_type for complex_type in ['function', 'code', 'if', 'switch', 'merge']):
                complexity_score += 2
        
        # تصنيف التعقيد
        if complexity_score <= 5:
            return 'low'
        elif complexity_score <= 15:
            return 'medium'
        else:
            return 'high'
    
    def generate_description(self, name: str, services: List[str], triggers: List[str]) -> str:
        """توليد وصف تلقائي للـ workflow"""
        trigger_desc = triggers[0] if triggers else 'manual'
        services_desc = ', '.join(services[:3]) if services else 'basic operations'
        
        return f"Automated workflow using {trigger_desc} trigger with {services_desc} integration"
    
    def extract_keywords(self, name: str, description: str, services: List[str]) -> List[str]:
        """استخراج الكلمات المفتاحية للفهرسة"""
        keywords = set()
        
        # من الاسم
        name_words = re.findall(r'\w+', name.lower())
        keywords.update(name_words)
        
        # من الوصف
        desc_words = re.findall(r'\w+', description.lower())
        keywords.update(desc_words)
        
        # من الخدمات
        keywords.update(services)
        
        # إزالة كلمات شائعة
        stop_words = {'and', 'or', 'the', 'a', 'an', 'to', 'for', 'with', 'by'}
        keywords = keywords - stop_words
        
        return list(keywords)
    
    def build_index(self):
        """بناء فهرس البحث"""
        for i, workflow in enumerate(self.workflows):
            # فهرسة الكلمات المفتاحية
            for keyword in workflow['keywords']:
                if keyword not in self.indexed_data['keywords']:
                    self.indexed_data['keywords'][keyword] = []
                self.indexed_data['keywords'][keyword].append(i)
            
            # فهرسة الخدمات
            for service in workflow['services']:
                if service not in self.indexed_data['services']:
                    self.indexed_data['services'][service] = []
                self.indexed_data['services'][service].append(i)
            
            # فهرسة المشغلات
            for trigger in workflow['trigger_types']:
                if trigger not in self.indexed_data['triggers']:
                    self.indexed_data['triggers'][trigger] = []
                self.indexed_data['triggers'][trigger].append(i)
            
            # فهرسة الأنماط
            for pattern in workflow['patterns']:
                if pattern not in self.indexed_data['patterns']:
                    self.indexed_data['patterns'][pattern] = []
                self.indexed_data['patterns'][pattern].append(i)
    
    def search_workflows(self, query: str, services: List[str] = None, 
                        trigger_type: str = None, max_results: int = 10) -> List[Dict]:
        """البحث الذكي في مكتبة الـ workflows"""
        if not query.strip() and not services and not trigger_type:
            return self.workflows[:max_results]
        
        scores = {}
        
        # البحث النصي
        if query.strip():
            query_words = re.findall(r'\w+', query.lower())
            for word in query_words:
                # بحث دقيق
                if word in self.indexed_data['keywords']:
                    for idx in self.indexed_data['keywords'][word]:
                        scores[idx] = scores.get(idx, 0) + 3
                
                # بحث جزئي
                for keyword, indices in self.indexed_data['keywords'].items():
                    if word in keyword or keyword in word:
                        for idx in indices:
                            scores[idx] = scores.get(idx, 0) + 1
        
        # فلترة بناءً على الخدمات
        if services:
            service_indices = set()
            for service in services:
                if service in self.indexed_data['services']:
                    service_indices.update(self.indexed_data['services'][service])
            
            if service_indices:
                for idx in service_indices:
                    scores[idx] = scores.get(idx, 0) + 5
        
        # فلترة بناءً على نوع المشغل
        if trigger_type and trigger_type in self.indexed_data['triggers']:
            for idx in self.indexed_data['triggers'][trigger_type]:
                scores[idx] = scores.get(idx, 0) + 3
        
        # ترتيب النتائج
        if not scores:
            return self.workflows[:max_results]
        
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in sorted_results[:max_results]:
            workflow = self.workflows[idx].copy()
            workflow['relevance_score'] = score
            results.append(workflow)
        
        return results
    
    def get_best_template_for_analysis(self, analysis_data: Dict) -> Optional[Dict]:
        """اختيار أفضل قالب بناءً على التحليل"""
        services = analysis_data.get('services', [])
        trigger_type = analysis_data.get('trigger_type', '')
        operations = analysis_data.get('operations', [])
        
        # بناء استعلام البحث
        search_query = ' '.join(operations + services)
        
        # البحث عن templates مناسبة
        candidates = self.search_workflows(
            query=search_query,
            services=services,
            trigger_type=trigger_type,
            max_results=5
        )
        
        if candidates:
            # اختيار الأفضل بناءً على التطابق
            best_match = candidates[0]
            return best_match
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """إحصائيات المكتبة"""
        total_workflows = len(self.workflows)
        active_workflows = sum(1 for w in self.workflows if w['active'])
        unique_services = len(self.indexed_data['services'])
        
        complexity_dist = {}
        for workflow in self.workflows:
            complexity = workflow['complexity']
            complexity_dist[complexity] = complexity_dist.get(complexity, 0) + 1
        
        return {
            'total_workflows': total_workflows,
            'active_workflows': active_workflows,
            'unique_services': unique_services,
            'complexity_distribution': complexity_dist,
            'available_services': list(self.indexed_data['services'].keys()),
            'available_triggers': list(self.indexed_data['triggers'].keys()),
            'available_patterns': list(self.indexed_data['patterns'].keys())
        }

# تحديث ai.py مع النظام الجديد
class EnhancedAISystem:
    """نظام AI محسن مع مكتبة workflows"""
    
    def __init__(self):
        self.library_loader = WorkflowsLibraryLoader()
        
    async def plan_workflow_with_library(self, user_prompt: str) -> Tuple[str, bool]:
        """تخطيط workflow مع الاستفادة من المكتبة"""
        try:
            # تحليل الطلب
            analysis = await self.analyze_request_with_ai(user_prompt)
            
            # البحث في المكتبة
            relevant_workflows = self.library_loader.search_workflows(
                query=user_prompt,
                services=analysis.get('services', []),
                trigger_type=analysis.get('trigger_type'),
                max_results=5
            )
            
            # تحضير تقرير شامل
            plan = self.create_comprehensive_plan(user_prompt, analysis, relevant_workflows)
            
            return plan, True
            
        except Exception as e:
            print(f"[ERROR] Enhanced planning failed: {e}")
            return f"تحليل أساسي: {user_prompt}", False
    
    async def analyze_request_with_ai(self, user_prompt: str) -> Dict[str, Any]:
        """تحليل الطلب باستخدام AI"""
        analysis_prompt = f"""
حلل هذا الطلب بعمق:
"{user_prompt}"

استخرج:
1. نوع المشغل (webhook/schedule/manual)
2. الخدمات المطلوبة
3. العمليات المطلوبة
4. الأسماء المخصصة
5. منطق العمل

أجب بـ JSON صالح:
{{
  "trigger_type": "...",
  "services": ["..."],
  "operations": ["..."],
  "custom_names": {{}},
  "business_logic": ["..."],
  "data_fields": {{}}
}}
"""
        
        try:
            response = await _call_gemini_api(analysis_prompt, ADVANCED_ANALYZER_PROMPT)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"[WARNING] AI analysis failed: {e}")
        
        # تحليل احتياطي
        return self.fallback_analysis(user_prompt)
    
    def fallback_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """تحليل احتياطي بسيط"""
        text = user_prompt.lower()
        
        # تحديد نوع المشغل
        if any(word in text for word in ['form', 'submit', 'webhook']):
            trigger = 'webhook'
        elif any(word in text for word in ['schedule', 'daily', 'every']):
            trigger = 'schedule'
        else:
            trigger = 'manual'
        
        # تحديد الخدمات
        services = []
        if 'sheets' in text or 'جدول' in text:
            services.append('google-sheets')
        if 'email' in text or 'gmail' in text:
            services.append('gmail')
        if 'slack' in text:
            services.append('slack')
        
        return {
            'trigger_type': trigger,
            'services': services,
            'operations': ['data_processing'],
            'custom_names': {},
            'business_logic': [],
            'data_fields': {}
        }
    
    def create_comprehensive_plan(self, user_prompt: str, analysis: Dict, 
                                 relevant_workflows: List[Dict]) -> str:
        """إنشاء خطة شاملة"""
        plan_parts = [
            "🔍 **تحليل شامل للطلب:**",
            "",
            f"**نوع المشغل:** {analysis.get('trigger_type', 'غير محدد')}",
            f"**الخدمات:** {', '.join(analysis.get('services', ['أساسية']))}",
            f"**العمليات:** {', '.join(analysis.get('operations', ['معالجة بيانات']))}",
        ]
        
        if analysis.get('custom_names'):
            plan_parts.extend([
                "",
                "**الأسماء المخصصة:**",
                json.dumps(analysis['custom_names'], ensure_ascii=False, indent=2)
            ])
        
        if relevant_workflows:
            plan_parts.extend([
                "",
                f"**workflows مشابهة في المكتبة ({len(relevant_workflows)}):**"
            ])
            
            for i, workflow in enumerate(relevant_workflows[:3], 1):
                plan_parts.append(f"{i}. {workflow['name']} (مطابقة: {workflow.get('relevance_score', 0)})")
        
        plan_parts.extend([
            "",
            "**طلب المستخدم الأصلي:**",
            user_prompt
        ])
        
        return "\n".join(plan_parts)
    
    async def generate_custom_workflow(self, plan: str) -> Tuple[str, bool]:
        """توليد workflow مخصص محسن"""
        try:
            # استخراج المعلومات من الخطة
            user_request = plan.split("طلب المستخدم الأصلي:")[-1].strip()
            analysis = await self.analyze_request_with_ai(user_request)
            
            # البحث عن أفضل قالب
            best_template = self.library_loader.get_best_template_for_analysis(analysis)
            
            if best_template:
                # تخصيص القالب
                customized_workflow = self.customize_workflow_from_template(
                    best_template['raw_workflow'], 
                    analysis
                )
                print(f"[SUCCESS] Customized workflow from template: {best_template['name']}")
            else:
                # إنشاء workflow جديد
                customized_workflow = self.create_new_workflow(analysis)
                print("[SUCCESS] Created new custom workflow")
            
            return json.dumps(customized_workflow, ensure_ascii=False, indent=2), True
            
        except Exception as e:
            print(f"[ERROR] Custom workflow generation failed: {e}")
            # إرجاع workflow احتياطي
            fallback = self.create_fallback_workflow()
            return json.dumps(fallback, ensure_ascii=False, indent=2), False
    
    def customize_workflow_from_template(self, template: Dict[str, Any], 
                                       analysis: Dict[str, Any]) -> Dict[str, Any]:
        """تخصيص workflow من قالب موجود"""
        customized = copy.deepcopy(template)
        
        # تحديث معلومات أساسية
        customized['name'] = self.generate_custom_name(analysis)
        customized['updatedAt'] = datetime.now().isoformat()
        
        # تخصيص العقد
        for node in customized.get('nodes', []):
            self.customize_node_parameters(node, analysis)
        
        # إضافة عقد جديدة حسب الحاجة
        self.add_missing_nodes(customized, analysis)
        
        # تحديث الاتصالات
        self.update_workflow_connections(customized)
        
        return customized
    
    def customize_node_parameters(self, node: Dict[str, Any], analysis: Dict[str, Any]):
        """تخصيص parameters العقدة"""
        node_type = node.get('type', '').lower()
        
        if 'googlesheets' in node_type:
            self.customize_sheets_node(node, analysis)
        elif 'gmail' in node_type:
            self.customize_gmail_node(node, analysis)
        elif 'slack' in node_type:
            self.customize_slack_node(node, analysis)
    
    def customize_sheets_node(self, node: Dict[str, Any], analysis: Dict[str, Any]):
        """تخصيص عقدة Google Sheets"""
        params = node.setdefault('parameters', {})
        
        # استخدام أسماء مخصصة
        custom_names = analysis.get('custom_names', {})
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
            for field, description in data_fields.items():
                column_name = description.title() if description else field.title()
                columns[column_name] = f"={{{{ $json.{field} }}}}"
            
            # إضافة حقول تلقائية
            if 'generate_id' in analysis.get('business_logic', []):
                columns['Request_ID'] = "={{ 'REQ-' + new Date().getTime().toString() }}"
            
            columns['Timestamp'] = "={{ new Date().toISOString() }}"
            
            params['columns'] = {
                "mappingMode": "defineBelow",
                "value": columns
            }
    
    def generate_custom_name(self, analysis: Dict[str, Any]) -> str:
        """توليد اسم مخصص للـ workflow"""
        trigger = analysis.get('trigger_type', 'automation')
        services = analysis.get('services', [])
        
        name_parts = []
        
        if trigger == 'webhook':
            name_parts.append('Form')
        elif trigger == 'schedule':
            name_parts.append('Scheduled')
        
        if 'google-sheets' in services:
            name_parts.append('to Sheets')
        if 'gmail' in services:
            name_parts.append('with Email')
        
        # إضافة تخصيص
        custom_names = analysis.get('custom_names', {})
        if custom_names:
            first_custom = list(custom_names.values())[0]
            name_parts.append(f'({first_custom})')
        
        return ' '.join(name_parts) if name_parts else 'Custom Automation'

# Singleton instance
enhanced_ai_system = EnhancedAISystem()

# تحديث الوظائف الرئيسية لاستخدام النظام المحسن
async def plan_workflow_with_ai(user_prompt: str) -> Tuple[str, bool]:
    """استخدام النظام المحسن للتخطيط"""
    return await enhanced_ai_system.plan_workflow_with_library(user_prompt)

async def draft_n8n_json_with_ai(plan: str) -> Tuple[str, bool]:
    """استخدام النظام المحسن للتوليد"""
    return await enhanced_ai_system.generate_custom_workflow(plan)

def search_library_candidates(query: str, top_k: int = 3) -> List[Dict]:
    """البحث في المكتبة المحسنة"""
    return enhanced_ai_system.library_loader.search_workflows(query, max_results=top_k)

def get_library_stats() -> Dict[str, Any]:
    """إحصائيات المكتبة"""
    return enhanced_ai_system.library_loader.get_stats()
