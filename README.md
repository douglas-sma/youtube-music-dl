# YouTube Music Downloader

Un descargador de música de YouTube/YouTube Music con Python que obtiene la mejor calidad de audio, portadas en alta resolución y metadatos completos optimizados.

## ✨ Características principales

- 🎵 **Descarga canciones individuales y playlists completas**
- 🎨 **Portadas en alta resolución** (hasta 1920x1080, optimizadas a 1000x1000)
- 📝 **Metadatos inteligentes** con nombres de artistas en romaji/latín
- 🎭 **Limpieza automática** de nombres (remueve "Official Channel", "VEVO", etc.)
- 🖼️ **Procesamiento de imágenes** (recorte automático, mejora de calidad)
- 🔍 **Búsqueda integrada** por texto
- 📦 **Múltiples formatos** (MP3, M4A, FLAC)
- ⚡ **Runtime JavaScript con Deno** para extracciones más rápidas
- 🎯 **Interfaz interactiva** fácil de usar

## 🆕 Mejoras recientes

### Portadas de alta calidad
- Selección automática de thumbnails en máxima resolución (maxresdefault)
- Procesamiento inteligente de imágenes (recorte, mejora, redimensionado)
- Conversión a formato cuadrado optimizado para reproductores de música
- Incrustación directa en archivos de audio

### Metadatos mejorados
- Extracción inteligente de artistas con prioridad para nombres en romaji/latín
- Limpieza automática de sufijos de canales ("Official YouTube Channel", etc.)
- Búsqueda en múltiples fuentes (metadata, descripción, título)
- Nombres de archivo limpios y organizados: `Artista - Título.m4a`
- Detección automática de año de lanzamiento

### Rendimiento
- Integración con Deno como runtime de JavaScript
- Reducción de advertencias y errores de extracción
- Mejor compatibilidad con YouTube Music

## 📦 Instalación

### Instalación automática (recomendada)
```bash
chmod +x install.sh
./install.sh
```

El script automáticamente:
- Crea un entorno virtual Python
- Instala todas las dependencias necesarias
- Verifica que ffmpeg esté instalado
- Instala Deno como runtime de JavaScript (opcional pero recomendado)

### Instalación manual
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# o en Windows: venv\Scripts\activate

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar ffmpeg (Ubuntu/Debian)
sudo apt install ffmpeg

# Instalar ffmpeg (macOS con Homebrew)
brew install ffmpeg

# Instalar Deno (opcional pero recomendado)
curl -fsSL https://deno.land/install.sh | sh
```

> **Nota:** Se recomienda usar entorno virtual para evitar conflictos con paquetes del sistema.

## 🎵 Uso

### Modo interactivo (recomendado)
```bash
# Activar el entorno virtual (si no está activo)
source venv/bin/activate

# Ejecutar el programa
python3 youtube_music_downloader.py
```

El menú interactivo ofrece:
1. **Descargar canción individual** - Pega una URL de YouTube/YouTube Music
2. **Descargar playlist** - Descarga todas las canciones de una playlist
3. **Buscar y descargar** - Busca por nombre de canción o artista
4. **Cambiar carpeta de descarga** - Personaliza la ubicación
5. **Salir**

### Uso desde código Python
```python
from youtube_music_downloader import YouTubeMusicDownloader

# Crear descargador
downloader = YouTubeMusicDownloader("./mis_descargas")

# Descargar canción individual en mejor calidad
downloader.download_single("https://music.youtube.com/watch?v=...", "best")

# Descargar en MP3 320kbps
downloader.download_single("https://music.youtube.com/watch?v=...", "mp3")

# Descargar playlist completa
downloader.download_playlist("https://music.youtube.com/playlist?list=...", "best")

# Buscar y descargar (primera coincidencia)
downloader.search_and_download("Bohemian Rhapsody Queen", "flac", max_results=1)
```

## 🎼 Formatos disponibles

| Formato | Calidad | Compatibilidad | Metadatos | Recomendado para |
|---------|---------|----------------|-----------|------------------|
| **`best`** | Máxima disponible | Alta | ✅ Completos | Uso general (recomendado) |
| **`mp3`** | 320kbps | Universal | ✅ Completos | Máxima compatibilidad |
| **`m4a`** | Variable (alta) | Apple/Moderna | ✅ Completos | Dispositivos Apple |
| **`flac`** | Sin pérdida | Audiófilo | ⚠️ Limitados | Audiófilos |

> **Recomendación:** Usa `best` para obtener el mejor balance entre calidad y tamaño, con conversión automática a M4A.

## 📁 Estructura de archivos

Los archivos descargados se guardan con nombres limpios y organizados:

```
downloads/
├── Maon Kurosaki - Magic∞world (Instrumental).m4a
├── Queen - Bohemian Rhapsody.m4a
└── Led Zeppelin - Stairway to Heaven.mp3
```

### Contenido del archivo
- **Audio:** Mejor calidad disponible del formato seleccionado
- **Portada:** Thumbnail de alta resolución (1000x1000) incrustada
- **Metadatos:**
  - Título de la canción
  - Artista (en romaji/latín cuando está disponible)
  - Álbum
  - Año de lanzamiento
  - Género
  - Duración

## 💡 URLs compatibles

- **YouTube Music:** `https://music.youtube.com/watch?v=...`
- **YouTube:** `https://www.youtube.com/watch?v=...`
- **Playlists:** `https://music.youtube.com/playlist?list=...`
- **Albums:** `https://music.youtube.com/browse/MPREb_...`
- **URLs cortas:** `https://youtu.be/...`

