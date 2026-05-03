"""Módulo de ensamblaje de video con MoviePy 2.x."""

import logging
import tempfile
from pathlib import Path

from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
    vfx,
)
from PIL import Image

from .config import Settings

logger = logging.getLogger(__name__)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _make_bg_image(width: int, height: int, color: tuple = (20, 20, 50)) -> str:
    """Crea una imagen de fondo sólida y retorna su path temporal."""
    img = Image.new("RGB", (width, height), color)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    return tmp.name


def _make_bar_image(width: int, height: int) -> str:
    """Crea una barra semi-transparente oscura."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 180))
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    return tmp.name


def _create_section_clip(
    image_path: Path,
    audio_path: Path,
    section_title: str,
    width: int,
    height: int,
) -> CompositeVideoClip:
    """Crea un clip de video para una sección (imagen + audio + título)."""
    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    # Imagen de fondo redimensionada
    img_clip = ImageClip(str(image_path)).with_duration(duration).resized((width, height))

    # Barra semi-transparente en la parte inferior
    bar_height = 80
    bar_path = _make_bar_image(width, bar_height)
    bar = (
        ImageClip(bar_path)
        .with_duration(duration)
        .with_position(("center", height - bar_height))
    )

    layers = [img_clip, bar]

    # Texto del título de sección
    try:
        txt_clip = (
            TextClip(
                font=FONT_PATH,
                text=section_title,
                font_size=36,
                color="white",
                size=(width - 40, None),
                method="caption",
            )
            .with_duration(min(5, duration))
            .with_position(("center", height - bar_height + 15))
            .with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])
        )
        layers.append(txt_clip)
    except Exception as e:
        logger.warning("No se pudo crear texto de sección: %s", e)

    composite = CompositeVideoClip(layers, size=(width, height)).with_audio(audio)
    return composite


def _create_intro_clip(
    title: str,
    width: int,
    height: int,
    duration: float = 4.0,
) -> CompositeVideoClip:
    """Crea un clip de introducción con el título del video."""
    bg_path = _make_bg_image(width, height)
    bg = ImageClip(bg_path).with_duration(duration)

    layers = [bg]
    try:
        txt = (
            TextClip(
                font=FONT_PATH,
                text=title,
                font_size=60,
                color="white",
                size=(width - 100, None),
                method="caption",
            )
            .with_duration(duration)
            .with_position("center")
            .with_effects([vfx.CrossFadeIn(1.0), vfx.CrossFadeOut(0.5)])
        )
        layers.append(txt)
    except Exception as e:
        logger.warning("No se pudo crear texto de intro: %s", e)

    return CompositeVideoClip(layers, size=(width, height))


def _create_outro_clip(
    width: int,
    height: int,
    duration: float = 5.0,
) -> CompositeVideoClip:
    """Crea un clip de cierre."""
    bg_path = _make_bg_image(width, height)
    bg = ImageClip(bg_path).with_duration(duration)

    layers = [bg]
    try:
        txt = (
            TextClip(
                font=FONT_PATH,
                text="Suscribete para mas contenido!\n\nDale like y comparte",
                font_size=50,
                color="white",
                size=(width - 100, None),
                method="caption",
            )
            .with_duration(duration)
            .with_position("center")
            .with_effects([vfx.CrossFadeIn(1.0), vfx.CrossFadeOut(0.5)])
        )
        layers.append(txt)
    except Exception as e:
        logger.warning("No se pudo crear texto de outro: %s", e)

    return CompositeVideoClip(layers, size=(width, height))


def assemble_video(
    settings: Settings,
    script: dict,
    audio_files: list[Path],
    image_files: list[Path],
    work_dir: Path,
) -> Path:
    """Ensambla el video final combinando imágenes, audio y texto."""
    output_path = work_dir / "final_video.mp4"
    width = settings.video_width
    height = settings.video_height
    sections = script.get("sections", [])

    logger.info("Ensamblando video: %d secciones", len(sections))

    clips = []

    # Intro
    title = script.get("title", "Video Educativo")
    intro = _create_intro_clip(title, width, height)
    clips.append(intro)

    # Secciones
    for i, (audio_path, image_path) in enumerate(zip(audio_files, image_files)):
        section = sections[i] if i < len(sections) else {}
        section_title = section.get("section_title", f"Seccion {i + 1}")

        logger.info("Procesando seccion %d/%d: %s", i + 1, len(audio_files), section_title)

        clip = _create_section_clip(
            image_path=image_path,
            audio_path=audio_path,
            section_title=section_title,
            width=width,
            height=height,
        )
        clips.append(clip)

    # Outro
    outro = _create_outro_clip(width, height)
    clips.append(outro)

    # Concatenar
    logger.info("Concatenando %d clips...", len(clips))
    final = concatenate_videoclips(clips, method="compose")

    # Exportar
    logger.info("Exportando video a: %s", output_path)
    final.write_videofile(
        str(output_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
        preset="medium",
        threads=4,
        logger=None,
    )

    # Limpiar
    final.close()
    for clip in clips:
        clip.close()

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info("Video generado: %s (%.1f MB)", output_path.name, file_size_mb)

    return output_path
