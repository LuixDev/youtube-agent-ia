"""Módulo de generación de voz con Edge TTS."""

import asyncio
import logging
from pathlib import Path

import edge_tts

from .config import Settings

logger = logging.getLogger(__name__)


async def _generate_audio(
    text: str,
    voice: str,
    output_path: Path,
) -> Path:
    """Genera audio con Edge TTS de forma asíncrona."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return output_path


def generate_voiceover(
    settings: Settings,
    sections: list[dict],
    work_dir: Path,
) -> list[Path]:
    """Genera archivos de audio para cada sección del guion."""
    audio_dir = work_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_files: list[Path] = []

    for i, section in enumerate(sections):
        narration = section.get("narration", "")
        if not narration.strip():
            continue

        output_path = audio_dir / f"section_{i:03d}.mp3"
        logger.info(
            "Generando audio sección %d/%d: %s",
            i + 1,
            len(sections),
            section.get("section_title", ""),
        )

        asyncio.run(_generate_audio(narration, settings.tts_voice, output_path))
        audio_files.append(output_path)
        logger.info("Audio guardado: %s", output_path.name)

    logger.info("Total de archivos de audio generados: %d", len(audio_files))
    return audio_files
