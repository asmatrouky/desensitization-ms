from typing import List
from app.models import Entity


def apply_masking(text: str, entities: List[Entity], decision: str) -> str:
    """
    Stratégie actuelle :
        - ALLOW : renvoie le texte tel quel.
        - MASK  : remplace chaque entité par un token de type <TYPE_MASKED>.
        - BLOCK : renvoie un message générique indiquant que le texte est trop sensible.

    Args:
        text: Texte d'origine.
        entities: Entités détectées dans le texte.
        decision: 'ALLOW', 'MASK' ou 'BLOCK'.

    Returns:
        Texte désensibilisé (ou message générique en cas de BLOCK)
    """

    # Si la décision est "ALLOW", retourne le texte original sans modification
    if decision == "ALLOW":
        return text 

    # Si la décision est "BLOCK", retourne un message générique (texte bloqué)
    if decision == "BLOCK":
        return "Texte trop sensible pour être envoyé tel quel." 
    # Initialise la variable de texte désensibilisé avec le texte original
    sanitized = text 

    # Important : on remplace en partant de la fin.
    # Trie la liste des entités par leur position de départ ('start') de manière décroissante (reverse=True)
    for e in sorted(entities, key=lambda x: x.start, reverse=True): 
        # Crée le jeton de masquage au format <TYPE_MASKED>
        token = f"<{e.type}_MASKED>" 
        
        # Effectue le remplacement : 
        # 1. Prend la partie du texte avant l'entité (jusqu'à e.start).
        # 2. Ajoute le token de masquage.
        # 3. Ajoute la partie du texte après l'entité (à partir de e.end).
        sanitized = sanitized[:e.start] + token + sanitized[e.end:] 

    return sanitized