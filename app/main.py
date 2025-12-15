# Import FastAPI -> API, requêtes HTTP, téléchargements de fichiers...
from fastapi import FastAPI, Request, UploadFile, File 
# Import pour renvoyer des réponses HTML
from fastapi.responses import HTMLResponse 
# Import Templates Jinja2 pour l'UI
from fastapi.templating import Jinja2Templates 
# Import pr fichiers statiques (CSS, JS, images)
from fastapi.staticfiles import StaticFiles 

# Import Pydantic pour les schémas de données (modèles de requête) -> voir models.py
# from pydantic import BaseModel 
from app.models import SanitizeRequest, WeightsUpdate, SanitizeResponse, Entity 

# Import des fonctions de ingestion.py pr ingérer le texte, pdf, images...
from app.ingestion import ingest_text, ingest_file 
# Import la fonction pr détecter les entités nommées (NER) via ML (spaCy)
#from app.ner_engine import detect_entities_ml 
# Import la fonction pr détecter les entités medicals (Camembert bio)
from app.ner_medical import detect_entities_medical
# Import la fonction pr détecter les entités via des règles customiser 
from app.rules_engine import detect_entities 
# Import la fonction de fusion des deux moteurs -> spaCy ET rules_engine
from app.entity_fusion import fuse_entities
# Import la fonction pr calculer le score de risque et prendre une décision (ALLOW/MASK/BLOCK).
from app.decision_engine import compute_decision 
# Import la fonction pour appliquer le masquage ou le blocage au texte.
from app.masking_engine import apply_masking 
# Import pour journaliser les resultat de la requête dans un fichier d'audit.
from app.audit import log_audit 
# Importe la fonction pour màj dela pondération (pour la configuration dynamique depuis IHM)
from app.config import update_risk_weights 

from app.ner_general_hf import detect_entities_general

from app.llm_guard import run_llm_guard


# ---------------------------------------------------------------------------------
#                               INITIALISATION APP
# ---------------------------------------------------------------------------------

app = FastAPI() 
app.mount("/static", StaticFiles(directory="static"), name="static") 
templates = Jinja2Templates(directory="templates") 


# ---------------------------------------------------------------------------------
#                   PIPELINE UNIQUE UTILISÉ PAR LES 2 ENDPOINTS
# ---------------------------------------------------------------------------------
# Fonction centrale qui exécute toutes les étapes du pipeline.
#   - rules : Étape de détection par règles.
#   - ml : Étape de détection par Machine Learning.
#   - fusion : Étape de fusion des entités.
#   - scoring : Étape de calcul du score de risque.
#   - masking : Étape de désensibilisation.
#   - audit : Étape de journalisation.

#   texte : string  source_type        extra_metadata

def run_sanitization_pipeline(text: str, source_type: str, extra_metadata=None): 

    # 1) Module RULE-BASED -> Détecte les données sensibles via les regex qu'on a mis en place
    rule_entities = detect_entities(text) 

    # 2) ML model camembert-> Détecte les données sensibles via le modèle ML.
    #ml_entities = detect_entities_ml(text) 
    general_entities = detect_entities_general(text)

     # 3) ML médical -> via modele bio machin 
    medical_entities = detect_entities_medical(text)

    # 3) FUSION -> Fusionne les résultat en donnant la priorité à nos régles
    entities = fuse_entities(rule_entities, general_entities + medical_entities)
    
    # 4) DECISION -> Calcule le score de risque global et détermine la décision de sécurité -> ALLOW / MASK / BLOCK
    decision, risk_score = compute_decision(entities) 

    # 5) MASKING -> Applique le masquage ou le blocage du texte selon la décision
    sanitized_text = apply_masking(text, entities, decision) 

    # 6) AUDIT -> Journalise la requête, la décision et les statistiques sans le texte brut
    log_audit(text, entities, decision, risk_score) 

    # Initialise les métadonnées de la réponse avec le type de source (texte/fichier)
    metadata = {"source_type": source_type} 

    # 8) LLM GUARD -> Analyse parallèle du texte brut pour pouvoir comparer avec notre pipeline à nous -> en cours ATY
    llm_guard_result = run_llm_guard(text)
    
    # Si métadonnées supplémentaires (ex: taille, pages) 
    if extra_metadata: 
        # Les ajoute 
        metadata.update(extra_metadata) 

    # Retourne le dictionnaire de résultats 
    return SanitizeResponse( 
        sanitized_text = sanitized_text, 
        decision = decision,
        risk_score = risk_score,
        entities = entities,
        metadata = {
            **metadata,
            "llm_guard": llm_guard_result
        }
    )

