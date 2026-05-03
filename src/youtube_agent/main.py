"""Orquestador principal del agente autónomo de YouTube."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from .config import get_settings
from .research import research_topics
from .scriptwriter import generate_script
from .uploader import upload_video
from .video import assemble_video
from .visuals import generate_section_images, generate_thumbnail
from .voiceover import generate_voiceover

console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)


def _create_work_dir(base_dir: Path, title: str) -> Path:
    """Crea un directorio de trabajo para el video."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title)[:50].strip()
    safe_title = safe_title.replace(" ", "_")
    work_dir = base_dir / f"{timestamp}_{safe_title}"
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir


def create_video_pipeline(
    settings=None,
    topic: dict | None = None,
    niche: str | None = None,
    upload: bool = True,
) -> dict:
    """Pipeline completo: investigar → guion → voz → imágenes → video → subir."""
    if settings is None:
        settings = get_settings()

    result = {"success": False, "video_path": None, "video_id": None}

    # Paso 1: Seleccionar tema
    if topic is None:
        console.print(Panel("🔍 Paso 1/6: Investigando temas...", style="bold blue"))
        topics = research_topics(settings, count=5, niche=niche)
        if not topics:
            console.print("[red]No se encontraron temas. Abortando.[/red]")
            return result
        topic = topics[0]  # Seleccionar el primer tema
        console.print(f"[green]Tema seleccionado:[/green] {topic['title']}")
    else:
        console.print(f"[green]Tema:[/green] {topic.get('title', 'Sin título')}")

    title = topic.get("title", "Video Educativo")
    description = topic.get("description", "")

    work_dir = _create_work_dir(settings.output_dir, title)
    logger.info("Directorio de trabajo: %s", work_dir)

    # Guardar información del tema
    (work_dir / "topic.json").write_text(json.dumps(topic, ensure_ascii=False, indent=2))

    # Paso 2: Generar guion
    console.print(Panel("📝 Paso 2/6: Generando guion...", style="bold blue"))
    script = generate_script(settings, title, description)
    (work_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2))
    sections = script.get("sections", [])
    console.print(f"[green]Guion generado:[/green] {len(sections)} secciones")

    # Paso 3: Generar voiceover
    console.print(Panel("🎙️ Paso 3/6: Generando narración...", style="bold blue"))
    audio_files = generate_voiceover(settings, sections, work_dir)
    console.print(f"[green]Audio generado:[/green] {len(audio_files)} archivos")

    # Paso 4: Generar imágenes
    console.print(Panel("🎨 Paso 4/6: Generando imágenes...", style="bold blue"))
    image_files = generate_section_images(settings, sections, work_dir)

    # Generar miniatura
    thumbnail_text = script.get("thumbnail_text", title)
    thumbnail_path = generate_thumbnail(settings, thumbnail_text, work_dir)
    console.print(f"[green]Imágenes generadas:[/green] {len(image_files)} + miniatura")

    # Paso 5: Ensamblar video
    console.print(Panel("🎬 Paso 5/6: Ensamblando video...", style="bold blue"))
    video_path = assemble_video(settings, script, audio_files, image_files, work_dir)
    result["video_path"] = str(video_path)
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    console.print(f"[green]Video creado:[/green] {video_path.name} ({file_size_mb:.1f} MB)")

    # Paso 6: Subir a YouTube
    if upload:
        console.print(Panel("📤 Paso 6/6: Subiendo a YouTube...", style="bold blue"))
        try:
            video_id = upload_video(
                settings=settings,
                video_path=video_path,
                title=script.get("title", title),
                description=script.get("description", description),
                tags=script.get("tags", []),
                thumbnail_path=thumbnail_path,
                work_dir=work_dir,
            )
            result["video_id"] = video_id
            result["video_url"] = f"https://www.youtube.com/watch?v={video_id}"
            console.print(f"[green bold]Video subido:[/green bold] {result['video_url']}")
        except Exception as e:
            logger.error("Error subiendo a YouTube: %s", e)
            console.print(
                f"[yellow]Video guardado localmente en:[/yellow] {video_path}\n"
                f"[yellow]Puedes subirlo manualmente más tarde.[/yellow]"
            )
    else:
        console.print(f"[yellow]Video guardado (sin subir):[/yellow] {video_path}")

    result["success"] = True
    return result


