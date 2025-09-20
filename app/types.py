# app/types.py
from typing import TypedDict, List, Dict, Any

class N8NNode(TypedDict, total=False):
    id: str
    name: str
    type: str
    typeVersion: int
    position: List[int]
    parameters: Dict[str, Any]