# ---------------------------------------------------------------------------------
#                               PAGE HTML (IHM)
# ---------------------------------------------------------------------------------
# Décorateur FastAPI pour définir un endpoint GET à la racine ('/') qui renvoie du HTML.
@app.get("/", response_class=HTMLResponse) 
# Définit la fonction de vue pour la page d'accueil.
def index(request: Request): 
    # Charge et renvoie le template HTML de l'IHM de démo.
    return templates.TemplateResponse("index.html", {"request": request}) 


# ---------------------------------------------------------------------------------
#                                 API TEXTE BRUT
# ---------------------------------------------------------------------------------
# Décorateur FastAPI pour définir un endpoint POST à l'URL '/sanitize'.
@app.post("/sanitize") 
# La requête POST attend le modèle SanitizeRequest ( voir models.py ou documentation partie modeles )
def sanitize(req: SanitizeRequest): 

    # Traite le texte brut pour obtenir le texte et les métadonnées avec fonction ingest_text() du module ingestion qui retourne raw_text, source_type, metadata
    ingest_res = ingest_text(req.text) 

    # Exécute le pipeline de désensibilisation 
    return run_sanitization_pipeline( 
        # Passage du texte brut
        text=ingest_res.raw_text, 
        # Passage du type de source ('text')
        source_type=ingest_res.source_type, 
        # Passage des métadonnées (taille, langue, etc.)
        extra_metadata=ingest_res.metadata, 
    ) 


# ---------------------------------------------------------------------------------
#                       API FICHIER (PDF, DOCX, IMAGE, OCR)
# ---------------------------------------------------------------------------------
# Décorateur FastAPI pour définir un endpoint POST à l'URL '/sanitize-file'
@app.post("/sanitize-file") 

# La requête attend un fichier téléchargé (asynchrone)
async def sanitize_file(file: UploadFile = File(...)): 
    # Recupere contenu binaire du fichier téléchargé.
    content = await file.read()

    # Traite le contenu binaire pour extraire le texte avec la fonction ingest_file() du module Ingestion
    ingest_res = ingest_file(
        # Passage du contenu binaire
        content=content, 
        # Passage du nom de fichier pour deviner le type de source
        filename=file.filename, 
        # Passage du type MIME pour deviner le type de source
        content_type=file.content_type, 
    ) 

    # Exécute le pipeline de désensibilisation sur le texte extrait du fichier.
    return run_sanitization_pipeline( 
        # Passage du texte extrait
        text=ingest_res.raw_text, 
        # Passage du type de source ('pdf', 'docx', 'image')
        source_type=ingest_res.source_type, 
        # Passage des métadonnées du fichier (pages, taille, dimensions image, etc.).
        extra_metadata=ingest_res.metadata, 
    )

# ---------------------------------------------------------------------------------
#                        UPDATE CONFIG ( EN COURS - ATY )
# ---------------------------------------------------------------------------------
# Décorateur FastAPI pour définir l'endpoint de mise à jour dynamique de la configuration des coefs pour le scoring
@app.post("/config/weights") 
# La requête POST attend le modèle WeightsUpdate (contenant le dictionnaire des coef ).

def update_weights(req: WeightsUpdate): 
  
    try: 
         # Appelle la fonction pour modifier l'état interne (la configuration en mémoire).
        update_risk_weights(req.weights)
        # Retourne un statut de succès.
        return {"status": "success", "message": "Poids de risque mis à jour avec succès."} 
    except Exception as e: 
        # Log et retour d'erreur si la mise à jour échoue (ex: problème de structure interne)
        return {"status": "error", "message": f"Erreur lors de la mise à jour : {str(e)}"} # Retourne un statut d'erreur avec le message de l'exception.


# ---------------------------------------------------------------------------------
#                                  HEALTHCHECK
# ---------------------------------------------------------------------------------
@app.get("/health") 
def health():
    # Renvoie un statut simple pour indiquer que le service est opérationnel.
    return {"status": "OK", "service": "desensitization-ms"} 