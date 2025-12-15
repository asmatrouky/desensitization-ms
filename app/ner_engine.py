# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MODULE : 
# Description : Moteur NER basé sur spaCy  

# Objectif :
#  - Détecter des entités "sémantiques" (PERSON, ORG, LOC, DATE, etc.)
#    dans un texte français.
#  - Retourner ces entités au même format que celles du module rules_engine
#    pour pouvoir ensuite les fusionner.

# Remarque :
#   - spaCy ne fournit pas "nativement" un score de confiance par entité.
#   - On utilise donc une valeur fixe pour le moment pour indiquer
#     qu'il s'agit d'une détection ML avec un niveau de confiance raisonnable
#   - Mapping des labels spaCy vers des types plus "génériques" A ALIMENTER 
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

from typing import List 
from app.models import Entity 
import spacy 

# Variable globale pour stocker le modèle chargé une seule fois
# Initialisé à None pour le chargement paresseux (lazy loading)
_nlp = None 

# ---------------------------------------------------------------------------------
#                               CHARGEMENT DE SPACY
# ---------------------------------------------------------------------------------
# Fonction interne pour charger le modèle spaCy.
# Charge et met en cache le modèle spaCy français.
# Utilise fr_core_news_md : python -m spacy download fr_core_news_md 

def _get_nlp():
    global _nlp 
    if _nlp is None: 
        _nlp = spacy.load("fr_core_news_md") 
    return _nlp 

# ---------------------------------------------------------------------------------
#                      DICTIONNAIRE DE TYPES ( A ALIMENTER )
# ---------------------------------------------------------------------------------
# Mapping des labels spaCy vers des types plus "génériques" ( A ALIMENTER )
# REMARQUE : spaCy peut aussi renvoyer des labels comme : "DATE", "TIME", "MONEY"
# Les autres labels sont conservés tels quels p

LABEL_MAP = { 
    "PER": "PERSON", 
    "ORG": "ORGANIZATION", 
    "LOC": "LOCATION"} 

# ---------------------------------------------------------------------------------
#                      DETECTION DE DONNEE SENSIBLE 
# ---------------------------------------------------------------------------------
#Applique le modèle NER spaCy au texte pour détecter des entités nommées.
#  Args: 
#   - text: Texte brut en français. 
#  Returns: 
#   - Liste d'Entity détectées par le modèle ML. 

def detect_entities_ml(text: str) -> List[Entity]: 

    # Récupère l'objet modèle spaCy chargé 
    nlp = _get_nlp() 
    # Traite le texte avec le modèle spaCy avec 'doc' = les entités.
    doc = nlp(text) 
    # Liste qui contiendra les entités au format standard.
    entities: List[Entity] = [] 

    # Boucle sur les entités dans 'doc'.
    for ent in doc.ents: 
        # Normalisation du label avec LABEL_MAP 
        ent_type = LABEL_MAP.get(ent.label_, ent.label_) 
        # Définit la confiance fixe par défaut pour toutes les entités ML (A REVOIR !!!!)
        confidence = 0.85 
        # Ajoute une nouvelle entité à la liste des résultats.
        entities.append( 
            # Crée un nouvel objet Entity.
            Entity( 
                # Le type de l'entité PERSON, ORGANIZATION, ...
                type=ent_type, 
                # Le texte exact de l'entité telle que trouvée par spaCy.
                value=ent.text, 
                # L'index de début de l'entité dans la chaîne originale.
                start=ent.start_char, 
                # L'index de fin (exclu) de l'entité dans la chaîne originale.
                end=ent.end_char, 
                # Le score de confiance fixe pour le moment à 0.85
                confidence=confidence, 
                # Indique que l'entité provient du moteur Machine Learning pour la fusion
                source="ml", 
            ) 
        ) 
    # Retourne la liste finale des entités au format standard Entity.
    return entities 