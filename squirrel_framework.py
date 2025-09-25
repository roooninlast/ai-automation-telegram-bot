# squirrel_framework.py - Multi-Step Reasoning System for High Accuracy
import os, json, httpx, re, asyncio
from typing import Dict, Any, List, Optional, Tuple
import uuid
from datetime import datetime
from urllib.parse import quote
import base64

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

class SquirrelFramework:
    """Multi-step reasoning system for high-accuracy workflow generation"""
    
    def __init__(self):
        # Curated GitHub repositories for examples
        self.github_repos = [
            "https://api.github.com/repos/enescingoz/awesome-n8n-templates/contents",
            "https://api.github.com/repos/Zie619/n8n-workflows/contents", 
            "https://api.github.com/repos/wassupjay/n8n-free-templates/contents"
        ]
        
        self.workflow_cache = {}  # Cache for retrieved examples
        
    async def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """Main pipeline: 6-step reasoning process"""
        
        print(f"[SQUIRREL] Starting 6-step reasoning pipeline for: {user_input[:50]}...")
        
        # Step 1: Clarify User Intent
        structured_spec = await self._step1_clarify_intent(user_input)
        print(f"[STEP 1] Intent clarified: {structured_spec.get('trigger', 'N/A')}")
        
        # Step 2: Retrieve Relevant Examples
        relevant_examples = await self._step2_retrieve_examples(structured_spec)
        print(f"[STEP 2] Found {len(relevant_examples)} relevant examples")
        
        # Step 3: Plan the Workflow
        workflow_plan = await self._step3_plan_workflow(structured_spec, relevant_examples)
        print(f"[STEP 3] Workflow planned with {len(workflow_plan.get('nodes', []))} nodes")
        
        # Step 4: Generate Workflow JSON
        workflow_json = await self._step4_generate_json(structured_spec, workflow_plan, relevant_examples)
        print(f"[STEP 4] JSON generated ({len(str(workflow_json))} chars)")
        
        # Step 5: Self-Check
        validated_workflow = await self._step5_self_check(structured_spec, workflow_json)
        print(f"[STEP 5] Self-check completed")
        
        # Step 6: User Confirmation Prep (return plan for user)
        confirmation_data = self._step6_prepare_confirmation(structured_spec, workflow_plan)
        print(f"[STEP 6] Confirmation data prepared")
        
        return {
            "structured_spec": structured_spec,
            "relevant_examples": relevant_examples,
            "workflow_plan": workflow_plan,
            "workflow_json": validated_workflow,
            "confirmation_data": confirmation_data,
            "confidence_score": self._calculate_confidence(structured_spec, relevant_examples, workflow_plan)
        }
    
    async def _step1_clarify_intent(self, user_input: str) -> Dict[str, Any]:
        """Step 1: Clarify and restructure user intent"""
        
        clarification_prompt = f"""
You are a workflow specification expert. The user gave you this request:
"{user_input}"

Rewrite this as a clear, structured specification. Extract EXACTLY what they want:

Return JSON with:
{{
    "trigger": "Specific trigger type and details",
    "inputs": ["List of all input data/sources"],
    "processing_steps": ["Step 1", "Step 2", "Step 3"],
    "outputs": ["All outputs and destinations"],
    "business_rules": ["Any conditions or logic"],
    "services_needed": ["service1", "service2"],
    "custom_requirements": {{"names": [], "formats": [], "special_logic": []}},
    "ambiguities": ["What needs clarification?"],
    "confidence": "high/medium/low"
}}

Be precise and identify gaps in the original request.
"""
        
        if OPENROUTER_API_KEY:
            try:
                response = await self._call_ai(clarification_prompt)
                return self._parse_json_response(response, fallback_key="structured_spec")
            except Exception as e:
                print(f"[WARNING] Step 1 AI failed: {e}")
        
        # Fallback analysis
        return self._fallback_intent_analysis(user_input)
    
    async def _step2_retrieve_examples(self, structured_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Step 2: Retrieve relevant examples from GitHub repos"""
        
        services = structured_spec.get("services_needed", [])
        trigger = structured_spec.get("trigger", "")
        
        # Generate search keywords
        search_keywords = self._extract_search_keywords(structured_spec)
        print(f"[STEP 2] Searching with keywords: {search_keywords}")
        
        all_examples = []
        
        # Search each repository
        for repo_url in self.github_repos:
            try:
                repo_examples = await self._search_github_repo(repo_url, search_keywords)
                all_examples.extend(repo_examples)
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"[WARNING] Failed to search repo {repo_url}: {e}")
        
        # Rank and filter examples
        relevant_examples = self._rank_examples(all_examples, structured_spec)
        
        return relevant_examples[:5]  # Top 5 most relevant
    
    async def _step3_plan_workflow(self, structured_spec: Dict[str, Any], examples: List[Dict]) -> Dict[str, Any]:
        """Step 3: Create detailed workflow plan"""
        
        examples_context = "\n".join([
            f"Example {i+1}: {ex.get('name', 'Unknown')}\n{ex.get('description', 'No description')[:200]}"
            for i, ex in enumerate(examples[:3])
        ])
        
        planning_prompt = f"""
Based on this specification and examples, create a detailed workflow plan:

SPECIFICATION:
{json.dumps(structured_spec, ensure_ascii=False, indent=2)}

RELEVANT EXAMPLES:
{examples_context}

Create a high-level plan as JSON:
{{
    "workflow_name": "Descriptive name",
    "nodes": [
        {{
            "node_name": "Node 1 Name",
            "node_type": "n8n-nodes-base.webhook",
            "purpose": "What this node does",
            "parameters": {{"key": "value"}},
            "position": [240, 300]
        }}
    ],
    "data_flow": "Describe how data flows between nodes",
    "error_handling": "How errors are handled",
    "validation_checks": ["Check 1", "Check 2"],
    "missing_elements": ["What might be missing?"]
}}

Focus on n8n node types and realistic parameters.
"""
        
        if OPENROUTER_API_KEY:
            try:
                response = await self._call_ai(planning_prompt)
                return self._parse_json_response(response, fallback_key="workflow_plan")
            except Exception as e:
                print(f"[WARNING] Step 3 AI failed: {e}")
        
        # Fallback planning
        return self._fallback_workflow_plan(structured_spec)
    
    async def _step4_generate_json(self, spec: Dict, plan: Dict, examples: List[Dict]) -> Dict[str, Any]:
        """Step 4: Generate actual n8n workflow JSON"""
        
        # Find the most relevant example
        best_example = examples[0] if examples else None
        example_json = ""
        
        if best_example and 'content' in best_example:
            example_json = f"\nREFERENCE EXAMPLE:\n{best_example['content'][:1000]}..."
        
        generation_prompt = f"""
Generate a complete n8n workflow JSON based on this plan:

SPECIFICATION:
{json.dumps(spec, ensure_ascii=False, indent=2)}

WORKFLOW PLAN:
{json.dumps(plan, ensure_ascii=False, indent=2)}

{example_json}

Create a complete n8n Cloud-compatible JSON workflow with:
- meta object with templateCreatedBy and instanceId
- nodes array with proper IDs and parameters
- connections object linking nodes
- All required fields: active, settings, versionId, id, name, tags, etc.

Generate ONLY valid JSON. Use modern node versions and proper n8n format.
"""
        
        if OPENROUTER_API_KEY:
            try:
                response = await self._call_ai(generation_prompt)
                return self._parse_json_response(response, fallback_key="workflow")
            except Exception as e:
                print(f"[WARNING] Step 4 AI failed: {e}")
        
        # Fallback generation
        return self._fallback_workflow_generation(spec, plan)
    
    async def _step5_self_check(self, spec: Dict, workflow: Dict) -> Dict[str, Any]:
        """Step 5: Self-validation and error correction"""
        
        validation_prompt = f"""
Review this n8n workflow against the original specification:

ORIGINAL SPECIFICATION:
{json.dumps(spec, ensure_ascii=False, indent=2)}

GENERATED WORKFLOW:
{json.dumps(workflow, ensure_ascii=False, indent=2)[:2000]}...

Check:
1. Does it satisfy all requirements from the specification?
2. Are all nodes properly connected?
3. Are node types and parameters correct for n8n?
4. Is the JSON structure valid for n8n Cloud?
5. Are there any missing or incorrect elements?

If issues found, return corrected workflow. Otherwise, return the original.

Return JSON:
{{
    "validation_passed": true/false,
    "issues_found": ["Issue 1", "Issue 2"],
    "corrected_workflow": {{...}} or null,
    "confidence_score": 0-100
}}
"""
        
        if OPENROUTER_API_KEY:
            try:
                response = await self._call_ai(validation_prompt)
                validation_result = self._parse_json_response(response, fallback_key="validation")
                
                if validation_result.get("corrected_workflow"):
                    return validation_result["corrected_workflow"]
                elif validation_result.get("validation_passed", True):
                    return workflow
                else:
                    # Apply basic fixes
                    return self._apply_basic_fixes(workflow)
                    
            except Exception as e:
                print(f"[WARNING] Step 5 AI failed: {e}")
        
        # Fallback validation
        return self._basic_workflow_validation(workflow)
    
    def _step6_prepare_confirmation(self, spec: Dict, plan: Dict) -> Dict[str, Any]:
        """Step 6: Prepare user confirmation data"""
        
        return {
            "summary": f"Workflow: {plan.get('workflow_name', 'Custom Automation')}",
            "trigger_description": spec.get("trigger", "Unknown trigger"),
            "main_actions": spec.get("processing_steps", []),
            "outputs": spec.get("outputs", []),
            "services_used": spec.get("services_needed", []),
            "node_count": len(plan.get("nodes", [])),
            "complexity": "high" if len(plan.get("nodes", [])) > 5 else "medium"
        }
    
    async def _search_github_repo(self, repo_url: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search GitHub repository for relevant workflows"""
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                headers = {"Accept": "application/vnd.github.v3+json"}
                
                # Add GitHub token if available
                github_token = os.getenv("GITHUB_TOKEN")
                if github_token:
                    headers["Authorization"] = f"token {github_token}"
                
                response = await client.get(repo_url, headers=headers)
                
                if response.status_code == 200:
                    files = response.json()
                    relevant_files = []
                    
                    for file in files:
                        if file.get("name", "").endswith(".json"):
                            # Check if filename matches keywords
                            filename = file.get("name", "").lower()
                            if any(keyword.lower() in filename for keyword in keywords):
                                
                                # Get file content
                                try:
                                    file_content = await self._get_file_content(file.get("download_url", ""))
                                    relevant_files.append({
                                        "name": file.get("name"),
                                        "path": file.get("path"),
                                        "url": file.get("html_url"),
                                        "content": file_content,
                                        "repo": repo_url,
                                        "relevance_score": 0
                                    })
                                except Exception as e:
                                    print(f"[WARNING] Failed to get file content: {e}")
                    
                    return relevant_files[:10]  # Limit to 10 files per repo
                    
        except Exception as e:
            print(f"[ERROR] GitHub search failed: {e}")
        
        return []
    
    async def _get_file_content(self, download_url: str) -> str:
        """Get file content from GitHub"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(download_url)
                if response.status_code == 200:
                    return response.text[:5000]  # Limit content size
        except Exception as e:
            print(f"[WARNING] Failed to download file: {e}")
        return ""
    
    def _extract_search_keywords(self, spec: Dict) -> List[str]:
        """Extract relevant keywords for searching"""
        keywords = []
        
        # From trigger
        trigger = spec.get("trigger", "")
        if "webhook" in trigger.lower():
            keywords.append("webhook")
        if "schedule" in trigger.lower() or "cron" in trigger.lower():
            keywords.append("schedule")
        if "email" in trigger.lower():
            keywords.append("email")
        
        # From services
        services = spec.get("services_needed", [])
        keywords.extend(services)
        
        # From processing steps
        steps = " ".join(spec.get("processing_steps", [])).lower()
        if "sheet" in steps or "google" in steps:
            keywords.append("sheets")
        if "slack" in steps:
            keywords.append("slack")
        if "email" in steps or "gmail" in steps:
            keywords.append("email")
        
        return list(set(keywords))  # Remove duplicates
    
    def _rank_examples(self, examples: List[Dict], spec: Dict) -> List[Dict]:
        """Rank examples by relevance to specification"""
        
        spec_text = json.dumps(spec, ensure_ascii=False).lower()
        keywords = spec.get("services_needed", []) + self._extract_search_keywords(spec)
        
        for example in examples:
            score = 0
            example_text = (example.get("name", "") + " " + example.get("content", "")).lower()
            
            # Keyword matching
            for keyword in keywords:
                if keyword.lower() in example_text:
                    score += 3
            
            # Service matching
            for service in spec.get("services_needed", []):
                if service.lower() in example_text:
                    score += 5
            
            # Trigger matching
            trigger = spec.get("trigger", "").lower()
            if any(word in example_text for word in trigger.split()):
                score += 2
            
            example["relevance_score"] = score
        
        # Sort by relevance score
        return sorted(examples, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    def _calculate_confidence(self, spec: Dict, examples: List, plan: Dict) -> int:
        """Calculate confidence score for the generated workflow"""
        
        confidence = 50  # Base confidence
        
        # Boost confidence based on factors
        if spec.get("confidence") == "high":
            confidence += 20
        elif spec.get("confidence") == "medium":
            confidence += 10
        
        if examples:
            confidence += min(len(examples) * 5, 25)  # Up to 25 points for examples
        
        if plan.get("nodes") and len(plan["nodes"]) > 0:
            confidence += 15
        
        if not spec.get("ambiguities"):
            confidence += 10
        
        return min(confidence, 100)
    
    # Fallback methods
    def _fallback_intent_analysis(self, user_input: str) -> Dict[str, Any]:
        """Fallback intent analysis without AI"""
        text = user_input.lower()
        
        # Detect trigger
        trigger = "webhook"
        if any(word in text for word in ["schedule", "every", "daily", "weekly"]):
            trigger = "schedule"
        elif any(word in text for word in ["email", "mail"]):
            trigger = "email"
        
        # Detect services
        services = []
        if "sheet" in text or "google" in text:
            services.append("google-sheets")
        if "slack" in text:
            services.append("slack")
        if "email" in text or "gmail" in text:
            services.append("gmail")
        
        return {
            "trigger": f"{trigger} trigger",
            "inputs": ["form data", "user input"],
            "processing_steps": ["receive data", "process data", "send output"],
            "outputs": ["notification", "data storage"],
            "business_rules": [],
            "services_needed": services or ["webhook"],
            "custom_requirements": {},
            "ambiguities": [],
            "confidence": "medium"
        }
    
    def _fallback_workflow_plan(self, spec: Dict) -> Dict[str, Any]:
        """Fallback workflow planning"""
        return {
            "workflow_name": "Custom Automation",
            "nodes": [
                {
                    "node_name": "Trigger",
                    "node_type": "n8n-nodes-base.webhook",
                    "purpose": "Receive data",
                    "parameters": {"httpMethod": "POST"},
                    "position": [240, 300]
                },
                {
                    "node_name": "Process Data",
                    "node_type": "n8n-nodes-base.set",
                    "purpose": "Process incoming data",
                    "parameters": {},
                    "position": [460, 300]
                }
            ],
            "data_flow": "Data flows from trigger to processing",
            "error_handling": "Basic error handling",
            "validation_checks": ["Check data format"],
            "missing_elements": []
        }
    
    def _fallback_workflow_generation(self, spec: Dict, plan: Dict) -> Dict[str, Any]:
        """Fallback workflow generation"""
        
        webhook_id = str(uuid.uuid4())
        process_id = str(uuid.uuid4())
        
        return {
            "meta": {
                "templateCreatedBy": "Squirrel Framework Fallback",
                "instanceId": str(uuid.uuid4())
            },
            "active": True,
            "connections": {
                webhook_id: {
                    "main": [[{"node": process_id, "type": "main", "index": 0}]]
                }
            },
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "id": str(uuid.uuid4()),
            "name": plan.get("workflow_name", "Custom Automation"),
            "nodes": [
                {
                    "parameters": {"httpMethod": "POST", "path": "automation"},
                    "id": webhook_id,
                    "name": "Automation Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "webhookId": webhook_id
                },
                {
                    "parameters": {"values": {"string": [{"name": "processed", "value": "true"}]}},
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
            "tags": [],
            "triggerCount": 1,
            "versionId": str(uuid.uuid4())
        }
    
    def _basic_workflow_validation(self, workflow: Dict) -> Dict[str, Any]:
        """Basic workflow validation and fixes"""
        
        # Ensure required fields
        workflow.setdefault("meta", {"templateCreatedBy": "Squirrel Framework"})
        workflow.setdefault("active", True)
        workflow.setdefault("connections", {})
        workflow.setdefault("id", str(uuid.uuid4()))
        workflow.setdefault("nodes", [])
        workflow.setdefault("settings", {"executionOrder": "v1"})
        workflow.setdefault("versionId", str(uuid.uuid4()))
        
        # Fix nodes
        for node in workflow.get("nodes", []):
            if not node.get("id"):
                node["id"] = str(uuid.uuid4())
            node.setdefault("parameters", {})
            node.setdefault("position", [240, 300])
        
        return workflow
    
    def _apply_basic_fixes(self, workflow: Dict) -> Dict[str, Any]:
        """Apply basic fixes to workflow"""
        return self._basic_workflow_validation(workflow)
    
    async def _call_ai(self, prompt: str) -> str:
        """Call AI API"""
        if not OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY not configured")
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
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
    
    def _parse_json_response(self, response: str, fallback_key: str = "result") -> Dict[str, Any]:
        """Parse JSON from AI response"""
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback
        return {fallback_key: response}

# Export the framework
__all__ = ['SquirrelFramework']
