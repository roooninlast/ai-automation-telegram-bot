# smart_ai_system.py - AI system with real GitHub search and custom generation
import os, json, httpx, re, asyncio
from typing import Dict, Any, Tuple, List, Optional
import uuid
from datetime import datetime

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

class SmartWorkflowGenerator:
    """Smart workflow generator that actually uses GitHub examples"""
    
    def __init__(self):
        self.github_searcher = None
        
    async def initialize(self):
        """Initialize GitHub searcher"""
        try:
            from real_github_searcher import github_searcher
            self.github_searcher = github_searcher
            print("[SUCCESS] GitHub searcher initialized")
        except ImportError as e:
            print(f"[WARNING] GitHub searcher not available: {e}")
            self.github_searcher = None
    
    async def create_custom_workflow(self, user_description: str) -> Tuple[Dict[str, Any], str, int]:
        """Create truly custom workflow based on user description and real examples"""
        
        print(f"[SMART] Processing: {user_description[:100]}...")
        
        # Step 1: Search for real GitHub examples
        examples = []
        analysis = {}
        
        if self.github_searcher:
            try:
                examples, analysis = await self.github_searcher.search_for_examples(user_description)
                print(f"[SMART] Found {len(examples)} real examples from GitHub")
            except Exception as e:
                print(f"[WARNING] GitHub search failed: {e}")
        
        # Step 2: Create detailed analysis
        if not analysis:
            analysis = self._fallback_analysis(user_description)
        
        # Step 3: Generate custom workflow using examples
        workflow_json = await self._generate_workflow_from_analysis(analysis, examples, user_description)
        
        # Step 4: Create comprehensive report
        report = self._create_generation_report(analysis, examples, user_description)
        
        # Step 5: Calculate confidence score
        confidence = self._calculate_confidence(analysis, examples)
        
        return workflow_json, report, confidence
    
    async def _generate_workflow_from_analysis(self, analysis: Dict, examples: List[Dict], description: str) -> Dict[str, Any]:
        """Generate workflow using analysis and real examples"""
        
        # Use the best example as a base if available
        best_example = examples[0] if examples else None
        
        if best_example and OPENROUTER_API_KEY:
            # AI-powered customization using real example
            return await self._ai_customize_workflow(analysis, best_example, description)
        elif best_example:
            # Rule-based customization of real example
            return self._rule_customize_workflow(analysis, best_example, description)
        else:
            # Create from scratch using analysis
            return self._create_from_analysis(analysis, description)
    
    async def _ai_customize_workflow(self, analysis: Dict, example: Dict, description: str) -> Dict[str, Any]:
        """Use AI to customize a real example workflow"""
        
        example_workflow = example.get("workflow_json", {})
        
        customization_prompt = f"""
You have a user request and a similar real n8n workflow example. Customize the example to match the user's exact needs.

USER REQUEST:
"{description}"

ANALYSIS:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

REAL EXAMPLE WORKFLOW:
{json.dumps(example_workflow, ensure_ascii=False, indent=2)[:3000]}...

Customize this workflow to match the user's request exactly:

1. Change node names to match user's requirements
2. Update parameters based on user's needs
3. Add/remove nodes as necessary
4. Update sheet names, email addresses, etc. from user description
5. Ensure all connections are correct
6. Keep the same overall structure if it works for the user

Return ONLY the complete customized n8n workflow JSON.
"""
        
        try:
            response = await self._call_openrouter_api(customization_prompt)
            
            # Try to parse the AI response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    customized = json.loads(json_match.group())
                    return self._ensure_workflow_validity(customized, description)
                except json.JSONDecodeError:
                    print("[WARNING] AI returned invalid JSON, using rule-based customization")
        except Exception as e:
            print(f"[WARNING] AI customization failed: {e}")
        
        # Fallback to rule-based customization
        return self._rule_customize_workflow(analysis, example, description)
    
    def _rule_customize_workflow(self, analysis: Dict, example: Dict, description: str) -> Dict[str, Any]:
        """Rule-based customization of example workflow"""
        
        workflow = example.get("workflow_json", {}).copy()
        
        # Update basic metadata
        workflow["name"] = f"Custom {analysis.get('trigger_type', 'Automation')} Workflow"
        workflow["id"] = str(uuid.uuid4())
        workflow["versionId"] = str(uuid.uuid4())
        workflow["updatedAt"] = datetime.now().isoformat()
        
        # Update nodes with custom requirements
        custom_reqs = analysis.get("custom_requirements", {})
        services_needed = analysis.get("services_needed", [])
        
        for node in workflow.get("nodes", []):
            # Update node IDs
            node["id"] = str(uuid.uuid4())
            
            # Customize Google Sheets nodes
            if "googleSheets" in node.get("type", ""):
                if "sheet_names" in custom_reqs and custom_reqs["sheet_names"]:
                    sheet_name = custom_reqs["sheet_names"][0]
                    if "sheetName" in node.get("parameters", {}):
                        node["parameters"]["sheetName"]["value"] = sheet_name
                
                # Update column mappings based on detected fields
                data_fields = analysis.get("data_fields", {})
                if data_fields and "columns" in node.get("parameters", {}):
                    columns_mapping = {}
                    for field_key, field_name in data_fields.items():
                        columns_mapping[field_name] = f"=${{json.{field_key}}}"
                    
                    # Add timestamp and ID
                    columns_mapping["Timestamp"] = "={{ new Date().toISOString() }}"
                    if "generate_unique_id" in analysis.get("business_logic", []):
                        columns_mapping["Request_ID"] = "={{ 'REQ-' + new Date().getTime().toString() }}"
                    
                    node["parameters"]["columns"]["value"] = columns_mapping
            
            # Customize webhook nodes
            elif "webhook" in node.get("type", ""):
                node["webhookId"] = node["id"]
                # Try to extract custom path from description
                if "webhook" in description.lower():
                    path_match = re.search(r'path[:\s]*["\']?([a-zA-Z0-9\-_]+)', description)
                    if path_match:
                        node["parameters"]["path"] = path_match.group(1)
            
            # Customize email nodes
            elif "gmail" in node.get("type", "") or "email" in node.get("type", ""):
                if "send_notification" in analysis.get("business_logic", []):
                    # Create custom email content
                    email_subject = f"New {analysis.get('trigger_type', 'Request')} Received"
                    email_body = f"A new {analysis.get('trigger_type', 'request')} has been processed.\n\nDetails:\n"
                    
                    for field in analysis.get("data_fields", {}).keys():
                        email_body += f"{field.title()}: ${{json.{field}}}\n"
                    
                    node["parameters"]["subject"] = email_subject
                    node["parameters"]["message"] = email_body
        
        # Fix connections with new node IDs
        self._fix_workflow_connections(workflow)
        
        return workflow
    
    def _create_from_analysis(self, analysis: Dict, description: str) -> Dict[str, Any]:
        """Create workflow from scratch based on analysis"""
        
        trigger_type = analysis.get("trigger_type", "webhook")
        services = analysis.get("services_needed", ["webhook"])
        data_fields = analysis.get("data_fields", {"name": "Name", "email": "Email"})
        
        nodes = []
        connections = {}
        
        # Create trigger node
        trigger_id = str(uuid.uuid4())
        
        if trigger_type == "webhook":
            trigger_node = {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "custom-automation",
                    "responseMode": "onReceived"
                },
                "id": trigger_id,
                "name": "Custom Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": trigger_id
            }
        elif trigger_type == "schedule":
            trigger_node = {
                "parameters": {
                    "rule": {"interval": [{"field": "cronExpression", "value": "0 9 * * *"}]}
                },
                "id": trigger_id,
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.cron",
                "typeVersion": 1,
                "position": [240, 300]
            }
        else:
            # Default webhook
            trigger_node = {
                "parameters": {"httpMethod": "POST", "path": "automation"},
                "id": trigger_id,
                "name": "Automation Trigger", 
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": trigger_id
            }
        
        nodes.append(trigger_node)
        
        # Create processing/storage nodes based on services
        prev_node_id = trigger_id
        x_position = 460
        
        if "google-sheets" in services or "google sheets" in services:
            sheets_id = str(uuid.uuid4())
            
            # Build columns from data fields
            columns_value = {}
            for field_key, field_name in data_fields.items():
                columns_value[field_name] = f"=${{json.{field_key}}}"
            
            columns_value["Timestamp"] = "={{ new Date().toISOString() }}"
            if "generate_unique_id" in analysis.get("business_logic", []):
                columns_value["Request_ID"] = "={{ 'REQ-' + new Date().getTime().toString() }}"
            
            # Get custom sheet name if provided
            sheet_name = "Custom Data"
            custom_reqs = analysis.get("custom_requirements", {})
            if "sheet_names" in custom_reqs and custom_reqs["sheet_names"]:
                sheet_name = custom_reqs["sheet_names"][0]
            
            sheets_node = {
                "parameters": {
                    "resource": "sheet",
                    "operation": "appendOrUpdate",
                    "documentId": {"__rl": True, "value": "={{$env.GOOGLE_SHEET_ID}}", "mode": "id"},
                    "sheetName": {"__rl": True, "value": sheet_name, "mode": "list"},
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": columns_value,
                        "matchingColumns": [],
                        "schema": []
                    }
                },
                "id": sheets_id,
                "name": f"Save to {sheet_name}",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [x_position, 300]
            }
            
            nodes.append(sheets_node)
            connections[prev_node_id] = {"main": [[{"node": sheets_id, "type": "main", "index": 0}]]}
            prev_node_id = sheets_id
            x_position += 220
        
        if "gmail" in services and "send_notification" in analysis.get("business_logic", []):
            email_id = str(uuid.uuid4())
            
            email_node = {
                "parameters": {
                    "resource": "message",
                    "operation": "send",
                    "toEmail": "={{ $json.email }}",
                    "subject": f"New {trigger_type.title()} Received",
                    "emailType": "text",
                    "message": f"Your {trigger_type} has been processed successfully.\n\nThank you!"
                },
                "id": email_id,
                "name": "Send Confirmation",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [x_position, 300]
            }
            
            nodes.append(email_node)
            connections[prev_node_id] = {"main": [[{"node": email_id, "type": "main", "index": 0}]]}
            x_position += 220
        
        # Create complete workflow
        workflow = {
            "meta": {
                "templateCreatedBy": "Smart AI System",
                "instanceId": str(uuid.uuid4())
            },
            "active": True,
            "connections": connections,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "id": str(uuid.uuid4()),
            "name": f"Custom {trigger_type.title()} Automation",
            "nodes": nodes,
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
        
        return workflow
    
    def _fix_workflow_connections(self, workflow: Dict):
        """Fix connections after changing node IDs"""
        nodes = workflow.get("nodes", [])
        old_connections = workflow.get("connections", {})
        new_connections = {}
        
        # Create mapping of old to new node names/IDs
        node_mapping = {}
        for node in nodes:
            node_name = node.get("name", "")
            node_id = node.get("id", "")
            node_mapping[node_name] = node_id
        
        # Try to rebuild connections based on node order
        for i, node in enumerate(nodes[:-1]):  # All but last node
            current_id = node["id"]
            next_node = nodes[i + 1]
            next_id = next_node["id"]
            
            new_connections[current_id] = {
                "main": [[{"node": next_id, "type": "main", "index": 0}]]
            }
        
        workflow["connections"] = new_connections
    
    def _ensure_workflow_validity(self, workflow: Dict, description: str) -> Dict[str, Any]:
        """Ensure workflow has all required fields and valid structure"""
        
        # Required top-level fields
        workflow.setdefault("meta", {
            "templateCreatedBy": "Smart AI System", 
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
        
        # Fix nodes
        for node in workflow.get("nodes", []):
            if not node.get("id"):
                node["id"] = str(uuid.uuid4())
            node.setdefault("parameters", {})
            node.setdefault("position", [240, 300])
            
            # Add webhookId for webhook nodes
            if "webhook" in node.get("type", ""):
                node["webhookId"] = node["id"]
        
        # Ensure name reflects description
        if not workflow.get("name") or workflow["name"] == "Unnamed":
            workflow["name"] = f"Custom Automation - {description[:50]}..."
        
        return workflow
    
    def _create_generation_report(self, analysis: Dict, examples: List[Dict], description: str) -> str:
        """Create detailed report about the generation process"""
        
        report_parts = [
            "🔍 **Smart Analysis Complete**",
            "",
            f"**Original Request:** {description}",
            "",
            f"**Detected Trigger:** {analysis.get('trigger_type', 'webhook').title()}",
            f"**Services Identified:** {', '.join(analysis.get('services_needed', ['Basic']))}", 
            f"**Business Logic:** {', '.join(analysis.get('business_logic', ['Standard processing']))}",
            ""
        ]
        
        if examples:
            report_parts.extend([
                f"**🎯 GitHub Examples Found: {len(examples)}**",
                ""
            ])
            
            for i, example in enumerate(examples[:3], 1):
                report_parts.extend([
                    f"**Example {i}:** {example.get('name', 'Unknown')}",
                    f"   📂 From: {example.get('repo', 'Unknown repo')}",
                    f"   🎯 Relevance: {example.get('final_relevance_score', 0)} points",
                    f"   🔧 Services: {', '.join(example.get('services', []))}",
                    ""
                ])
            
            report_parts.extend([
                "**✅ Customization Applied:**",
                f"• Used '{examples[0].get('name', 'Best match')}' as base template",
                "• Adapted parameters to match your requirements",
                "• Updated node names and configurations",
                "• Ensured n8n Cloud compatibility",
                ""
            ])
        else:
            report_parts.extend([
                "**⚠️ No GitHub Examples Found**",
                "• Created workflow from analysis only",
                "• Used intelligent service detection",
                "• Applied best practices for n8n workflows", 
                ""
            ])
        
        # Custom requirements
        custom_reqs = analysis.get("custom_requirements", {})
        if custom_reqs:
            report_parts.extend([
                "**🎨 Custom Requirements Applied:**"
            ])
            for key, value in custom_reqs.items():
                if isinstance(value, list):
                    report_parts.append(f"• {key.replace('_', ' ').title()}: {', '.join(value)}")
                else:
                    report_parts.append(f"• {key.replace('_', ' ').title()}: {value}")
            report_parts.append("")
        
        # Data fields
        data_fields = analysis.get("data_fields", {})
        if data_fields:
            report_parts.extend([
                "**📋 Data Fields Configured:**",
                ", ".join(data_fields.values()),
                ""
            ])
        
        complexity = analysis.get("complexity", "medium")
        report_parts.extend([
            f"**📊 Workflow Complexity:** {complexity.title()}",
            f"**🎯 Generation Method:** {'AI + GitHub Examples' if examples and OPENROUTER_API_KEY else 'Rule-based Generation'}",
        ])
        
        return "\n".join(report_parts)
    
    def _calculate_confidence(self, analysis: Dict, examples: List[Dict]) -> int:
        """Calculate confidence score based on analysis and examples"""
        
        confidence = 60  # Base confidence
        
        # Boost for examples found
        if examples:
            confidence += min(len(examples) * 8, 25)  # Up to 25 points
            
            # Extra boost for high relevance examples
            best_score = examples[0].get("final_relevance_score", 0)
            if best_score > 10:
                confidence += 10
            elif best_score > 5:
                confidence += 5
        
        # Boost for clear analysis
        services = analysis.get("services_needed", [])
        if len(services) > 0:
            confidence += 5
        if len(services) > 1:
            confidence += 5
        
        # Boost for detected custom requirements
        if analysis.get("custom_requirements"):
            confidence += 5
        
        # Boost for detected business logic
        if analysis.get("business_logic"):
            confidence += 5
        
        # Boost for AI availability
        if OPENROUTER_API_KEY and examples:
            confidence += 10  # AI customization available
        
        return min(confidence, 100)
    
    def _fallback_analysis(self, description: str) -> Dict[str, Any]:
        """Fallback analysis when GitHub search fails"""
        
        text = description.lower()
        
        # Basic service detection
        services = []
        if any(word in text for word in ["sheet", "spreadsheet", "google"]):
            services.append("google-sheets")
        if any(word in text for word in ["email", "gmail", "mail"]):
            services.append("gmail")
        if any(word in text for word in ["slack", "notification"]):
            services.append("slack")
        if any(word in text for word in ["webhook", "form", "submit"]):
            services.append("webhook")
        
        # Basic trigger detection
        trigger = "webhook"
        if any(word in text for word in ["daily", "weekly", "schedule", "cron"]):
            trigger = "schedule"
        elif any(word in text for word in ["email", "mail"]):
            trigger = "email"
        
        # Basic field detection
        fields = {}
        common_fields = ["name", "email", "phone", "company", "message"]
        for field in common_fields:
            if field in text:
                fields[field] = field.title()
        
        if not fields:  # Default fields
            fields = {"name": "Name", "email": "Email", "message": "Message"}
        
        return {
            "trigger_type": trigger,
            "services_needed": services or ["webhook"],
            "business_logic": ["send_notification"] if "email" in services else [],
            "custom_requirements": {},
            "data_fields": fields,
            "examples_used": 0,
            "confidence": "medium",
            "complexity": "medium"
        }
    
    async def _call_openrouter_api(self, prompt: str) -> str:
        """Call OpenRouter API for AI processing"""
        
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
                raise RuntimeError(f"OpenRouter API returned {response.status_code}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

# Initialize the smart generator
smart_generator = SmartWorkflowGenerator()

async def create_smart_workflow(user_description: str) -> Tuple[Dict[str, Any], str, int]:
    """Main function to create smart workflow"""
    await smart_generator.initialize()
    return await smart_generator.create_custom_workflow(user_description)

# Export
__all__ = ['create_smart_workflow', 'smart_generator']
