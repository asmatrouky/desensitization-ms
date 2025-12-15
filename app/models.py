# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MODELS.PY
# Description : 
#
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

from typing import List, Dict, Literal 
# Import Pydantic pour définir les modèles de données avec validation
from pydantic import BaseModel 

# ---------------------------------------------------------------------------------
#                        Entity - ELEMENT SENSIBLE DETECTE
# ---------------------------------------------------------------------------------
# Modèle Pydantic, garantissant la structure de chaque élément sensible détecté.
class Entity(BaseModel): 
    type: str # ( STRING ) Type logique de l'entité -> ex: 'BANK_IBAN', 'EMAIL', 'PHONE' 
    value: str # ( STRING ) Valeur brute trouvée dans le texte
    start: int # ( INT ) Index de début de la valeur ( chaîne originale ) 
    end: int # ( INT ) Index de fin (exclu)
    confidence: float #  ( FLOAT ) Score de confiance entre 0 et 1 
    source: Literal["rules", "ml"] = "rules" # Origine de la détection ('rules' pour regex, 'ml' pour un modèle NER plus tard)





# ---------------------------------------------------------------------------------
#                      SanitizeRequest - TEXT BRUT A ANALYSER
# ---------------------------------------------------------------------------------
# Modèle Pydantic, garantissant la structure du corps de la requête POST pour l'analyse de texte.
class SanitizeRequest(BaseModel):
    text: str # ( STRING ) Texte brut à analyser et désensibiliser



# ---------------------------------------------------------------------------------
#                            SanitizeResponse - RESPONSE 
# ---------------------------------------------------------------------------------
# Modèle Pydantic, garantissant la structure du corps de la réponse JSON renvoyée par l'endpoint /sanitize.

class SanitizeResponse(BaseModel):
    sanitized_text: str # Version désensibilisée du texte d'origine. 
    decision: Literal["ALLOW", "MASK", "BLOCK"] # Décision globale ('ALLOW', 'MASK', 'BLOCK')
    risk_score: float # Score de risque global entre 0 et 1
    entities: List[Entity] # Liste des entités sensibles détectées
    metadata: Dict[str, object] = {} #  Métadonnées techniques




# ---------------------------------------------------------------------------------
#                      SanitizeResponse - RESPONSE ( en cours )
# ---------------------------------------------------------------------------------
# La classe WeightsUpdate modélise la requête pour la modification dynamique de la ponderation

class WeightsUpdate(BaseModel): 
    weights: Dict[str, float] # Le corps de la requête doit contenir un dictionnaire 'weights' -> (clé=str, valeur=float)