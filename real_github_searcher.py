# real_github_searcher.py - Actually search GitHub repos for n8n examples
import os, json, httpx, re, asyncio
from typing import Dict, Any, List, Optional, Tuple
import uuid
from datetime import datetime
import base64

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Optional but recommended

class GitHubWorkflowSearcher:
    """Real GitHub repository searcher for n8n workflows"""
    
    def __init__(self):
        self.repos = [
            {
                "owner": "enescingoz",
                "name": "awesome-n8n-templates",
                "api_url": "https://api.github.com/repos/enescingoz/awesome-n8n-templates"
            },
            {
                "owner": "Zie619", 
                "name": "n8n-workflows",
                "api_url": "https://api.github.com/repos/Zie619/n8n-workflows"
            },
            {
                "owner": "wassupjay",
                "name": "n8n-free-templates", 
                "api_url": "https://api.github.com/repos/wassupjay/n8n-free-templates"
            }
        ]
        
        self.workflow_cache = {}
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "n8n-automation-bot"
        }
        
        if GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {GITHUB_TOKEN}"
            print("[INFO] Using GitHub token for API access")
    
    async def search_for_examples(self, user_description: str) -> Tuple[List[Dict], Dict]:
        """Search GitHub repos for relevant n8n workflow examples"""
        
        print(f"[GITHUB] Starting real search for: {user_description[:50]}...")
        
        # Extract search terms from user description
        search_terms = self._extract_search_terms(user_description)
        print(f"[GITHUB] Search terms: {search_terms}")
        
        all_workflows = []
        
        # Search each repository
        for repo in self.repos:
            try:
                workflows = await self._search_single_repo(repo, search_terms)
                all_workflows.extend(workflows)
                print(f"[GITHUB] Found {len(workflows)} workflows in {repo['name']}")
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"[ERROR] Failed to search {repo['name']}: {e}")
        
        if not all_workflows:
            print("[WARNING] No workflows found, trying broader search...")
            # Try broader search with common terms
            broad_terms = ["webhook", "form", "notification", "automation"]
            for repo in self.repos:
                try:
                    workflows = await self._search_single_repo(repo, broad_terms)
                    all_workflows.extend(workflows[:2])  # Limit to 2 per repo
                except Exception as e:
                    print(f"[ERROR] Broad search failed for {repo['name']}: {e}")
        
        # Rank workflows by relevance
        ranked_workflows = self._rank_by_relevance(all_workflows, user_description, search_terms)
        
        # Generate analysis based on found examples
        analysis = self._analyze_user_request_with_examples(user_description, ranked_workflows)
        
        return ranked_workflows[:5], analysis  # Return top 5
    
    def _extract_search_terms(self, description: str) -> List[str]:
        """Extract relevant search terms from user description"""
        
        text = description.lower()
        terms = []
        
        # Service detection
        service_keywords = {
            "google sheets": ["sheet", "spreadsheet", "google", "gsheet"],
            "gmail": ["email", "gmail", "mail", "send email"],
            "slack": ["slack", "message", "channel", "notification"],
            "webhook": ["form", "submit", "receive", "trigger", "webhook"],
            "schedule": ["daily", "weekly", "monthly", "schedule", "cron", "time"],
            "discord": ["discord", "bot", "message"],
            "twitter": ["twitter", "tweet", "social"],
            "api": ["api", "request", "http", "endpoint"],
            "database": ["database", "db", "mysql", "postgres"],
            "shopify": ["shopify", "order", "product", "ecommerce"],
            "wordpress": ["wordpress", "blog", "post", "cms"]
        }
        
        for service, keywords in service_keywords.items():
            if any(keyword in text for keyword in keywords):
                terms.append(service.replace(" ", "-"))
        
        # Action detection
        if any(word in text for word in ["save", "store", "record"]):
            terms.append("save")
        if any(word in text for word in ["send", "notify", "alert"]):
            terms.append("notification")
        if any(word in text for word in ["process", "transform", "format"]):
            terms.append("processing")
        if any(word in text for word in ["filter", "condition", "if"]):
            terms.append("conditional")
        
        # Remove duplicates and ensure we have at least basic terms
        terms = list(set(terms))
        if not terms:
            terms = ["webhook", "automation"]
            
        return terms[:5]  # Limit to 5 terms
    
    async def _search_single_repo(self, repo: Dict, search_terms: List[str]) -> List[Dict]:
        """Search a single repository for workflows"""
        
        repo_key = f"{repo['owner']}/{repo['name']}"
        
        # Check cache first
        if repo_key in self.workflow_cache:
            print(f"[GITHUB] Using cached data for {repo_key}")
            return self._filter_cached_workflows(self.workflow_cache[repo_key], search_terms)
        
        workflows = []
        
        try:
            # Get repository contents
            async with httpx.AsyncClient(timeout=30) as client:
                
                # First try to get the contents of common directories
                directories_to_search = ["", "workflows", "templates", "examples", "n8n"]
                
                for directory in directories_to_search:
                    try:
                        url = f"{repo['api_url']}/contents/{directory}" if directory else f"{repo['api_url']}/contents"
                        response = await client.get(url, headers=self.headers)
                        
                        if response.status_code == 200:
                            contents = response.json()
                            if isinstance(contents, list):
                                for item in contents:
                                    if item.get("name", "").endswith(".json"):
                                        workflow = await self._fetch_workflow_content(client, item, repo)
                                        if workflow:
                                            workflows.append(workflow)
                            break  # Found valid directory
                            
                    except Exception as e:
                        print(f"[DEBUG] Directory {directory} not found in {repo_key}: {e}")
                        continue
                        
        except Exception as e:
            print(f"[ERROR] Failed to search repository {repo_key}: {e}")
        
        # Cache the results
        self.workflow_cache[repo_key] = workflows
        print(f"[GITHUB] Cached {len(workflows)} workflows from {repo_key}")
        
        return self._filter_cached_workflows(workflows, search_terms)
    
    async def _fetch_workflow_content(self, client: httpx.AsyncClient, item: Dict, repo: Dict) -> Optional[Dict]:
        """Fetch actual workflow content from GitHub"""
        
        try:
            # Get file content
            if item.get("download_url"):
                content_response = await client.get(item["download_url"])
                if content_response.status_code == 200:
                    content_text = content_response.text
                    
                    # Try to parse as JSON
                    try:
                        workflow_json = json.loads(content_text)
                        
                        # Validate it's a real n8n workflow
                        if self._is_valid_n8n_workflow(workflow_json):
                            return {
                                "name": item.get("name", "Unknown"),
                                "path": item.get("path", ""),
                                "repo": f"{repo['owner']}/{repo['name']}",
                                "url": item.get("html_url", ""),
                                "content": content_text,
                                "workflow_json": workflow_json,
                                "size": len(content_text),
                                "services": self._extract_services_from_workflow(workflow_json),
                                "trigger_type": self._extract_trigger_type(workflow_json)
                            }
                    except json.JSONDecodeError:
                        print(f"[DEBUG] Invalid JSON in {item.get('name')}")
                        
        except Exception as e:
            print(f"[DEBUG] Failed to fetch {item.get('name')}: {e}")
        
        return None
    
    def _is_valid_n8n_workflow(self, workflow_json: Dict) -> bool:
        """Check if JSON is a valid n8n workflow"""
        required_fields = ["nodes", "connections"]
        return (isinstance(workflow_json, dict) and 
                all(field in workflow_json for field in required_fields) and
                isinstance(workflow_json.get("nodes"), list) and
                len(workflow_json.get("nodes", [])) > 0)
    
    def _extract_services_from_workflow(self, workflow: Dict) -> List[str]:
        """Extract services/integrations used in workflow"""
        services = set()
        
        for node in workflow.get("nodes", []):
            node_type = node.get("type", "")
            if "." in node_type:
                service = node_type.split(".")[-1]
                services.add(service)
        
        return list(services)
    
    def _extract_trigger_type(self, workflow: Dict) -> str:
        """Extract the trigger type from workflow"""
        for node in workflow.get("nodes", []):
            node_type = node.get("type", "").lower()
            if "webhook" in node_type:
                return "webhook"
            elif "cron" in node_type or "schedule" in node_type:
                return "schedule" 
            elif "email" in node_type or "imap" in node_type:
                return "email"
            elif "manual" in node_type:
                return "manual"
        return "unknown"
    
    def _filter_cached_workflows(self, workflows: List[Dict], search_terms: List[str]) -> List[Dict]:
        """Filter cached workflows by search terms"""
        
        filtered = []
        
        for workflow in workflows:
            score = 0
            
            # Check filename
            filename = workflow.get("name", "").lower()
            for term in search_terms:
                if term.lower() in filename:
                    score += 3
            
            # Check services
            services = workflow.get("services", [])
            for term in search_terms:
                if any(term.lower() in service.lower() for service in services):
                    score += 5
            
            # Check trigger type
            trigger = workflow.get("trigger_type", "")
            for term in search_terms:
                if term.lower() in trigger.lower():
                    score += 2
            
            # Check content
            content = workflow.get("content", "").lower()
            for term in search_terms:
                if term.lower() in content:
                    score += 1
            
            workflow["relevance_score"] = score
            
            if score > 0:  # Only include relevant workflows
                filtered.append(workflow)
        
        return sorted(filtered, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    def _rank_by_relevance(self, workflows: List[Dict], description: str, search_terms: List[str]) -> List[Dict]:
        """Rank workflows by relevance to user description"""
        
        description_lower = description.lower()
        
        for workflow in workflows:
            base_score = workflow.get("relevance_score", 0)
            
            # Bonus for exact matches in description
            workflow_name = workflow.get("name", "").lower()
            if any(term in workflow_name and term in description_lower for term in search_terms):
                base_score += 10
            
            # Bonus for matching trigger types
            trigger = workflow.get("trigger_type", "")
            if ("webhook" in trigger and any(word in description_lower for word in ["form", "submit", "receive"])):
                base_score += 5
            elif ("schedule" in trigger and any(word in description_lower for word in ["daily", "weekly", "schedule"])):
                base_score += 5
            
            # Update score
            workflow["final_relevance_score"] = base_score
        
        return sorted(workflows, key=lambda x: x.get("final_relevance_score", 0), reverse=True)
    
    def _analyze_user_request_with_examples(self, description: str, examples: List[Dict]) -> Dict[str, Any]:
        """Create detailed analysis based on found examples"""
        
        description_lower = description.lower()
        
        # Detect trigger type
        trigger_type = "webhook"
        if any(word in description_lower for word in ["daily", "weekly", "schedule", "every", "cron"]):
            trigger_type = "schedule"
        elif any(word in description_lower for word in ["email", "mail", "imap"]):
            trigger_type = "email"
        
        # Detect services from description and examples
        detected_services = set()
        
        # From description
        service_mapping = {
            "google sheets": ["sheet", "spreadsheet", "google", "gsheet"],
            "gmail": ["email", "gmail", "mail"],
            "slack": ["slack", "notification", "message"],
            "discord": ["discord"],
            "shopify": ["shopify", "order", "ecommerce"],
            "wordpress": ["wordpress", "blog"],
            "http-request": ["api", "http", "request"],
            "webhook": ["webhook", "form", "receive"]
        }
        
        for service, keywords in service_mapping.items():
            if any(keyword in description_lower for keyword in keywords):
                detected_services.add(service)
        
        # From examples
        for example in examples[:3]:  # Top 3 examples
            detected_services.update(example.get("services", []))
        
        # Detect business logic
        business_logic = []
        if any(word in description_lower for word in ["if", "condition", "when", "only if"]):
            business_logic.append("conditional_logic")
        if any(word in description_lower for word in ["id", "unique", "number", "reference"]):
            business_logic.append("generate_unique_id")
        if any(word in description_lower for word in ["email", "notify", "send", "alert"]):
            business_logic.append("send_notification")
        
        # Extract custom names/requirements
        custom_requirements = {}
        
        # Look for quoted names
        sheet_names = re.findall(r'["\']([^"\']+)["\']', description)
        if sheet_names:
            custom_requirements["sheet_names"] = sheet_names
        
        # Detect data fields
        common_fields = ["name", "email", "phone", "company", "message", "subject"]
        detected_fields = {}
        for field in common_fields:
            if field in description_lower:
                detected_fields[field] = field.title()
        
        return {
            "trigger_type": trigger_type,
            "services_needed": list(detected_services),
            "business_logic": business_logic,
            "custom_requirements": custom_requirements,
            "data_fields": detected_fields,
            "examples_used": len(examples),
            "best_example": examples[0] if examples else None,
            "confidence": "high" if examples else "medium",
            "complexity": "high" if len(detected_services) > 2 else "medium"
        }

# Initialize the searcher
github_searcher = GitHubWorkflowSearcher()

async def search_github_examples(user_description: str) -> Tuple[List[Dict], Dict[str, Any]]:
    """Main function to search GitHub for examples"""
    return await github_searcher.search_for_examples(user_description)

# Export
__all__ = ['search_github_examples', 'github_searcher']
