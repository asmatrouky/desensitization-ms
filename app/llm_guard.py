# app/llm_guard.py
"""
Stub temporaire pour LLM Guard.
Permet de garder la structure du pipeline sans dépendance externe.
À remplacer plus tard par une implémentation réelle.
"""

def run_llm_guard(text: str) -> dict:
    return {
        "enabled": False,
        "decision": "ALLOW",
        "risk_score": 0.0,
        "reason": "LLM Guard disabled (stub)"
    }
