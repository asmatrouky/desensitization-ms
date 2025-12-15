# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# RULES_ENGINE.PY
# Description : 
#
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

import re 
from typing import List 
# Import la classe Entity -> pour les entités détectées.
from app.models import Entity
# Import la fonction qui charge les patterns regex depuis le fichier de configuration `settings.json`
from app.config import get_rule_patterns 

# Chargement dynamique des patterns
PATTERNS = get_rule_patterns() 


#---------------------------------------------------------------------------------
#                                INGESTION FICHIERS 
# ---------------------------------------------------------------------------------
# Fonction pour appliquer un ensemble de regex au texte pour détecter des entités sensibles
#    Args: 
#        text: Texte brut à analyser. 
#
#    Returns: 
#       Liste d'objets Entity représentant les éléments détectés. # Le format de sortie.

def detect_entities(text: str) -> List[Entity]: 

    # Liste qui stockera toutes les entités sensibles trouvées
    entities: List[Entity] = [] 

    # Boucle sur chaque pattern chargé dynamiquement depuis la configuration -> dictionnaire avec 'type' et 'regex'
    for pattern_data in PATTERNS: 
        # Extrait le type logique de l'entité (ex: BANK_IBAN)
        entity_type = pattern_data["type"] 
        # Extrait l'expression régulière (la chaîne de caractères brute).
        pattern = pattern_data["regex"] 
        
        # Compilation de la regex en un objet pattern (pour améliorer les performances)
        compiled_pattern = re.compile(pattern) 

        # Cherche toutes les occurrences du pattern dans le texte
        for m in compiled_pattern.finditer(text): 
            # Ajoute une nouvelle entité à la liste
            entities.append( 
                # Crée un nouvel objet Entity.
                Entity( 
                    type=entity_type, # Utilise le type de la configuration
                    value=m.group(0), # TXT exacte qui a correspondu à la regex
                    start=m.start(), #  index de début de la correspondance 
                    end=m.end(), # index de fin (exclu) de la correspondance dans le texte
                    confidence=0.99, # score de confiance élevé et fixe ( Pour le moment )
                    source="rules", # Marque l'entité comme provenant du moteur de règles
                ) 
            ) 

    # Retourne la liste des entités détectées par les règles
    return entities 