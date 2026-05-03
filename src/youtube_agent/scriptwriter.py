"""Módulo de generación de guiones con Groq (Llama 3)."""

import json
import logging

from .config import Settings
from .research import get_llm_client

logger = logging.getLogger(__name__)

SCRIPT_PROMPT = """\
Eres un guionista profesional de videos educativos de YouTube en español.

Crea un guion completo para un video educativo sobre:
Título: {title}
Descripción: {description}

El guion debe:
- Durar aproximadamente {duration} minutos cuando se lee en voz alta
- Estar completamente en español (latinoamericano)
- Tener un gancho atractivo en los primeros 10 segundos
- Incluir una introducción, desarrollo con secciones claras, y conclusión
- Usar un tono conversacional pero informativo
- Incluir llamados a la acción (suscribirse, dar like, comentar)
- Cada sección debe tener indicaciones visuales para las imágenes

Devuelve el guion en formato JSON:
{{
    "title": "Título del video",
    "description": "Descripción para YouTube (máx 5000 caracteres, con hashtags)",
    "tags": ["tag1", "tag2", ...],
    "sections": [
        {{
            "section_title": "Nombre de la sección",
            "narration": "Texto de narración para esta sección...",
            "visual_prompt": "Descripción de imagen para esta sección",
            "duration_estimate_seconds": 30
        }}
    ],
    "thumbnail_text": "Texto corto y llamativo para la miniatura (máx 5 palabras)"
}}

Responde SOLO con el JSON.
"""


def generate_script(
    settings: Settings,
    title: str,
    description: str,
) -> dict:
    """Genera un guion completo para un video educativo usando Groq."""
    client = get_llm_client(settings)

    duration_minutes = settings.target_duration // 60

    logger.info("Generando guion para: %s", title)

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un guionista experto de videos educativos de YouTube en español. "
                    "Siempre respondes en formato JSON válido."
                ),
            },
            {
                "role": "user",
                "content": SCRIPT_PROMPT.format(
                    title=title,
                    description=description,
                    duration=duration_minutes,
                ),
            },
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content or "{}"

    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    script = json.loads(content)

    sections = script.get("sections", [])
    total_words = sum(len(s.get("narration", "").split()) for s in sections)
    logger.info(
        "Guion generado: %d secciones, ~%d palabras, ~%d min estimado",
        len(sections),
        total_words,
        total_words // 150,
    )

    return script
