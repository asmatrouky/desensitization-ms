// ---------------------------------------------------------------------------------
//                            AFFICHAGE DU RESULTAT
// ---------------------------------------------------------------------------------
// fonction principale pour mettre à jour l'interface avec les données de la réponse API.

// Récupère depuis HTML <pre> pour afficher le texte désensibilisé
const sanitizedTextEl = document.getElementById("sanitizedText"); 
// Récupère depuis HTML le badge de décision (ALLOW/MASK/BLOCK)
const decisionBadgeEl = document.getElementById("decisionBadge"); 
// Récupère depuis HTML l'élément pour afficher le score de risque
const riskScoreEl = document.getElementById("riskScore"); 
 // Récupère depuis HTML le conteneur pour afficher la liste des entités détectées
const entitiesContainer = document.getElementById("entitiesContainer");
// Récupère l'élément pour afficher les métadonnées de la source
const metadataInfoEl = document.getElementById("metadataInfo"); 


const llmGuardDecisionEl = document.getElementById("llmGuardDecision");
const llmGuardScoreEl = document.getElementById("llmGuardScore");
const llmGuardFlagsEl = document.getElementById("llmGuardFlags");
const llmGuardContainer = document.getElementById("llmGuardContainer");

function displayResult(data) { 
    // Si aucune donnée n'est passée, arrête la fonction.
    if (!data) return; 
    // Affiche le texte désensibilisé ou un tiret par défaut dans l'element HTML <pre id="sanitizedText">
    sanitizedTextEl.textContent = data.sanitized_text || "—"; 
    // Vérifie si le score est un nombre valide
    if (typeof data.risk_score === "number") { 
        // Affiche le score arrondi à deux décimales
        riskScoreEl.textContent = "Score : " + data.risk_score.toFixed(2); 
    } else {
        // Affiche un tiret si le score est absent ou invalide.
        riskScoreEl.textContent = "Score : — "; 
    }

    // Initialise la variable du HTML du badge.
    let badge = ""; 
    // Crée le HTML pour ALLOW
    if (data.decision === "ALLOW") badge = `<span class="badge badge-allow">ALLOW</span>`; 
    // Crée le HTML pour MASK
    if (data.decision === "MASK")  badge = `<span class="badge badge-mask">MASK</span>`; 
    // Crée le HTML pour BLOCK
    if (data.decision === "BLOCK") badge = `<span class="badge badge-block">BLOCK</span>`; 

    // Insère le badge HTML dans l'élément html <p id="decisionBadge"></p>
    decisionBadgeEl.innerHTML = badge; 

    // Récupère la liste des entités détéctée sensibles 
    const entities = data.entities || []; 
    // S'il n'y a pas d'entités affiche un message d'absence
    if (entities.length === 0) {
        entitiesContainer.innerHTML = "<p>Aucune entité sensible détectée.</p>"; 
    } else {
        // Initialise la chaîne HTML pour les lignes du tableau
        let rows = ""; 
        // Boucle sur chaque entité
        entities.forEach((e) => { 
        // Pour chaque entitée -> une ligne de tableau avec : type, valeur, confiance, indices et source
        rows += `
            <tr>
            <td>${e.type}</td>
            <td>${e.value}</td>
            <td>${(e.confidence * 100).toFixed(1)}%</td>
            <td>${e.start}–${e.end}</td>
            <td>${e.source}</td>
            </tr>`; 
        }); 
        // Construit le tableau complet entête + lignes construit AVEC ROWS juste avant et insere dansle html <div id="entitiesContainer"></div>
        entitiesContainer.innerHTML = `
        <table>
            <thead>
            <tr>
                <th>Type</th>
                <th>Valeur</th>
                <th>Confiance</th>
                <th>Span</th>
                <th>Source</th>
            </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>`; 
    } 
    // Vérifie que l'élément metadata et les données existent.
    if (metadataInfoEl && data.metadata) { 
        const m = data.metadata; 
        // Récupère le type de source
        const source = m.source_type || "—"; 
        // Récupère le nom de fichier
        const filename = m.filename || "—"; 
        // Affiche les infos dans le HTML<p id="metadataInfo" class="muted"></p>
        metadataInfoEl.textContent = `Source : ${source} | Fichier : ${filename}`; 
    }

    // -------------------------------
    // AFFICHAGE RÉSULTAT LLM GUARD
    // -------------------------------
    if (
      data.metadata &&
      data.metadata.llm_guard &&
      llmGuardContainer
    ) {
      const g = data.metadata.llm_guard;

      // Affiche le container
      llmGuardContainer.style.display = "block";

      // Décision
      llmGuardDecisionEl.textContent =
        "Décision LLM Guard : " + (g.llm_guard_decision || "—");

      // Score
      if (typeof g.llm_guard_score === "number") {
        llmGuardScoreEl.textContent =
          "Score LLM Guard : " + g.llm_guard_score.toFixed(2);
      } else {
        llmGuardScoreEl.textContent = "Score LLM Guard : —";
      }

      // Flags
      if (Array.isArray(g.llm_guard_flags) && g.llm_guard_flags.length > 0) {
        llmGuardFlagsEl.innerHTML = g.llm_guard_flags
          .map(f => `<li>${f}</li>`)
          .join("");
      } else {
        llmGuardFlagsEl.innerHTML = "<li>Aucun risque détecté</li>";
      }

    } else if (llmGuardContainer) {
      // Cache si pas de résultat
      llmGuardContainer.style.display = "none";
    }

    }


