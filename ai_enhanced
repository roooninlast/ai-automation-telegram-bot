# enhanced_ai_system.py - Advanced AI System with Internet Research
import os, json, httpx, re, asyncio
from typing import Dict, Any, Tuple, List, Optional
import copy
import uuid
from datetime import datetime
from urllib.parse import quote

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

class EnhancedWorkflowGenerator:
    """Advanced workflow generator with internet research capabilities"""
    
    def __init__(self):
        self.search_engines = [
            "https://www.google.com/search?q=",
            "https://duckduckgo.com/?q="
        ]
        self.n8n_resources = [
            "n8n.io/workflows",
            "github.com n8n workflow",
            "n8n community examples",
            "n8n automation examples"
        ]
    
    async def analyze_user_request(self, user_description: str) -> Dict[str, Any]:
        """Deep analysis of user request using AI"""
        
        analysis_prompt = f"""
Analyze this automation request in detail:
"{user_description}"

Extract and return JSON with:
{{
  "intent": "what user wants to achieve",
  "trigger_type": "webhook/schedule/email/manual",
  "services_needed": ["service1", "service2"],
  "data_flow": "description of data transformation",
  "business_rules": ["rule1", "rule2"],
  "custom_requirements": {{"names": [], "fields": [], "logic": []}},
  "complexity": "simple/medium/complex",
  "search_keywords": ["keyword1", "keyword2"],
  "similar_use_cases": ["use_case1", "use_case2"]
}}
"""
        
        if OPENROUTER_API_KEY:
            try:
                response = await self._call_openrouter_api(analysis_prompt)
                return self._parse_json_response(response)
            except Exception as e:
                print(f"[WARNING] AI analysis failed: {e}")
        
        return self._fallback_analysis(user_description)
    
    async def research_automation_examples(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Research internet for similar automation examples"""
        
        search_queries = self._generate_search_queries(analysis)
        research_results = []
        
        for query in search_queries[:3]:  # Limit to 3 searches
            try:
                results = await self._search_internet(query)
                research_results.extend(results)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"[WARNING] Search failed for '{query}': {e}")
        
        # Filter and rank results
        return self._filter_relevant_results(research_results, analysis)
    
    async def generate_custom_workflow(self, analysis: Dict[str, Any], research_results: List[Dict]) -> Dict[str, Any]:
        """Generate custom n8n workflow based on analysis and research"""
        
        # Create generation prompt with research context
        generation_prompt = self._build_generation_prompt(analysis, research_results)
        
        if OPENROUTER_API_KEY:
            try:
                workflow_json = await self._call_openrouter_api(generation_prompt)
                return self._parse_workflow_json(workflow_json)
            except Exception as e:
                print(f"[WARNING] AI generation failed: {e}")
        
        # Fallback to template-based generation
        return self._generate_from_template(analysis)
    
    def _generate_search_queries(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate targeted search queries"""
        
        base_keywords = analysis.get("search_keywords", [])
        services = analysis.get("services_needed", [])
        intent = analysis.get("intent", "")
        
        queries = []
        
        # n8n specific searches
        queries.extend([
            f"n8n workflow {' '.join(base_keywords[:2])}",
            f"n8n automation {intent[:50]}",
            f"n8n {' '.join(services[:2])} integration example"
        ])
        
        # General automation searches
        queries.extend([
            f"automation workflow {' '.join(base_keywords[:3])}",
            f"zapier workflow {intent[:50]}",
            f"{' '.join(services)} automation tutorial"
        ])
        
        return queries[:5]
    
    async def _search_internet(self, query: str) -> List[Dict[str, Any]]:
        """Search internet for automation examples"""
        
        # Use DuckDuckGo API or similar search service
        search_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_redirect=1&no_html=1"
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    # Parse search results
                    for item in data.get("RelatedTopics", [])[:5]:
                        if "Text" in item and "FirstURL" in item:
                            results.append({
                                "title": item.get("Text", "")[:100],
                                "url": item.get("FirstURL", ""),
                                "snippet": item.get("Text", "")[:300],
                                "relevance_score": 0.5
                            })
                    
                    return results
                
        except Exception as e:
            print(f"[ERROR] Search request failed: {e}")
        
        return []
    
    def _filter_relevant_results(self, results: List[Dict], analysis: Dict) -> List[Dict]:
        """Filter and rank search results by relevance"""
        
        keywords = analysis.get("search_keywords", [])
        services = analysis.get("services_needed", [])
        
        filtered_results = []
        
        for result in results:
            text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
            
            # Calculate relevance score
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 2
            
            for service in services:
                if service.lower() in text:
                    score += 3
            
            if "n8n" in text:
                score += 5
            if "workflow" in text:
                score += 2
            
            result["relevance_score"] = score
            
            if score > 2:  # Only keep relevant results
                filtered_results.append(result)
        
        # Sort by relevance and return top 5
        return sorted(filtered_results, key=lambda x: x["relevance_score"], reverse=True)[:5]
    
    def _build_generation_prompt(self, analysis: Dict, research: List[Dict]) -> str:
        """Build comprehensive prompt for workflow generation"""
        
        research_context = ""
        if research:
            research_context = "\n".join([
                f"- {r.get('title', '')}: {r.get('snippet', '')[:200]}"
                for r in research[:3]
            ])
        
        prompt = f"""
Generate a complete n8n workflow JSON based on this analysis and research:

USER REQUEST ANALYSIS:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

RESEARCH FINDINGS:
{research_context}

Create a complete n8n Cloud compatible workflow JSON that:
1. Implements the exact user requirements
2. Uses modern n8n node versions
3. Includes proper error handling
4. Has descriptive node names
5. Uses the patterns found in research when applicable

The workflow must be a valid JSON with these required fields:
- meta, nodes, connections, active, settings, versionId, id, name, tags, pinData, staticData, createdAt, updatedAt, triggerCount

Generate ONLY valid JSON, no explanations.
"""
        
        return prompt
    
    def _parse_workflow_json(self, response: str) -> Dict[str, Any]:
        """Parse AI response to extract workflow JSON"""
        
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                workflow = json.loads(json_match.group())
                return self._validate_and_enhance_workflow(workflow)
            except Exception as e:
                print(f"[WARNING] JSON parsing failed: {e}")
        
        # Fallback
        return self._create_basic_workflow()
    
    def _validate_and_enhance_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance generated workflow"""
        
        # Ensure required fields
        workflow.setdefault("meta", {
            "templateCreatedBy": "Enhanced AI Bot with Internet Research",
            "instanceId": str(uuid.uuid4())
        })
        
        workflow.setdefault("active", True)
        workflow.setdefault("connections", {})
        workflow.setdefault("createdAt", datetime.now().isoformat())
        workflow["updatedAt"] = datetime.now().isoformat()
        workflow.setdefault("id", str(uuid.uuid4()))
        workflow.setdefault("nodes", [])
        workflow.setdefault("pinData", {})
        workflow.setdefault("settings", {"executionOrder": "v1"})
        workflow.setdefault("staticData", {})
        workflow.setdefault("tags", [])
        workflow.setdefault("triggerCount", 1)
        workflow.setdefault("versionId", str(uuid.uuid4()))
        
        # Validate nodes
        for node in workflow.get("nodes", []):
            if not node.get("id"):
                node["id"] = str(uuid.uuid4())
            node.setdefault("parameters", {})
            node.setdefault("position", [240, 300])
            node.setdefault("typeVersion", 1)
        
        return workflow
    
    def _create_basic_workflow(self) -> Dict[str, Any]:
        """Create basic workflow as fallback"""
        
        webhook_id = str(uuid.uuid4())
        process_id = str(uuid.uuid4())
        
        return {
            "meta": {
                "templateCreatedBy": "Enhanced AI Bot (Fallback)",
                "instanceId": str(uuid.uuid4())
            },
            "active": True,
            "connections": {
                webhook_id: {
                    "main": [[{
                        "node": process_id,
                        "type": "main",
                        "index": 0
                    }]]
                }
            },
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "id": str(uuid.uuid4()),
            "name": "Custom Automation Workflow",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "automation",
                        "responseMode": "onReceived"
                    },
                    "id": webhook_id,
                    "name": "Automation Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "webhookId": webhook_id
                },
                {
                    "parameters": {
                        "values": {
                            "string": [{
                                "name": "processed_at",
                                "value": "={{ new Date().toISOString() }}"
                            }]
                        }
                    },
                    "id": process_id,
                    "name": "Process Data",
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 3,
                    "position": [460, 300]
                }
            ],
            "pinData": {},
            "settings": {"executionOrder": "v1"},
            "staticData": {},
            "tags": [{
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "custom"
            }],
            "triggerCount": 1,
            "versionId": str(uuid.uuid4())
        }
    
    def _fallback_analysis(self, user_description: str) -> Dict[str, Any]:
        """Fallback analysis without AI"""
        
        text = user_description.lower()
        
        # Extract services
        services = []
        service_mapping = {
            "sheets": "google-sheets",
            "gmail": "gmail",
            "slack": "slack",
            "discord": "discord",
            "webhook": "webhook",
            "api": "http-request"
        }
        
        for keyword, service in service_mapping.items():
            if keyword in text:
                services.append(service)
        
        # Determine trigger
        trigger = "webhook"
        if any(word in text for word in ["schedule", "daily", "hourly", "time"]):
            trigger = "schedule"
        elif any(word in text for word in ["email", "mail"]):
            trigger = "email"
        
        # Generate search keywords
        keywords = []
        words = re.findall(r'\b\w+\b', text)
        keywords = [w for w in words if len(w) > 3 and w not in ["when", "then", "with", "from", "this", "that"]][:5]
        
        return {
            "intent": user_description[:100],
            "trigger_type": trigger,
            "services_needed": services or ["webhook"],
            "data_flow": "Basic data processing",
            "business_rules": [],
            "custom_requirements": {},
            "complexity": "medium",
            "search_keywords": keywords,
            "similar_use_cases": []
        }
    
    def _generate_from_template(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow from templates"""
        return self._create_basic_workflow()
    
    async def _call_openrouter_api(self, prompt: str) -> str:
        """Call OpenRouter API"""
        if not OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY not configured")
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                raise RuntimeError(f"API returned {response.status_code}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return {}

# Main functions for integration
async def enhanced_workflow_planning(user_description: str) -> Tuple[str, Dict[str, Any], List[Dict]]:
    """Enhanced workflow planning with internet research"""
    
    generator = EnhancedWorkflowGenerator()
    
    # 1. Analyze user request
    analysis = await generator.analyze_user_request(user_description)
    
    # 2. Research similar examples
    research_results = await generator.research_automation_examples(analysis)
    
    # 3. Create comprehensive plan
    plan_parts = [
        "🔍 **تحليل متقدم مع بحث إنترنت:**",
        "",
        f"**الهدف:** {analysis.get('intent', 'غير محدد')}",
        f"**المشغل:** {analysis.get('trigger_type', 'webhook')}",
        f"**الخدمات:** {', '.join(analysis.get('services_needed', []))}",
        f"**التعقيد:** {analysis.get('complexity', 'متوسط')}",
        ""
    ]
    
    if analysis.get('business_rules'):
        plan_parts.extend([
            "**قواعد العمل:**",
            "\n".join([f"• {rule}" for rule in analysis['business_rules']]),
            ""
        ])
    
    if research_results:
        plan_parts.extend([
            f"**أمثلة مشابهة وُجدت ({len(research_results)}):**"
        ])
        
        for i, result in enumerate(research_results[:3], 1):
            plan_parts.append(f"{i}. {result.get('title', 'مثال')[:80]}...")
        
        plan_parts.append("")
    
    plan_parts.extend([
        "**البيانات المطلوبة:**",
        json.dumps(analysis.get('custom_requirements', {}), ensure_ascii=False, indent=2),
        "",
        "**الوصف الأصلي:**",
        user_description
    ])
    
    return "\n".join(plan_parts), analysis, research_results

async def enhanced_workflow_generation(analysis: Dict[str, Any], research_results: List[Dict]) -> Dict[str, Any]:
    """Generate workflow using analysis and research"""
    
    generator = EnhancedWorkflowGenerator()
    workflow = await generator.generate_custom_workflow(analysis, research_results)
    
    return workflow

# Export functions
__all__ = [
    'enhanced_workflow_planning',
    'enhanced_workflow_generation',
    'EnhancedWorkflowGenerator'
]
