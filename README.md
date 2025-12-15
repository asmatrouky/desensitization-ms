# Microservice de désensibilisation – V1 (BPCE PLab)

Ce projet est un prototype de microservice de désensibilisation qui agit comme un proxy de sécurité
entre un utilisateur interne et un modèle d'IA générative.

Il reçoit un texte brut, détecte des données sensibles (bancaires / personnelles), calcule un score
de risque, applique une politique de masquage et renvoie un texte désensibilisé.

---

## 🧱 Architecture simplifiée (V1)

- **FastAPI** : exposition des endpoints `/health`, `/sanitize` et d'une page HTML de démo (`/`).
- **Moteur de règles regex** : détection déterministe de :
  - IBAN français (`BANK_IBAN`)
  - numéros de carte (`BANK_CARD`)
  - emails (`EMAIL`)
  - numéros de téléphone FR (`PHONE`)
- **Moteur de scoring** :
  - pondération par type d'entité,
  - calcul d'un `risk_score` entre 0 et 1,
  - décision : `ALLOW`, `MASK` ou `BLOCK`.
- **Moteur de masquage** :
  - `ALLOW` : texte inchangé,
  - `MASK` : remplacement par des tokens `<TYPE_MASKED>`,
  - `BLOCK` : texte remplacé par un message générique.
- **Audit** :
  - journalisation dans `audit.log` (décision, score, nombre d'entités, types),
  - le texte brut n'est pas stocké.

---

## ⚙️ Installation

```bash
git clone <url-du-repo>
cd desensitization-ms

# Configuration pyenv éventuelle :
# pyenv local 3.9.18

python -m venv venv
source venv/bin/activate  # macOS / Linux

pip install -r requirements.txt


## Lancement du microservice
uvicorn app.main:app --reload

# Ouvrir un navigateur sur : http://127.0.0.1:8000/
# Saisir un texte du type : Bonjour Jean Dupont, votre IBAN est FR76 3000 6000 0112 3456 7890 123 et votre email est jean.dupont@example.com
# Cliquer sur "Analyser / désensibiliser".

# Visualiser :




Politique de risque configurable (JSON / YAML).