@click.group()
def cli():
    """Agente autónomo de IA para crear y subir videos educativos a YouTube."""
    pass


@cli.command()
@click.option("--count", "-c", default=5, help="Número de temas a investigar")
@click.option("--niche", "-n", default=None, help="Nicho específico (ej: 'programación')")
def research(count: int, niche: str | None):
    """Investiga temas trending para videos educativos."""
    settings = get_settings()
    topics = research_topics(settings, count=count, niche=niche)

    table = Table(title="Temas Encontrados")
    table.add_column("#", style="cyan")
    table.add_column("Título", style="bold")
    table.add_column("Descripción")
    table.add_column("Interés", style="green")

    for i, topic in enumerate(topics, 1):
        table.add_row(
            str(i),
            topic.get("title", ""),
            topic.get("description", ""),
            topic.get("estimated_interest", ""),
        )

    console.print(table)


@cli.command()
@click.option("--title", "-t", required=True, help="Título del video")
@click.option("--description", "-d", default="", help="Descripción del tema")
def script(title: str, description: str):
    """Genera un guion para un video."""
    settings = get_settings()
    result = generate_script(settings, title, description)
    console.print_json(json.dumps(result, ensure_ascii=False, indent=2))


@cli.command()
@click.option("--niche", "-n", default=None, help="Nicho específico")
@click.option("--upload/--no-upload", default=True, help="Subir a YouTube automáticamente")
def create(niche: str | None, upload: bool):
    """Crea un video completo automáticamente (pipeline completo)."""
    settings = get_settings()
    console.print(
        Panel(
            "[bold magenta]🤖 Agente Autónomo de YouTube[/bold magenta]\n"
            "Iniciando pipeline de creación de video...",
            title="YouTube Agent IA",
            border_style="magenta",
        )
    )

    result = create_video_pipeline(settings=settings, niche=niche, upload=upload)

    if result["success"]:
        console.print(
            Panel(
                f"[bold green]Video creado exitosamente[/bold green]\n"
                f"📁 Archivo: {result.get('video_path', 'N/A')}\n"
                f"🔗 YouTube: {result.get('video_url', 'No subido')}",
                title="Resultado",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel("[bold red]Error en la creación del video[/bold red]", border_style="red")
        )
        sys.exit(1)


@cli.command()
@click.option("--niche", "-n", default=None, help="Nicho específico")
@click.option("--count", "-c", default=3, help="Número de videos a crear")
@click.option("--upload/--no-upload", default=True, help="Subir a YouTube automáticamente")
def batch(niche: str | None, count: int, upload: bool):
    """Crea múltiples videos en lote."""
    settings = get_settings()

    console.print(
        Panel(
            f"[bold magenta]🤖 Modo Batch: {count} videos[/bold magenta]",
            title="YouTube Agent IA",
            border_style="magenta",
        )
    )

    topics = research_topics(settings, count=count, niche=niche)

    results = []
    for i, topic in enumerate(topics[:count], 1):
        console.print(f"\n[bold cyan]═══ Video {i}/{count} ═══[/bold cyan]")
        result = create_video_pipeline(
            settings=settings,
            topic=topic,
            upload=upload,
        )
        results.append(result)

    # Resumen
    success_count = sum(1 for r in results if r["success"])
    console.print(
        Panel(
            f"[bold]Resultados: {success_count}/{count} videos creados exitosamente[/bold]",
            title="Resumen Batch",
            border_style="green" if success_count == count else "yellow",
        )
    )


if __name__ == "__main__":
    cli()