// ---------------------------------------------------------------------------------
//                         SECTION SOUMISSIONS TEXTE UNIQUE
// ---------------------------------------------------------------------------------

// Récupère depuis HTML le bouton d'analyse de texte brut
const btn = document.getElementById("analyzeBtn"); 
// Récupère depuis HTML le champ de texte d'entrée.
const input = document.getElementById("inputText"); 

// Attend clique sur bouton "Analyser"
btn.addEventListener("click", async () => { 
  // Récupère le texte entré et supprime les espaces inutiles
  const text = input.value.trim(); 
  // Si le champ est vide, arrête
  if (!text) return; 

  // Sinon Envoie une requête POST asynchrone à l'endpoint /sanitize
  const res = await fetch("/sanitize", { 
    method: "POST", // Méthode HTTP POST
    headers: { "Content-Type": "application/json" },  // Spécifie que le corps est au format JSON
    body: JSON.stringify({ text }) // Convertit le texte en JSON pour l'envoi
  });

  // Vérifie si la réponse HTTP est un succès 
  if (!res.ok) { 
    // Log l'erreur dans la console si le statut n'est pas OK
    console.error("Erreur HTTP /sanitize", res.status); 
    return; 
  }

  // Parse la réponse JSON de l'API.
  const data = await res.json(); 
  // Affiche les résultats dans l'interface en utilisant la fonction utilitaire.
  displayResult(data); 
});



// ---------------------------------------------------------------------------------
//                          SECTION SOUMISSIONS D'UN FICHIER
// ---------------------------------------------------------------------------------

// Récupère depuis HTML le champ input[type="file"]
const fileInput = document.getElementById("fileInput"); 
// Récupère depuis HTML le bouton analyse de fichier
const analyzeFileBtn = document.getElementById("analyzeFileBtn"); 
// Récupère depuis HTML l'élément pour afficher les métadonnées du fichier.
const fileMetadataEl = document.getElementById("fileMetadata"); 

// Attend clique sur bouton "Analyser le fichier"
analyzeFileBtn.addEventListener("click", async () => { 
  // Récupère le 1er fichier sélectionné
  const file = fileInput.files[0]; 
  // Si auncun fichier a été sélectionné affiche un message d'erreur 
  if (!file) { 
    fileMetadataEl.textContent = "Merci de sélectionner un fichier."; 
    return; 
  }

  // Crée un objet FormData pour envoyer des fichiers
  const formData = new FormData(); 
  // ajt le fichier file à l'objet FormData avec clé "file"
  formData.append("file", file); 

  // Envoie la requête POST au endpoint /sanitize-file ( notre back )
  const res = await fetch("/sanitize-file", {  
    method: "POST", // Méthode HTTP POST
    body: formData // Corps FormData, /!\ NE PAS mettre Content-Type ici, fetch le gère pour multipart/form-data.
  });

  // Si statut HTTP pas ok
  if (!res.ok) {
    // Affiche l'erreur HTTP
    fileMetadataEl.textContent = "Erreur HTTP /sanitize-file : " + res.status; 
    return; 
  }
  // sinon parse la réponse JSON.
  const data = await res.json(); 

  // Et appeler displayResult() pour afficher le resultat
  displayResult(data);

  // Si les métadonnées spécifiques au fichier sont présentes.
  if (data.metadata) {
    const m = data.metadata; 
    // Initialise un tableau pour stocker les chaînes de métadonnées.
    const details = []; 
    // Ajoute le nom du fichier.
    if (m.filename) details.push("Fichier : " + m.filename); 
    // Ajoute le type de source (pdf ou docx ou image)
    if (m.source_type) details.push("Type : " + m.source_type); 
     // Ajoute le nombre de pages si PDF
    if (m.pages) details.push("Pages : " + m.pages);
    // Ajoute le nombre de paragraphes si DOCX
    if (m.paragraphs) details.push("Paragraphes : " + m.paragraphs); 
    // Ajoute les dimensions si image OCR
    if (m.width && m.height) details.push(`Dimensions : ${m.width}x${m.height}`); 
    // Joint toutes les métadonnées avec un séparateur " | "
    fileMetadataEl.textContent = details.join(" | "); 
  } else {
    fileMetadataEl.textContent = ""; // Vide le champ s'il n'y a pas de métadonnées.
  }
});


