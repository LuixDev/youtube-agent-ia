# 🤖 YouTube Agent IA

**Agente autónomo de inteligencia artificial para crear y subir videos educativos en español a YouTube.**

Este agente utiliza **Grok (xAI)** para generar contenido, **Edge TTS** para la narración en español, y la **API de YouTube** para subir los videos automáticamente a tu canal.

## 🚀 ¿Qué hace?

El agente ejecuta un pipeline completo de forma autónoma:

1. **🔍 Investigación** → Identifica temas trending y de alto interés educativo
2. **📝 Guion** → Genera un guion completo en español con Grok
3. **🎙️ Narración** → Crea el audio con voces naturales en español (Edge TTS)
4. **🎨 Imágenes** → Genera imágenes con IA (Grok Aurora)
5. **🎬 Video** → Ensambla el video final con intro, secciones y outro
6. **📤 Subida** → Sube automáticamente a YouTube con título, descripción y miniatura

## 📋 Requisitos

- Python 3.11+
- FFmpeg
- Clave de API de xAI (Grok): [console.x.ai](https://console.x.ai/)
- Credenciales OAuth2 de YouTube: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

## 🛠️ Instalación

```bash
# Clonar el repositorio
git clone https://github.com/LuixDev/youtube-agent-ia.git
cd youtube-agent-ia

# Instalar dependencias con uv
uv sync

# O con pip
pip install -e .

# Instalar FFmpeg (si no lo tienes)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg
```

## ⚙️ Configuración

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Edita `.env` con tus credenciales:

```env
# Clave de xAI (Grok)
XAI_API_KEY=xai-tu-clave-aqui

# YouTube OAuth2
YOUTUBE_CLIENT_ID=tu-client-id
YOUTUBE_CLIENT_SECRET=tu-client-secret
```

### Obtener credenciales de YouTube

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo o selecciona uno existente
3. Habilita la **YouTube Data API v3**
4. Ve a **Credenciales** → **Crear credenciales** → **ID de cliente OAuth**
5. Selecciona **Aplicación de escritorio**
6. Copia el `Client ID` y `Client Secret` al archivo `.env`

### Obtener clave de xAI (Grok)

1. Ve a [console.x.ai](https://console.x.ai/)
2. Crea una cuenta o inicia sesión
3. Genera una clave de API
4. Copia la clave al archivo `.env`

## 🎮 Uso

### Crear un video automáticamente

```bash
# Crear un video completo y subirlo a YouTube
youtube-agent create

# Crear video sobre un nicho específico
youtube-agent create --niche "programación python"

# Crear video sin subir (solo guardar localmente)
youtube-agent create --no-upload
```

### Investigar temas

```bash
# Ver 5 temas trending
youtube-agent research

# Investigar 10 temas en un nicho
youtube-agent research --count 10 --niche "ciencia"
```

### Generar solo el guion

```bash
youtube-agent script --title "Cómo funciona la IA" --description "Explicación sencilla de inteligencia artificial"
```

### Crear videos en lote

```bash
# Crear 3 videos automáticamente
youtube-agent batch --count 3

# Crear 5 videos sobre tecnología sin subir
youtube-agent batch --count 5 --niche "tecnología" --no-upload
```

## 📁 Estructura del Proyecto

```
youtube-agent-ia/
├── pyproject.toml           # Dependencias y configuración
├── .env.example             # Ejemplo de variables de entorno
├── README.md                # Este archivo
├── src/
│   └── youtube_agent/
│       ├── __init__.py
│       ├── main.py          # CLI y orquestador principal
│       ├── config.py        # Configuración con Pydantic
│       ├── research.py      # Investigación de temas con Grok
│       ├── scriptwriter.py  # Generación de guiones con Grok
│       ├── voiceover.py     # Narración con Edge TTS
│       ├── visuals.py       # Generación de imágenes con Grok
│       ├── video.py         # Ensamblaje de video con MoviePy
│       └── uploader.py      # Subida a YouTube
└── output/                  # Videos generados
```

## 🎙️ Voces Disponibles (Español)

| Voz | Descripción |
|-----|-------------|
| `es-MX-JorgeNeural` | Masculina - México (default) |
| `es-MX-DaliaNeural` | Femenina - México |
| `es-ES-AlvaroNeural` | Masculina - España |
| `es-ES-ElviraNeural` | Femenina - España |
| `es-AR-TomasNeural` | Masculina - Argentina |
| `es-CO-GonzaloNeural` | Masculina - Colombia |

Cambia la voz en `.env`:
```env
TTS_VOICE=es-MX-DaliaNeural
```

## 📊 Personalización

Puedes personalizar en `.env`:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `XAI_MODEL` | Modelo de Grok | `grok-3` |
| `TARGET_DURATION` | Duración del video (segundos) | `480` (8 min) |
| `VIDEO_WIDTH` | Ancho del video | `1920` |
| `VIDEO_HEIGHT` | Alto del video | `1080` |
| `YOUTUBE_PRIVACY` | Privacidad del video | `public` |
| `YOUTUBE_CATEGORY_ID` | Categoría de YouTube | `27` (Educación) |

## 🔧 Solución de Problemas

### Error de autenticación de YouTube
La primera vez que ejecutes el agente, se abrirá el navegador para autenticar con Google. Después, el token se guarda localmente en `token.json`.

### Error de FFmpeg
Asegúrate de tener FFmpeg instalado:
```bash
ffmpeg -version
```

### Error de xAI
Verifica que tu clave de API sea válida en [console.x.ai](https://console.x.ai/).

## 📄 Licencia

MIT License
