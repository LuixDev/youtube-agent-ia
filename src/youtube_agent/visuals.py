"""Módulo de generación de imágenes con Grok (Aurora)."""

import logging
from pathlib import Path

import httpx
from openai import OpenAI

from .config import Settings
from .research import get_xai_client

logger = logging.getLogger(__name__)


def generate_image(
    client: OpenAI,
    model: str,
    prompt: str,
    output_path: Path,
    size: str = "1792x1024",
) -> Path:
    """Genera una imagen usando Grok y la guarda en disco."""
    logger.info("Generando imagen: %s...", prompt[:80])

    response = client.images.generate(
        model=model,
        prompt=prompt,
        n=1,
        size=size,
    )

    image_url = response.data[0].url
    if not image_url:
        raise ValueError("No se recibió URL de imagen de la API")

    resp = httpx.get(image_url, timeout=60)
    resp.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(resp.content)

    logger.info("Imagen guardada: %s", output_path.name)
    return output_path


def generate_section_images(
    settings: Settings,
    sections: list[dict],
    work_dir: Path,
) -> list[Path]:
    """Genera imágenes para cada sección del video."""
    client = get_xai_client(settings)
    images_dir = work_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    image_files: list[Path] = []

    for i, section in enumerate(sections):
        visual_prompt = section.get("visual_prompt", "")
        if not visual_prompt.strip():
            section_title = section.get("section_title", "education")
            visual_prompt = f"Educational illustration about: {section_title}"

        enhanced_prompt = (
            f"{visual_prompt}. "
            "High quality, professional, educational YouTube video style, "
            "vibrant colors, clean design, 16:9 aspect ratio"
        )

        output_path = images_dir / f"section_{i:03d}.png"

        try:
            generate_image(
                client=client,
                model=settings.xai_image_model,
                prompt=enhanced_prompt,
                output_path=output_path,
            )
            image_files.append(output_path)
        except Exception as e:
            logger.warning("Error generando imagen sección %d: %s", i, e)
            # Crear imagen placeholder
            _create_placeholder(
                output_path,
                section.get("section_title", f"Sección {i + 1}"),
                settings.video_width,
                settings.video_height,
            )
            image_files.append(output_path)

        logger.info("Imagen %d/%d completada", i + 1, len(sections))

    return image_files


def generate_thumbnail(
    settings: Settings,
    prompt: str,
    work_dir: Path,
) -> Path:
    """Genera la miniatura del video."""
    client = get_xai_client(settings)
    output_path = work_dir / "thumbnail.png"

    enhanced_prompt = (
        f"{prompt}. "
        "YouTube thumbnail style, bold text overlay area, "
        "eye-catching, vibrant colors, high contrast, professional"
    )

    try:
        generate_image(
            client=client,
            model=settings.xai_image_model,
            prompt=enhanced_prompt,
            output_path=output_path,
            size="1792x1024",
        )
    except Exception as e:
        logger.warning("Error generando miniatura: %s", e)
        _create_placeholder(output_path, "THUMBNAIL", 1280, 720)

    return output_path


def _create_placeholder(
    output_path: Path,
    text: str,
    width: int,
    height: int,
) -> None:
    """Crea una imagen placeholder cuando la generación falla."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (width, height), color=(30, 30, 60))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path))
