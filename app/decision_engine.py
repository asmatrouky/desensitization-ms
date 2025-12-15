from typing import List, Tuple
from app.models import Entity
from app.config import get_risk_config # Import de la fonction pour obtenir la config à jour

# NOTE: Les variables globales comme WEIGHTS, MASK_THRESHOLD, etc. sont supprimées 
# ou commentées car elles doivent être chargées DANS la fonction compute_decision 
# pour être dynamiques.

def compute_decision(entities: List[Entity]) -> Tuple[str, float]:
    """
    Calcule un score de risque global à partir des entités détectées, puis
    applique une politique de décision simple.

    Logique :
        - Lit la configuration de risque la plus récente.
        - Somme des poids de chaque entité.
        - Normalisation /10 puis clamp entre 0 et 1.

    Args:
        entities: Liste d'entités détectées.

    Returns:
        Tuple (decision, risk_score).
    """
    # Chargement dynamique de la configuration à chaque appel
    RISK_CONFIG = get_risk_config()
    WEIGHTS = RISK_CONFIG["weights"]
    DEFAULT_WEIGHT = RISK_CONFIG["default_weight"]
    MASK_THRESHOLD = RISK_CONFIG["thresholds"]["MASK"]
    BLOCK_THRESHOLD = RISK_CONFIG["thresholds"]["BLOCK"]
    
    score = 0.0

    for e in entities:
        # Utilise le poids par défaut si le type n'est pas dans la config
        score += WEIGHTS.get(e.type, DEFAULT_WEIGHT)

    risk_score = min(score / 10.0, 1.0)

    if risk_score < MASK_THRESHOLD:
        decision = "ALLOW"
    elif risk_score < BLOCK_THRESHOLD:
        decision = "MASK"
    else:
        decision = "BLOCK"

    return decision, risk_score