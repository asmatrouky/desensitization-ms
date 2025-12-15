# Importe la librairie standard pour travailler avec les données JSON.
import json 
from typing import Dict, Any, List 

# Chemin du fichier de configuration par défaut
CONFIG_FILE_PATH = "settings.json" 

# Variable globale privée (convention _nom) pour stocker la configuration chargée, initialisée à un dictionnaire vide
_config: Dict[str, Any] = {} 



# ---------------------------------------------------------------------------------
#                          CHARGEMENT DE LA CONFIGURATION 
# ---------------------------------------------------------------------------------
# Fonction pour charge la configuration à partir du fichier JSON.
# Met en cache la configuration pour éviter des relectures.

def load_config(file_path: str = CONFIG_FILE_PATH) -> Dict[str, Any]:

    global _config 
    # Vérifie si la configuration n'a pas encore été chargée 
    if not _config: 
        try:
            # Tente d'ouvrir le fichier en mode lecture ('r'), avec encodage UTF-8
            with open(file_path, "r", encoding="utf-8") as f: 
                # Charge le contenu JSON du fichier dans globale _config
                _config = json.load(f) 
        # Erreur si le fichier n'existe pas
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {file_path}. Please create one.")
        # Erreur si le fichier JSON est mal formaté
        except json.JSONDecodeError as e: 
            # Erreur si le décodage échoue, incluant l'erreur d'origine.
            raise ValueError(f"Error decoding JSON configuration file: {e}")

    return _config # Retourne le dictionnaire de configuration chargé.




# ---------------------------------------------------------------------------------
#                      RECUPERATION DE LA CONFIGURATION 
# ---------------------------------------------------------------------------------
# Récupère la configuration chargée
# Charge la configuration si elle ne l'est pas encore.

def get_config() -> Dict[str, Any]:
     # Vérifie si la configuration n'est pas encore en cache.
    if not _config:
         # Si elle n'est pas en cache, appelle la fonction pour la charger (et la mettra en cache)
        return load_config()
    return _config


# ---------------------------------------------------------------------------------
#                      RECUPERATION DU RISQUE
# ---------------------------------------------------------------------------------
# Retourne la section 'risk_engine' de la configuration.

def get_risk_config() -> Dict[str, Any]:
    return get_config()["risk_engine"] 


# ---------------------------------------------------------------------------------
#                      RECUPERATION DU RISQUE DEPUIS IHM - en cours ATY
# ---------------------------------------------------------------------------------
# Met à jour les poids de risque dans la configuration en mémoire.
# Ceci permet au decision_engine d'utiliser les nouvelles valeurs immédiatement.

def update_risk_weights(new_weights: Dict[str, float]):
    global _config 
    # Accède à la section 'weights' dans 'risk_engine' et lui assigne le nouveau dictionnaire de poids
    _config["risk_engine"]["weights"] = new_weights 
    

# ---------------------------------------------------------------------------------
#                      RECUPERATION DU POIDS DES RISQUE 
# ---------------------------------------------------------------------------------
# Retourne la pondération des risques (à ne plus utiliser directement dans decision_engine)
def get_risk_weights() -> Dict[str, float]:
    # Récupère toute la configuration, puis les sections 'risk_engine' et 'weights'
    return get_config()["risk_engine"]["weights"]

# ---------------------------------------------------------------------------------
#                      RECUPERATION DES PATERNS REGEX 
# ---------------------------------------------------------------------------------
def get_rule_patterns() -> List[Dict[str, str]]:
    # Récupère les patterns de la section 'rules_engine'.
    return get_config()["rules_engine"]["patterns"]

# ---------------------------------------------------------------------------------
#                      RECUPERATION DE LA CONFIANCE MOTEUR ML
# ---------------------------------------------------------------------------------
def get_ml_confidence() -> float:
    # Récupère la valeur de confiance par défaut de la section 'ml_engine'.
    return get_config()["ml_engine"]["default_confidence"]