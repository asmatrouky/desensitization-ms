# 🔐 Microservice de désensibilisation – V1 (BPCE Project Lab)

Ce projet est un **microservice de désensibilisation** jouant le rôle de **proxy de sécurité**
entre un utilisateur interne (ou une application métier) et un système d’IA générative.

Il reçoit du **texte brut ou des fichiers (PDF, DOCX, images)**, détecte des **données sensibles**
(bancaires, personnelles, médicales), calcule un **score de risque**, applique une **politique de sécurité**
(`ALLOW`, `MASK`, `BLOCK`) et renvoie un **texte désensibilisé**.

---

## 🎯 Objectifs de la V1

- Empêcher la fuite de données sensibles vers des modèles d’IA
- Fournir une décision explicable (`ALLOW / MASK / BLOCK`)
- Être modulaire, auditable et extensible
- Fonctionner comme un microservice indépendant (FastAPI + Docker)

---

## 🧱 Architecture (V1)

- **FastAPI**
  - `/` : page HTML de démonstration
  - `/sanitize` : désensibilisation de texte brut
  - `/sanitize-file` : désensibilisation de fichiers (multipart)
  - `/health` : healthcheck
- **Ingestion**
  - Texte brut
  - PDF / DOCX
  - Images (OCR avec Tesseract)
- **Détection des entités**
  - Moteur de règles (regex)
  - NER général (Hugging Face)
  - NER médical
- **Fusion des entités**
  - Priorité aux règles déterministes
- **Scoring & décision**
  - Calcul d’un `risk_score` ∈ [0,1]
  - Décision : `ALLOW`, `MASK`, `BLOCK`
- **Masquage**
  - Remplacement par des tokens `<TYPE_MASKED>`
- **Audit**
  - Journalisation des décisions (sans stocker le texte brut)
- **LLM Guard**
  - Stub local (désactivé en V1, prévu pour V2)

---

## 🐳 Installation avec Docker (recommandé)

### 1️⃣ Installer Docker Desktop

#### macOS / Windows
- Télécharger Docker Desktop :  
  https://www.docker.com/products/docker-desktop/
- Installer puis lancer Docker Desktop
- Vérifier l’installation :

```bash
docker --version
docker info
Linux
https://docs.docker.com/engine/install/

2️⃣ Cloner le projet
bash
Copier le code
git clone <url-du-repo>
cd desensitization-ms
3️⃣ Build de l’image Docker
À la racine du projet (là où se trouve le Dockerfile) :

bash
Copier le code
docker build -t my-desensitization-ms-app .
⚠️ Le build peut prendre quelques minutes (dépendances ML).

4️⃣ Lancer le microservice
bash
Copier le code
docker run -p 8000:8000 my-desensitization-ms-app
5️⃣ Accéder à l’application
Healthcheck
http://localhost:8000/health

Documentation Swagger
http://localhost:8000/docs

Interface HTML de démonstration
http://localhost:8000/

🧪 Exemples d’utilisation
🔹 Texte brut (/sanitize)
Exemple de texte :

yaml
Copier le code
Bonjour Jean Dupont,
Votre IBAN est FR76 3000 6000 0112 3456 7890 123
et votre email est jean.dupont@example.com
Résultat :

entités détectées (IBAN, EMAIL, etc.)

score de risque

texte masqué ou bloqué selon la politique

🔹 Fichier (/sanitize-file)
Formats supportés :

PDF

DOCX

Images (PNG / JPG – OCR)

Le texte est extrait, analysé, puis désensibilisé.

🛠️ Développement local (sans Docker – optionnel)
bash
Copier le code
python -m venv venv
source venv/bin/activate  # macOS / Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
Puis :

http://127.0.0.1:8000/docs

🧠 Notes importantes
Microservice CPU-only (pas de GPU / CUDA)

Compatible Docker / CI

Stub LLM Guard pour une architecture future-proof

Aucun texte sensible n’est stocké dans les logs

🔜 Évolutions prévues (V2)
Implémentation complète du LLM Guard (prompt injection, exfiltration)

Configuration dynamique des règles et pondérations

Authentification / contrôle d’accès

Déploiement cloud (CI/CD)

👩‍💻 Contexte
Projet réalisé dans le cadre du BPCE Project Lab
Microservice expérimental orienté sécurité des prompts et données sensibles.

Copier le code
