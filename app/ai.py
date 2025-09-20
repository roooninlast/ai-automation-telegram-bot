# app/ai.py
# يستعمل OpenRouter API للحوار وبناء مخطّط الوركفلو ثم إخراج n8n JSON
import os
import json
import httpx
from typing import Any

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")  # غيّرها كما تحب
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYS_PLANNER = (
    "You are an automation architect for n8n. "
    "Your job: extract missing details via assumptions (be sane), propose a clear trigger + steps, "
    "and output a concise plan describing each node purpose and edges."
)

SYS_JSONER = (
    "You are an expert n8n workflow generator. "
    "Output MUST be a *single valid JSON* for n8n import with keys: name, nodes, connections, settings, tags. "
    "IDs must be unique strings. Prefer generic env refs like {{$env.SHEET_ID}} not secrets. "
    "Include a reasonable trigger (webhook/cron/manual), ensure connections match node IDs."
)

async def _chat(system: str, user: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(OPENROUTER_URL, headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

async def plan_workflow_with_ai(user_prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        return f"Trigger: decide based on prompt.\nSteps: parse → fetch/process → output.\nUserPrompt: {user_prompt}"
    return await _chat(SYS_PLANNER, user_prompt)

async def draft_n8n_json_with_ai(plan: str) -> str:
    if not OPENROUTER_API_KEY:
        example = {
            "name": "Webhook → Google Sheets (Sample)",
            "nodes": [
                {
                    "id": "wh1",
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [200, 200],
                    "parameters": {"path": "auto_generate", "responseMode": "onReceived"}
                },
                {
                    "id": "gs1",
                    "name": "Append to Sheet",
                    "type": "n8n-nodes-base.googleSheets",
                    "typeVersion": 1,
                    "position": [520, 200],
                    "parameters": {
                        "operation": "append",
                        "sheetId": "={{$env.SHEET_ID}}",
                        "range": "={{$env.SHEET_RANGE}}"
                    }
                }
            ],
            "connections": {"wh1": {"main": [[{"node": "gs1", "type": "main", "index": 0}]]}},
            "settings": {},
            "tags": ["generated", "sample"]
        }
        return json.dumps(example)
    return await _chat(SYS_JSONER, plan)
