"""Módulo de generación de imágenes con PIL (100% gratuito, sin API externa)."""

import logging
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .config import Settings

logger = logging.getLogger(__name__)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Paletas de colores profesionales para videos educativos
COLOR_PALETTES = [
    {"bg_start": (25, 25, 112), "bg_end": (0, 0, 50), "accent": (0, 200, 255)},
    {"bg_start": (20, 60, 20), "bg_end": (0, 30, 0), "accent": (100, 255, 100)},
    {"bg_start": (80, 20, 80), "bg_end": (40, 0, 40), "accent": (255, 100, 255)},
    {"bg_start": (100, 40, 0), "bg_end": (50, 20, 0), "accent": (255, 180, 50)},
    {"bg_start": (20, 60, 80), "bg_end": (10, 30, 50), "accent": (0, 220, 200)},
    {"bg_start": (60, 20, 20), "bg_end": (30, 10, 10), "accent": (255, 80, 80)},
]


def _draw_gradient(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    color_start: tuple,
    color_end: tuple,
) -> None:
    """Dibuja un gradiente vertical."""
    for y in range(height):
        ratio = y / height
        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def _draw_decorative_elements(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    accent: tuple,
) -> None:
    """Dibuja elementos decorativos geométricos."""
    # Círculos decorativos semi-transparentes
    for _ in range(5):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        radius = random.randint(50, 200)
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=(*accent, 60),
            width=2,
        )

    # Líneas diagonales decorativas
    for i in range(3):
        x_offset = random.randint(-200, width)
        draw.line(
            [(x_offset, height), (x_offset + 400, 0)],
            fill=(*accent, 25),
            width=1,
        )


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Divide el texto en líneas que quepan en el ancho dado."""
    words = text.split()
    lines: list[str] = []
    current_line: list[str] = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def generate_section_image(
    title: str,
    section_number: int,
    total_sections: int,
    width: int,
    height: int,
    output_path: Path,
) -> Path:
    """Genera una imagen profesional para una sección del video."""
    palette = COLOR_PALETTES[section_number % len(COLOR_PALETTES)]

    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Fondo con gradiente
    _draw_gradient(draw, width, height, palette["bg_start"], palette["bg_end"])

    # Elementos decorativos
    _draw_decorative_elements(draw, width, height, palette["accent"])

    # Barra superior con acento
    draw.rectangle([0, 0, width, 6], fill=palette["accent"])

    # Número de sección
    try:
        num_font = ImageFont.truetype(FONT_PATH, 120)
    except OSError:
        num_font = ImageFont.load_default()

    section_num = str(section_number + 1)
    num_bbox = num_font.getbbox(section_num)
    num_w = num_bbox[2] - num_bbox[0]
    draw.text(
        (width - num_w - 60, height - 180),
        section_num,
        fill=(*palette["accent"], 40),
        font=num_font,
    )

    # Título principal
    try:
        title_font = ImageFont.truetype(FONT_PATH, 52)
    except OSError:
        title_font = ImageFont.load_default()

    lines = _wrap_text(title, title_font, width - 160)
    total_text_height = len(lines) * 65
    y_start = (height - total_text_height) // 2 - 20

    for i, line in enumerate(lines):
        bbox = title_font.getbbox(line)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2

        # Sombra del texto
        draw.text((x + 3, y_start + i * 65 + 3), line, fill=(0, 0, 0, 180), font=title_font)
        # Texto principal
        draw.text((x, y_start + i * 65), line, fill=(255, 255, 255), font=title_font)

    # Barra inferior con indicador de progreso
    bar_y = height - 8
    draw.rectangle([0, bar_y, width, height], fill=(0, 0, 0, 100))
    progress_width = int(width * (section_number + 1) / total_sections)
    draw.rectangle([0, bar_y, progress_width, height], fill=palette["accent"])

    # Convertir a RGB y guardar
    img_rgb = img.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_rgb.save(str(output_path), quality=95)

    logger.info("Imagen generada: %s", output_path.name)
    return output_path


def generate_section_images(
    settings: Settings,
    sections: list[dict],
    work_dir: Path,
) -> list[Path]:
    """Genera imágenes para cada sección del video."""
    images_dir = work_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    image_files: list[Path] = []

    for i, section in enumerate(sections):
        section_title = section.get("section_title", f"Seccion {i + 1}")
        output_path = images_dir / f"section_{i:03d}.png"

        generate_section_image(
            title=section_title,
            section_number=i,
            total_sections=len(sections),
            width=settings.video_width,
            height=settings.video_height,
            output_path=output_path,
        )
        image_files.append(output_path)
        logger.info("Imagen %d/%d completada", i + 1, len(sections))

    return image_files


def generate_thumbnail(
    settings: Settings,
    title: str,
    work_dir: Path,
) -> Path:
    """Genera la miniatura del video."""
    output_path = work_dir / "thumbnail.png"
    width, height = 1280, 720

    palette = random.choice(COLOR_PALETTES)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Fondo gradiente vibrante
    _draw_gradient(draw, width, height, palette["bg_start"], palette["bg_end"])

    # Borde llamativo
    border = 8
    draw.rectangle(
        [border, border, width - border, height - border],
        outline=palette["accent"],
        width=border,
    )

    # Título grande
    try:
        title_font = ImageFont.truetype(FONT_PATH, 64)
    except OSError:
        title_font = ImageFont.load_default()

    lines = _wrap_text(title, title_font, width - 120)
    total_text_height = len(lines) * 80
    y_start = (height - total_text_height) // 2

    for i, line in enumerate(lines):
        bbox = title_font.getbbox(line)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2

        # Sombra fuerte
        draw.text((x + 4, y_start + i * 80 + 4), line, fill=(0, 0, 0), font=title_font)
        # Texto blanco
        draw.text((x, y_start + i * 80), line, fill=(255, 255, 255), font=title_font)

    img_rgb = img.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_rgb.save(str(output_path), quality=95)

    logger.info("Miniatura generada: %s", output_path.name)
    return output_path
