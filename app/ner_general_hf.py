# Importe les classes nécessaires de Hugging Face pour charger un tokenizer et un modèle de classification de jetons 
from transformers import AutoTokenizer, AutoModelForTokenClassification 
# Importe la librairie PyTorch, utilisée par le modèle en arrière-plan
import torch 
# Importe la classe Entity -> Pydantic Model pour structurer le résultat final.
from app.models import Entity 

 # Modèle pré-entraîné à charger depuis le Hub de Hugging Face.
MODEL_NAME = "Jean-Baptiste/camembert-ner"

# Variable globale privée pour mettre en cache le tokenizer
_tokenizer = None 
 # Variable globale privée pour mettre en cache le modèle
_model = None


def _load_model():
    global _tokenizer, _model 
    # Vérifie si le tokenizer n'a pas encore été chargé (mécanisme de cache/singleton)
    if _tokenizer is None: 
        print("[NER-GENERAL] Loading model...")
        # Charge le tokenizer 
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME) 
        # Charge le modèle de classification de jetons pré-entraîné.
        _model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME) 
        # Retourne les objets tokenizer et model.
    return _tokenizer, _model 


def detect_entities_general(text: str):
    # S'assure que le modèle est chargé et récupère le tokenizer et le modèle.
    tokenizer, model = _load_model() 

    # Tokenise le texte d'entrée. return_tensors="pt" demande le format PyTorch
    inputs = tokenizer(text, return_tensors="pt") 
    
    # Passe les entrées tokenisées au modèle pour obtenir les sorties
    outputs = model(**inputs) 

    # Applique la fonction softmax sur les logits pour obtenir des scores de probabilité par classe
    scores = torch.softmax(outputs.logits, dim=-1) 
    
    # Choisit la classe (label) avec la probabilité la plus élevée pour chaque jeton. .squeeze() supprime les dimensions unitaires, .tolist() convertit en liste Python
    predictions = torch.argmax(scores, dim=-1).squeeze().tolist() 
    # Récupère la liste des jetons (inclut les jetons spéciaux comme [CLS], [SEP], etc.).
    tokens = inputs.tokens() 

    # Initialise la liste pour stocker les objets Entity détectés
    entities = [] 
    # Variable temporaire pour stocker l'entité en cours de construction (pour gérer les entités sur plusieurs jetons)
    current = None 

    # Itère sur les prédictions (un index par jeton).
    for idx, pred in enumerate(predictions): 
        # Convertit l'identifiant de la prédiction (ID) en son label de chaîne de caractères (ex: 0 -> 'O', 1 -> 'PER').
        label = model.config.id2label[pred] 

        # Récupère l'intervalle de caractères (position de début et de fin) dans le texte original correspondant au jeton actuel
        char_span = inputs.token_to_chars(idx) 
        if char_span is None:
             # Ignore les jetons spéciaux qui n'ont pas d'intervalle de caractères dans le texte original
            continue  

        # Si le jeton est une entité nommée 
        if label != "O":
            # Si aucune entité n'est en cours de construction (début d'une nouvelle entité).
            if current is None: 
                # Initialise la nouvelle entité avec le label et les positions de début et de fin du jeton actuel
                current = { 
                    "label": label,
                    "start": char_span.start,
                    "end": char_span.end,
                }
            else:
                # Si une entité est déjà en cours, étend sa fin jusqu'à la fin du jeton actuel
                current["end"] = char_span.end 

        # Si le jeton est "O" (Outside) - marque la fin d'une entité.
        else: 
             # Si une entité était en cours de construction avant ce jeton "O"
            if current:
                # Extrait le texte de l'entité dans la chaîne d'origine.
                span_text = text[current["start"]:current["end"]] 
                # Crée un objet Entity final et l'ajoute à la liste
                entities.append(Entity(
                    type=current["label"],
                    value=span_text,
                    start=current["start"],
                    end=current["end"],
                    confidence=1.0, # Confidence fixée à 1.0 par simplification 
                    source="ml" # Indique que l'entité provient d'un modèle 
                ))
                current = None # Réinitialise 'current' pour commencer à chercher la prochaine entité

    # Si le texte se termine par une entité nommée (la boucle se termine avant d'atteindre un "O")
    if current: 
        # Extrait le texte de l'entité.
        span_text = text[current["start"]:current["end"]] 
        # Crée et ajoute l'objet Entity final
        entities.append(Entity(
            type=current["label"],
            value=span_text,
            start=current["start"],
            end=current["end"],
            confidence=1.0,
            source="ml"
        ))

    return entities 