## 🔧 Solución de problemas

### Advertencias de JavaScript runtime
Si ves advertencias sobre "No supported JavaScript runtime":
```bash
# Instalar Deno (recomendado)
curl -fsSL https://deno.land/install.sh | sh

# Agregar Deno al PATH (el instalador lo hace automáticamente)
# Reiniciar el terminal para que tome efecto
```

El script automáticamente detectará y usará Deno si está instalado.

### Portadas borrosas o de baja calidad
El script ahora busca automáticamente thumbnails en máxima resolución (1920x1080). Si las portadas siguen siendo de baja calidad:
- Verifica que el video tenga thumbnails de alta resolución disponibles
- El script mostrará todos los thumbnails disponibles durante la descarga

### Nombres de artistas en japonés/chino
El script prioriza automáticamente nombres en romaji/latín cuando están disponibles en los metadatos. Si no funciona:
- Algunos videos solo tienen nombres en caracteres originales
- Puedes renombrar manualmente después de la descarga

### Error: "Sign in to confirm you're not a bot" o "Signature extraction failed"
```bash
# Activar entorno virtual
source venv/bin/activate

# Actualizar yt-dlp a la última versión
pip install --upgrade yt-dlp
```

### Error: "yt-dlp not found"
```bash
# Asegúrate de tener el entorno virtual activado
source venv/bin/activate
pip install --upgrade yt-dlp
```

### Error: "ffmpeg not found"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### Error: "No module named 'mutagen'" o "No module named 'PIL'"
```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar todas las dependencias
pip install -r requirements.txt
```

### Error de permisos
```bash
chmod +x youtube_music_downloader.py
chmod +x install.sh
```

### Archivos descargados sin metadatos
Asegúrate de que el formato sea compatible:
- ✅ M4A y MP3: Soporte completo de metadatos
- ⚠️ FLAC: Soporte limitado de portadas

## 🎨 Características técnicas

### Procesamiento de imágenes
- **Selección inteligente:** Busca thumbnails en orden de calidad (maxresdefault → hq720 → sddefault)
- **Recorte automático:** Elimina barras negras y elementos no deseados
- **Mejora de calidad:** Aplicación de filtros de nitidez, contraste y saturación
- **Optimización:** Conversión a formato cuadrado y redimensionado a 1000x1000
- **Compresión inteligente:** JPEG de alta calidad (95%) con tamaño optimizado

### Extracción de metadatos
1. **Prioridad de fuentes:**
   - Campo `artist` o `creator` (más confiable)
   - Extracción del título (formato "Artista - Título")
   - Búsqueda en descripción del video
   - Uploader/Canal (como último recurso)

2. **Limpieza automática:**
   - Remueve "Official YouTube Channel"
   - Remueve "VEVO", "Official", "Topic"
   - Detecta y prioriza nombres en caracteres latinos

3. **Detección de idioma:**
   - Identifica caracteres japoneses (Hiragana, Katakana, Kanji)
   - Identifica caracteres chinos (CJK)
   - Identifica caracteres coreanos (Hangul)
   - Busca alternativas en romaji cuando están disponibles

### Runtime JavaScript
El script está optimizado para usar Deno como runtime de JavaScript:
- Mejora la extracción de información de YouTube
- Reduce advertencias y errores
- Acceso a más formatos de audio
- Mejor compatibilidad a largo plazo

## 📊 Calidad de audio por formato

| Formato | Bitrate típico | Codec | Tamaño promedio (4 min) |
|---------|----------------|-------|-------------------------|
| **M4A** | 128-256 kbps | AAC | 4-8 MB |
| **MP3** | 320 kbps | MP3 | ~10 MB |
| **FLAC** | ~1000 kbps | FLAC | ~30 MB |

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⚖️ Consideraciones legales

- Solo descarga música que tengas derecho a descargar
- Respeta los derechos de autor
- Uso personal únicamente
- No redistribuyas contenido con copyright

## 🛠️ Dependencias

### Python (instaladas automáticamente)
- **yt-dlp** - Descargador de YouTube/YouTube Music
- **mutagen** - Edición de metadatos de audio
- **Pillow** - Procesamiento de imágenes
- **requests** - Descarga de thumbnails

### Sistema
- **Python 3.6+** - Lenguaje de programación
- **ffmpeg** - Conversión y procesamiento de audio/video
- **deno** - Runtime de JavaScript (opcional pero recomendado)

## 📝 Changelog

### v2.0 (Diciembre 2025)
- ✨ Portadas en alta resolución (hasta 1920x1080)
- 🎨 Procesamiento avanzado de imágenes
- 📝 Extracción inteligente de metadatos
- 🌐 Prioridad para nombres en romaji/latín
- 🧹 Limpieza automática de nombres de canales
- ⚡ Integración con Deno runtime
- 📁 Nombres de archivo optimizados

### v1.0 (Inicial)
- 🎵 Descarga de canciones individuales
- 📋 Descarga de playlists
- 🔍 Búsqueda integrada
- 🎼 Múltiples formatos de audio
- 📝 Metadatos básicos

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

**Hecho con ❤️ para los amantes de la música**