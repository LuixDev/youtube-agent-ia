# YouTube Agent IA

Agente autónomo de IA para crear y subir videos educativos en español a YouTube. **100% gratuito** - no requiere APIs de pago.

## Stack Tecnológico (Todo Gratuito)

| Componente | Tecnología | Costo |
|------------|-----------|-------|
| Guiones e investigación | **Groq** (Llama 3.3 70B) | Gratis |
| Narración de voz | **Edge TTS** (voces naturales en español) | Gratis |
| Imágenes de secciones | **PIL** (gráficos generados) | Gratis |
| Ensamblaje de video | **MoviePy** + FFmpeg | Gratis |
| Subida a YouTube | **YouTube Data API v3** | Gratis |

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- FFmpeg (`sudo apt install ffmpeg` en Ubuntu)

## Instalación

```bash
git clone https://github.com/LuixDev/youtube-agent-ia.git
cd youtube-agent-ia
uv sync
```

## Configuración

1. Copia el archivo de configuración:

```bash
cp .env.example .env
```

2. Configura tus credenciales en `.env`:

### Groq API Key (Gratuito)

1. Ve a https://console.groq.com/keys
2. Crea una cuenta (puedes usar Google)
3. Click "Create API Key"
4. Copia la clave en `GROQ_API_KEY`

### YouTube API (Para subir videos)

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo
3. Habilita la **YouTube Data API v3**
4. Ve a **Credenciales** > **Crear credenciales** > **ID de cliente OAuth**
5. Tipo de aplicación: **Aplicación de escritorio**
6. Copia `Client ID` y `Client Secret` en el `.env`

## Uso

### Crear un video completo y subirlo

```bash
youtube-agent create
```

### Crear video sobre un tema específico

```bash
youtube-agent create --niche "programación python"
```

### Crear video sin subir a YouTube

```bash
youtube-agent create --no-upload
```

### Crear múltiples videos en lote

```bash
youtube-agent batch --count 3
youtube-agent batch --count 5 --niche "inteligencia artificial"
```

### Solo investigar temas trending

```bash
youtube-agent research
youtube-agent research --count 10 --niche "ciencia"
```

### Generar solo un guion

```bash
youtube-agent script --title "Cómo aprender Python" --description "Tutorial para principiantes"
```

## Pipeline Completo

```
1. 🔍 Investigación  → Groq genera ideas de temas trending
2. 📝 Guion          → Groq escribe el guion completo en español
3. 🎙  Narración     → Edge TTS genera el audio con voz natural
4. 🎨 Imágenes       → PIL crea gráficos profesionales por sección
5. 🎬 Video          → MoviePy ensambla todo (intro + secciones + outro)
6. 📤 Upload         → YouTube API sube el video con título, descripción y miniatura
```

## Voces Disponibles

| Voz | Código | Región |
|-----|--------|--------|
| Jorge (por defecto) | `es-MX-JorgeNeural` | México |
| Dalia | `es-MX-DaliaNeural` | México |
| Elvira | `es-ES-ElviraNeural` | España |
| Álvaro | `es-ES-AlvaroNeural` | España |
| Tomás | `es-AR-TomasNeural` | Argentina |
| Gonzalo | `es-CO-GonzaloNeural` | Colombia |

Cambia la voz en `.env`:

```
TTS_VOICE=es-MX-DaliaNeural
```

## Modelos de Groq Disponibles (Gratis)

| Modelo | Descripción |
|--------|-------------|
| `llama-3.3-70b-versatile` | Recomendado, mejor calidad |
| `mixtral-8x7b-32768` | Rápido, buen contexto |
| `llama-3.1-8b-instant` | Ultra rápido, menor calidad |

## Estructura del Proyecto

```
src/youtube_agent/
├── config.py        # Configuración con Pydantic
├── research.py      # Investigación de temas
├── scriptwriter.py  # Generación de guiones
├── voiceover.py     # Narración con Edge TTS
├── visuals.py       # Generación de imágenes con PIL
├── video.py         # Ensamblaje de video
├── uploader.py      # Subida a YouTube
└── main.py          # CLI principal
```

## Troubleshooting

### "FFmpeg not found"
```bash
sudo apt install ffmpeg
```

### Error de autenticación YouTube
La primera vez que subas un video, se abrirá tu navegador para autorizar la app. El token se guarda en `token.json` para futuras ejecuciones.

### Rate limit de Groq
El tier gratuito permite 30 peticiones por minuto. Si ves errores 429, espera un momento y reintenta.

## Licencia

MIT
