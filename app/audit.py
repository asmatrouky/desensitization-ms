import json
from datetime import datetime
from typing import List
from app.models import Entity


def log_audit(raw_text: str, entities: List[Entity], decision: str, risk_score: float):
    """
    Journalise une entrée d'audit pour une requête /sanitize.
    Principe :
        - On ne stocke PAS le texte brut (raw_text)
        - On conserve uniquement :
            - timestamp
            - décision
            - score de risque
            - nombre d'entités trouvées
            - nombre par type

    Args:
        raw_text: Texte d'origine 
        entities: Entités détectées
        decision: Décision globale
        risk_score: Score de risque global
    """
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "decision": decision,
        "risk_score": risk_score,
        "entities_count": len(entities),
        "types_count": {},
    }

    for e in entities:
        audit_entry["types_count"].setdefault(e.type, 0)
        audit_entry["types_count"][e.type] += 1

    with open("audit.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
