# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MODULE : INGESTION
# Description : 

# Objectif :
#  - 
#  -
# Remarque : 
#  - Revoir la sortie desirée, pour le moment les fichiées sont traitée comme des texte, on ne génére pas de fichier
#  - Partie Image ne fonctionne pas correctement 
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

from dataclasses import dataclass 
from typing import Dict, Optional 
import io 
import os 
import pdfplumber
import docx 
from PIL import Image 
import pytesseract 


# Classe pour stocker le résultat de l'ingestion.
@dataclass 
class IngestResult: 
    # Texte brut extrait du contenu.
    raw_text: str 
    # Type de source (ex: "text", "pdf", "docx", "image").
    source_type: str 
    # Dictionnaire contenant les métadonnées de la source (taille, pages, etc.).
    metadata: Dict[str, object] 


# ---------------------------------------------------------------------------------
#                               INGESTION TEXTE BRUT
# ---------------------------------------------------------------------------------

def ingest_text(text: str) -> IngestResult: 
    # Riztourne un objet IngestResult
    return IngestResult( 
        # Le texte extrait est le texte d'entrée
        raw_text=text, 
        # La source est 'text'
        source_type="text", 
        # Définit les métadonnées
        metadata={ 
             # Pas de nom de fichier vu que c'est pas un fichier 
            "filename": None,
            # Calcule la taille en octets du texte encodé en UTF-8 -> Maybe utile pour analyse des logs 
            "size": len(text.encode("utf-8")), 
            # Langue fixée au français pour la version actuelle 
            "lang": "fr",  
        }, 
    ) 


# ---------------------------------------------------------------------------------
#                                INGESTION FICHIERS 
# ---------------------------------------------------------------------------------
# -> Fonction principale pour l'ingestion de fichiers 
# -> Elle va appeler la bonne fonction pour traiter le fichier selon son le type 
# -> Utilisé par l'endpoint /sanitize-file depuis le main

def ingest_file(content: bytes, filename: Optional[str], content_type: Optional[str]) -> IngestResult: 
    
    # Appelle _guess_source_type() pour déterminer le type de fichier.
    source_type = _guess_source_type(filename, content_type) 

    # Si le type est PDF appelle _ingest_pdf
    if source_type == "pdf": 
        return _ingest_pdf(content, filename or "document.pdf") 
    # Si le type est DOCX appelle _ingest_docx()
    if source_type == "docx": 
        return _ingest_docx(content, filename or "document.docx")
    # Si le type est image appelle _ingest_image_ocr()
    if source_type == "image": 
        return _ingest_image_ocr(content, filename or "image") # Appelle l'ingesteur OCR.

    # Si c'est ni PDF ni DOCX ni image
    try: 
        # On essaye de décoder le contenu binaire en UTF-8, ignorant les erreurs.
        text = content.decode("utf-8", errors="ignore") 
    except Exception: 
        # Définit le texte à vide en cas d'échec de décodage 
        text = " ERREUR INGESTION " 

    # Retourne le résultat pour le fallback binaire ou texte.
    return IngestResult( 
        raw_text=text, # le texte ou message ERREUR INGESTION
        source_type=source_type, # Type de source -> 'binary' si non reconnu
        metadata={ 
            "filename": filename, # nom du fichier
            "size": len(content), # taille en octets
            "lang": "fr", # Langue -> français.
        }, 
    ) 



# ---------------------------------------------------------------------------------
#                               DEVINER LE FICHIER 
# ---------------------------------------------------------------------------------
# Devine le type de source à partir de l'extension ou du content_type

