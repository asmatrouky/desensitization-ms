from typing import List, Optional
from gliner import GLiNER

from app.models import Entity

MODEL_NAME = "almanach/camembert-bio-gliner-v0.1"

_medical_model: Optional[GLiNER] = None

BIOMED_LABELS = [
    "Patient",
    "Âge",
    "Maladie",
    "Symptômes",
    "Médicament",
    "Examen",
    "Acte médical",
    "Traitement",
]


def _load_medical_model() -> GLiNER:
    global _medical_model
    if _medical_model is None:
        print("[NER-MEDICAL] Loading GLiNER medical model...")
        _medical_model = GLiNER.from_pretrained(MODEL_NAME)
    return _medical_model


def detect_entities_medical(text: str) -> List[Entity]:
    if not text or not text.strip():
        return []

    model = _load_medical_model()

    raw_entities = model.predict_entities(
        text,
        BIOMED_LABELS,
        threshold=0.5,
        flat_ner=True,
    )

    entities: List[Entity] = []
    lower_text = text.lower()
    used_pos = 0

    for ent in raw_entities:
        span = ent.get("text", "").strip()
        label = ent.get("label", "Medical")
        if not span:
            continue

        span_lower = span.lower()

        start = lower_text.find(span_lower, used_pos)
        if start == -1:
            start = lower_text.find(span_lower)
            if start == -1:
                continue

        end = start + len(span)
        used_pos = end

        ent_type = f"MED_{label.upper()}"
        confidence = float(ent.get("score", 0.9))

        entities.append(
            Entity(
                type=ent_type,
                value=text[start:end],
                start=start,
                end=end,
                confidence=confidence,
                source="ml", 
            )
        )

    return entities
