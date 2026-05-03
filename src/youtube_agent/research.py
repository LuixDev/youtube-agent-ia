"""Módulo de investigación de temas trending en YouTube."""

import json
import logging

from openai import OpenAI

from .config import Settings

logger = logging.getLogger(__name__)

TOPIC_PROMPT = """\
Eres un experto en contenido educativo de YouTube en español.
Tu tarea es generar {count} ideas de videos educativos/tutoriales que sean:
- Trending o de alto interés actualmente
- Aptos para un canal educativo en español
- Con potencial de muchas visualizaciones
- Sobre temas que la gente busca activamente

Para cada idea, devuelve un JSON con esta estructura:
{{
    "topics": [
        {{
            "title": "Título atractivo para YouTube (máx 60 caracteres)",
            "description": "Descripción breve del tema (1-2 oraciones)",
            "keywords": ["palabra1", "palabra2", "palabra3"],
            "target_audience": "Audiencia objetivo",
            "estimated_interest": "alto/medio"
        }}
    ]
}}

{context}

Responde SOLO con el JSON, sin texto adicional.
"""


def get_llm_client(settings: Settings) -> OpenAI:
    """Crea un cliente OpenAI compatible con Groq."""
    return OpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
    )


def research_topics(
    settings: Settings,
    count: int = 5,
    niche: str | None = None,
) -> list[dict]:
    """Genera ideas de temas educativos usando Groq (Llama 3)."""
    client = get_llm_client(settings)

    context = ""
    if niche:
        context = f"Enfócate en el nicho: {niche}"

    logger.info("Investigando %d temas educativos trending...", count)

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": "Eres un investigador de contenido para YouTube en español.",
            },
            {
                "role": "user",
                "content": TOPIC_PROMPT.format(count=count, context=context),
            },
        ],
        temperature=0.8,
    )

    content = response.choices[0].message.content or "{}"

    # Extraer JSON del contenido
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    data = json.loads(content)
    topics = data.get("topics", [])

    logger.info("Se encontraron %d temas.", len(topics))
    return topics
