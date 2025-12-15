# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MODULE : ENTITY FUSION
# Description : Fusionne les entités détectées par les règles (rule-based) et par le modèle ML (NER).
#
# Remarque :
#   - Pour le moment on considère que les entités issues des règles sont prioritaires (IBAN, CB, EMAIL, PHONE, etc.).
#   - Si une entité ML chevauche une entité de rules (même zone de texte),
#     on ignore l'entité ML pour éviter les doublons ou conflits.
#   - Sinon, on garde l'entité ML.
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

from typing import List
from app.models import Entity

# ---------------------------------------------------------------------------------
#                               FUUUUUUSION 
# ---------------------------------------------------------------------------------
#  Args: 
#      - rule_entities: Entités détectées via regex (source="rules").
#      - ml_entities: Entités détectées via NER (source="ml").
#  Returns:
#      - Liste fusionnée d'entités sans doublons grossiers.
  
def fuse_entities(rule_entities: List[Entity], ml_entities: List[Entity]) -> List[Entity]:

    fused: List[Entity] = []        

    # 1) On ajoute toutes les entités rules (prioritaires)
    fused.extend(rule_entities)

    # 2) Pour chaque entité ML, on regarde si elle chevauche une entité rules
    for ml_ent in ml_entities:
        overlaps = False

        for rule_ent in rule_entities:
            # chevauchement si les intervalles [start, end] se recoupent
            if not (ml_ent.end <= rule_ent.start or ml_ent.start >= rule_ent.end):
                overlaps = True
                break

        if not overlaps:
            fused.append(ml_ent)

    return fused