// ---------------------------------------------------------------------------------
//                          SECTION SOUMISSIONS D'UN JEU DE DONNÉE
// ---------------------------------------------------------------------------------
// Fonction asynchrone pour lire le contenu d'un fichier en tant que texte.


// Récupère depuis HTML le champ input[type="file"] pour le dataset
const datasetFileInput = document.getElementById("datasetFile"); 
// Récupère depuis HTML le bouton pour lancer les tests
const runDatasetBtn = document.getElementById("runDatasetBtn"); 
// Récupère depuis HTML le conteneur principal des résultats du dataset
const datasetResults = document.getElementById("datasetResults"); 
// Récupère depuis HTML l'élément pour afficher le résumé (réussis/total)
const datasetSummary = document.getElementById("datasetSummary"); 
// Récupère depuis HTML le conteneur pour le tableau de résultats détaillés
const datasetTableContainer = document.getElementById("datasetTableContainer"); 

async function readFileAsText(file) { 
  // Retourne une Promise gérer asynchrone
  return new Promise((resolve) => { 
    // Création un objet FileReader
    const reader = new FileReader(); 
    // Quand lecture est finie rend la Promise 
    reader.onload = (e) => resolve(e.target.result); 
    // Lance lecture du fichier avec encodage UTF-8
    reader.readAsText(file, "utf-8"); 
  }); 
}

// Attend clique sur bouton Lancer les tests
runDatasetBtn.addEventListener("click", async () => { 
  // Récupère le JSON sélectionné
  const file = datasetFileInput.files[0]; 
  // Arrêt si aucun fichier n'est sélectionné
  if (!file) return; 

  // Sinon Désactive le bouton pour éviter les clics multiples pendant le traitement
  runDatasetBtn.disabled = true; 
  // Affiche la section des résultats du dataset
  datasetResults.style.display = "block";
  // message de chargement
  datasetSummary.textContent = "Tests en cours..."; 
  // Vide le tableau précédent
  datasetTableContainer.innerHTML = ""; 

  // Attend la lecture du fichier JSON ( voir en haut )
  const content = await readFileAsText(file); 
  // Parse le contenu JSON en tableau d'objets 
  const tests = JSON.parse(content);
  
  // Chaîne HTML pour les lignes du tableau de résultats.
  let rows = ""; 
  // Compteur des tests réussis
  let passed = 0; 

   // Boucle sur chaque chaque entrée du dataset de test
  for (const t of tests) {
    // Envoie le chaque entrée de test à l'API /sanitize
    const res = await fetch("/sanitize", { 
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: t.text })
    });

    // Récupère le résultat de l'analyse.
    const data = await res.json(); 
    // Extrait tous les types d'entités détectées sensibles
    const detected = data.entities.map((e) => e.type); 
    // Récupère les types d'entités attendues 
    const expected = t.expected_entities || []; 

    // Vérifie si toutes les entités attendues ont été détectées.
    // Renvoie true si chaque attente 'x' est dans la liste 'detected'.
    const ok = expected.every((x) => detected.includes(x)); 

    // Incrémente le compteur de score si le test est réussi.
    if (ok) passed++; 
    // Construit la ligne de tableau pour ce test spécifique.
    rows += `
      <tr>
        <td>${t.id}</td>
        <td>${expected.join(", ")}</td>
        <td>${detected.join(", ")}</td>
        <td>${data.decision}</td>
        <td>${data.risk_score.toFixed(2)}</td>
        <td>${ok ? "OK" : "KO"}</td>
      </tr>
    `; 
  } 

  // Met à jour le résumé du dataset
  datasetSummary.textContent = `${passed} / ${tests.length} tests réussis.`; 
  
  // Affiche le tableau de résultats détaillés
  datasetTableContainer.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Attendu</th>
          <th>Détecté</th>
          <th>Décision</th>
          <th>Score</th>
          <th>Statut</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`; 
  // Réactive le bouton de lancement des tests
  runDatasetBtn.disabled = false; 
});
