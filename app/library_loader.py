# app/library_loader.py
import json
import os
from typing import List, Dict, Any

_CACHE: List[Dict[str, Any]] = []

def ensure_library_loaded():
    global _CACHE
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "workflows_library.json")
    if not os.path.exists(path):
        _CACHE = []
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = json.load(f)
            if isinstance(content, list):
                _CACHE = content
            else:
                _CACHE = []
    except Exception:
        _CACHE = []

def search_library_candidates(query: str, top_k: int = 3):
    if not _CACHE:
        return []
    q = query.lower()
    scored = []
    for item in _CACHE:
        txt = (item.get("name", "") + " " + " ".join(item.get("tags", [])) + " " + item.get("summary", "")).lower()
        score = sum(1 for token in q.split() if token in txt)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:top_k]]
