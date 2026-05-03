"""Módulo de subida a YouTube usando la API v3."""

import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import Settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.json"


def _get_credentials(settings: Settings, work_dir: Path) -> Credentials:
    """Obtiene o renueva credenciales OAuth2 para YouTube."""
    token_path = work_dir / TOKEN_FILE
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        logger.info("Renovando token de YouTube...")
        creds.refresh(Request())
    else:
        logger.info("Iniciando flujo de autenticación de YouTube...")

        client_config = {
            "installed": {
                "client_id": settings.youtube_client_id,
                "client_secret": settings.youtube_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }

        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)

    # Guardar token para futuras ejecuciones
    token_path.write_text(creds.to_json())
    logger.info("Token de YouTube guardado en: %s", token_path)

    return creds


def upload_video(
    settings: Settings,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: Path | None = None,
    work_dir: Path = Path("."),
) -> str:
    """Sube un video a YouTube y retorna el ID del video."""
    creds = _get_credentials(settings, work_dir)
    youtube = build("youtube", "v3", credentials=creds)

    logger.info("Subiendo video: %s", title)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": settings.youtube_category_id,
            "defaultLanguage": "es",
            "defaultAudioLanguage": "es",
        },
        "status": {
            "privacyStatus": settings.youtube_privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            logger.info("Subida: %d%%", progress)

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info("Video subido exitosamente: %s", video_url)

    # Subir miniatura si existe
    if thumbnail_path and thumbnail_path.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/png"),
            ).execute()
            logger.info("Miniatura subida exitosamente")
        except Exception as e:
            logger.warning("Error subiendo miniatura: %s", e)

    return video_id
