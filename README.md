# YouTube Music Downloader

Un descargador de música de YouTube con Python que obtiene la mejor calidad y metadatos completos.

## 🚀 Características

- ✅ Descarga canciones individuales
- ✅ Descarga playlists completas
- ✅ Búsqueda por texto
- ✅ Múltiples formatos (MP3, M4A, FLAC)
- ✅ Metadatos automáticos (título, artista, duración)
- ✅ Thumbnails incrustados
- ✅ Mejor calidad disponible
- ✅ Interfaz interactiva

## 📦 Instalación

### Instalación automática
```bash
chmod +x install.sh
./install.sh
```

### Instalación manual
```bash
# Instalar dependencias
pip3 install -r requirements.txt

# Instalar ffmpeg (Ubuntu/Debian)
sudo apt install ffmpeg

# Instalar ffmpeg (macOS con Homebrew)
brew install ffmpeg
```

## 🎵 Uso

### Ejecutar el programa
```bash
python3 youtube_music_downloader.py
```

### Uso desde código
```python
from youtube_music_downloader import YouTubeMusicDownloader

# Crear descargador
downloader = YouTubeMusicDownloader("./mis_descargas")

# Descargar canción individual
downloader.download_single("https://music.youtube.com/watch?v=...", "mp3")

# Descargar playlist
downloader.download_playlist("https://music.youtube.com/playlist?list=...", "best")

# Buscar y descargar
downloader.search_and_download("Bohemian Rhapsody Queen", "flac", max_results=1)
```

## 🎼 Formatos disponibles

- **`best`**: Mejor calidad disponible (recomendado)
- **`mp3`**: Formato MP3 con máxima calidad
- **`m4a`**: Formato M4A nativo de YouTube
- **`flac`**: Formato sin pérdida (para audiofilia)

## 📁 Estructura de archivos descargados

```
downloads/
├── Artista - Canción.m4a
├── Artista - Canción.info.json
└── Artista - Canción.webp
```

## 💡 Ejemplos de URLs compatibles

- YouTube Music: `https://music.youtube.com/watch?v=...`
- YouTube: `https://www.youtube.com/watch?v=...`
- Playlists: `https://music.youtube.com/playlist?list=...`

## 🔧 Solución de problemas

### Error: "yt-dlp not found"
```bash
pip3 install --upgrade yt-dlp
```

### Error: "ffmpeg not found"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### Error de permisos
```bash
chmod +x youtube_music_downloader.py
```

## ⚖️ Consideraciones legales

- Solo descarga música que tengas derecho a descargar
- Respeta los derechos de autor
- Uso personal únicamente
- No redistribuyas contenido con copyright

## 🛠️ Dependencias

- Python 3.6+
- yt-dlp
- ffmpeg
- mutagen (para metadatos)
- Pillow (para thumbnails)