def _guess_source_type(filename: Optional[str], content_type: Optional[str]) -> str: 
    
    # Vérifie si le type MIME -> le content_type <- est fourni ( MIME = norme qui permet d'identifier la nature et le format d'un fichier)
    if content_type: 
        # Si oui alors convertit le type MIME en minuscules pour la comparaison
        ct = content_type.lower() 
         # Comparaison pour definir le type de fichier
        if "pdf" in ct:
            return "pdf" 
        if "word" in ct or "officedocument" in ct: 
            return "docx" 
        if "image" in ct: 
            return "image" 
        
    # Si le nom de fichier est fourni.
    if filename: 
        ext = os.path.splitext(filename)[1].lower() # Extrait l'extension et la met en minuscules
        # Et rebelotte -> comparaison pour definir le type de fichier
        if ext == ".pdf": 
            return "pdf" 
        if ext in (".docx", ".doc"): 
            return "docx" 
        if ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"): 
            return "image" 
    
    # Retourne "binary" par défaut si aucun type n'a pu être deviné.
    return "binary" 

# ---------------------------------------------------------------------------------
#                                INGESTION PDF 
# ---------------------------------------------------------------------------------

def _ingest_pdf(content: bytes, filename: str) -> IngestResult: 
    # Initialise une liste pour stocker le texte de chaque page
    text_parts = []
    # Ouvre le contenu binaire du PDF avec pdfplumber
    with pdfplumber.open(io.BytesIO(content)) as pdf: 
        # Itère sur toutes les pages du PDF
        for page in pdf.pages: 
            # Extraction du texte de la page ou " "  si échec
            page_text = page.extract_text() or "" 
            # Ajoute le texte de la page à la liste
            text_parts.append(page_text) 

    # full_text = Les textes de la page avec un saut de ligne
    full_text = "\n".join(text_parts) 

    # Retourne le résultat de l'ingestion
    return IngestResult( 
        raw_text=full_text, # Txt extrait 
        source_type="pdf", # source -> 'pdf'
        metadata={
            "filename": filename, # nom du fichier
            "pages": len(text_parts), # n pages
            "size": len(content), # taille en octets 
            "lang": "fr", # Langue -> fr
        }, 
    ) 

# ---------------------------------------------------------------------------------
#                                INGESTION DOCX 
# ---------------------------------------------------------------------------------

def _ingest_docx(content: bytes, filename: str) -> IngestResult: 
    # Tampon en mémoire à partir du contenu binaire
    file_like = io.BytesIO(content) 
    # Ouvre le docx à partir du tampon en mémoire
    document = docx.Document(file_like) 
    # Recupere txt de chaque paragraphe dans une liste
    text_parts = [p.text for p in document.paragraphs] 
    # Joint les txt des paragraphes avec un saut de ligne + ignore  paragraphes vides
    full_text = "\n".join(t for t in text_parts if t) 

    # Retourne résultat de l'ingestion
    return IngestResult( 
        raw_text=full_text, # Txt extrait 
        source_type="docx", # source -> 'docx'.
        metadata={ 
            "filename": filename, # nom du fichier.
            "paragraphs": len(text_parts), # n paragraphes.
            "size": len(content), # taille en octets 
            "lang": "fr", # Langue -> fr
        }, 
    ) 


# ---------------------------------------------------------------------------------
#                                INGESTION IMAGE 
# ---------------------------------------------------------------------------------
# Fonction pour extraire le texte d'une image via OCR (Tesseract)
# Nécessite que tesseract soit installé sur la machine : 
# - macOS : brew install tesseract

def _ingest_image_ocr(content: bytes, filename: str) -> IngestResult: 
    
    # Ouvre l'image avec PIL/Pillow.
    image = Image.open(io.BytesIO(content)) 
    # ext l'OCR sur img pr extraire le txt en forçant le fr
    text = pytesseract.image_to_string(image, lang="fra") 

    # Retourne résultat de l'ingestion
    return IngestResult( 
        raw_text=text, # Txt extrait 
        source_type="image", # source -> 'image'
        metadata={
            "filename": filename, # nom du fichier
            "size": len(content), # taille en octets 
            "width": image.width, # largeur de l'image en px
            "height": image.height, # hauteur de l'image en px
            "mode": image.mode, # mode de couleur de l'image (ex: RGB, L)
            "lang": "fr", #Langue -> fr
        }, 
    ) 


