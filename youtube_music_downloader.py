#!/usr/bin/env python3
"""
YouTube Music Downloader
Descarga canciones de YouTube Music con la mejor calidad y metadatos completos
"""

import os
import yt_dlp
import subprocess
import sys
from pathlib import Path
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC
from mutagen.flac import FLAC
import requests
from PIL import Image
import io

class YouTubeMusicDownloader:
    def __init__(self, download_path="./downloads"):
        """
        Inicializa el descargador
        
        Args:
            download_path (str): Ruta donde se guardarán las descargas
        """
        self.download_path = Path(download_path)
        self.download_path.mkdir(exist_ok=True)
        
    def check_dependencies(self):
        """Verifica que yt-dlp y ffmpeg estén instalados"""
        try:
            subprocess.run(['yt-dlp', '--version'], 
                         capture_output=True, check=True)
            print("✓ yt-dlp está instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ yt-dlp no está instalado")
            print("Instala con: pip install yt-dlp")
            return False
            
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            print("✓ ffmpeg está instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ ffmpeg no está instalado")
            print("Instala con: sudo apt install ffmpeg (Ubuntu/Debian)")
            return False
            
        return True
    
    def clean_thumbnail_image(self, image_data):
        """
        Limpia y mejora la imagen del thumbnail con máxima calidad
        
        Args:
            image_data (bytes): Datos de la imagen
        Returns:
            bytes: Imagen limpia y mejorada
        """
        try:
            # Cargar imagen con Pillow
            img = Image.open(io.BytesIO(image_data))
            original_size = img.size
            print(f"� Imagen original: {original_size[0]}x{original_size[1]}")
            
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Recortar barras negras automáticamente
            img = self.auto_crop_black_bars(img)
            
            # Mejorar nitidez y contraste
            img = self.enhance_image_quality(img)
            
            # Redimensionar a un tamaño cuadrado si es muy rectangular
            width, height = img.size
            if abs(width - height) > min(width, height) * 0.1:  # Si no es casi cuadrado
                # Crear imagen cuadrada tomando el lado más pequeño
                size = min(width, height)
                # Recortar desde el centro
                left = (width - size) // 2
                top = (height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                print(f"🔲 Convertido a cuadrado: {size}x{size}")
            
            # Redimensionar a alta resolución para portadas
            target_size = 1000  # 1000x1000 para máxima calidad
            if img.size[0] != target_size:
                # Usar LANCZOS para mejor calidad en redimensionamiento
                img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                print(f"📏 Redimensionado a: {target_size}x{target_size}")
            
            # Convertir de vuelta a bytes con máxima calidad
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95, optimize=True, progressive=True)
            final_size = len(output.getvalue())
            print(f"💾 Tamaño final: {final_size // 1024}KB")
            return output.getvalue()
            
        except Exception as e:
            print(f"⚠️ Error procesando imagen: {e}")
            return image_data  # Devolver imagen original si falla
    
    def enhance_image_quality(self, img):
        """
        Mejora la calidad de la imagen aplicando filtros
        
        Args:
            img (PIL.Image): Imagen a mejorar
        Returns:
            PIL.Image: Imagen mejorada
        """
        try:
            from PIL import ImageEnhance, ImageFilter
            
            # Aplicar un ligero enfoque para mejorar nitidez
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
            
            # Mejorar contraste ligeramente
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # Mejorar saturación ligeramente
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.05)
            
            print("✨ Calidad de imagen mejorada")
            
        except Exception as e:
            print(f"⚠️ Error mejorando calidad: {e}")
        
        return img
    
    def auto_crop_black_bars(self, img):
        """
        Recorta automáticamente las barras negras de una imagen
        
        Args:
            img (PIL.Image): Imagen a procesar
        Returns:
            PIL.Image: Imagen recortada
        """
        try:
            # Convertir a escala de grises para detectar áreas oscuras
            gray = img.convert('L')
            
            # Usar numpy si está disponible para detección más precisa
            try:
                import numpy as np
                arr = np.array(gray)
                
                # Detectar filas y columnas que no son principalmente negras
                threshold = 25  # Umbral para considerar "negro"
                
                # Encontrar filas con contenido significativo
                row_means = np.mean(arr, axis=1)
                content_rows = np.where(row_means > threshold)[0]
                
                # Encontrar columnas con contenido significativo
                col_means = np.mean(arr, axis=0)
                content_cols = np.where(col_means > threshold)[0]
                
                if len(content_rows) > 0 and len(content_cols) > 0:
                    top = content_rows[0]
                    bottom = content_rows[-1]
                    left = content_cols[0]
                    right = content_cols[-1]
                    
                    # Solo recortar si las barras son significativas (>5% de la imagen)
                    height, width = arr.shape
                    if (top > height * 0.05 or bottom < height * 0.95 or 
                        left > width * 0.05 or right < width * 0.95):
                        img = img.crop((left, top, right + 1, bottom + 1))
                        print("🔲 Barras negras removidas")
                
            except ImportError:
                # Fallback sin numpy: detección simple
                bbox = img.getbbox()
                if bbox:
                    img = img.crop(bbox)
                    print("🔲 Imagen recortada automáticamente")
                    
        except Exception as e:
            print(f"⚠️ Error removiendo barras: {e}")
        
        return img

    def enhance_image_quality(self, img):
        """
        Mejora la calidad visual de la imagen
        
        Args:
            img (PIL.Image): Imagen a mejorar
        Returns:
            PIL.Image: Imagen mejorada
        """
        try:
            from PIL import ImageEnhance, ImageFilter
            
            # Aplicar filtro de nitidez suave
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
            
            # Mejorar contraste ligeramente
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # Mejorar color/saturación ligeramente
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.05)
            
            # Mejorar brillo si está muy oscuro
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.02)
            
            print("✨ Calidad de imagen mejorada")
            return img
            
        except Exception as e:
            print(f"⚠️ Error mejorando calidad: {e}")
            return img
    
    def smart_crop_image(self, img):
        """
        Recorta inteligentemente la imagen removiendo bordes y elementos no deseados
        
        Args:
            img (PIL.Image): Imagen a procesar
        Returns:
            PIL.Image: Imagen recortada
        """
        try:
            import numpy as np
            
            # Convertir a array para análisis
            arr = np.array(img)
            height, width = arr.shape[:2]
            
            # Detectar bordes oscuros/negros
            gray = np.mean(arr, axis=2)  # Convertir a escala de grises
            
            # Detectar filas y columnas oscuras
            row_darkness = np.mean(gray, axis=1)
            col_darkness = np.mean(gray, axis=0)
            
            # Threshold para considerar "oscuro" (ajustable)
            dark_threshold = 50
            
            # Encontrar límites no oscuros
            bright_rows = np.where(row_darkness > dark_threshold)[0]
            bright_cols = np.where(col_darkness > dark_threshold)[0]
            
            if len(bright_rows) > 0 and len(bright_cols) > 0:
                top = bright_rows[0]
                bottom = bright_rows[-1]
                left = bright_cols[0] 
                right = bright_cols[-1]
                
                # Solo recortar si hay una diferencia significativa
                margin_threshold = min(width, height) * 0.1  # 10% del tamaño mínimo
                
                if (top > margin_threshold or (height - bottom) > margin_threshold or
                    left > margin_threshold or (width - right) > margin_threshold):
                    
                    # Agregar un pequeño margen para no cortar demasiado
                    margin = 5
                    top = max(0, top - margin)
                    bottom = min(height - 1, bottom + margin)
                    left = max(0, left - margin)
                    right = min(width - 1, right + margin)
                    
                    img = img.crop((left, top, right + 1, bottom + 1))
                    print(f"✂️ Bordes oscuros removidos: {left},{top} a {right},{bottom}")
            
            # Detectar y remover logos/texto en las esquinas
            img = self.remove_corner_elements(img)
            
        except ImportError:
            print("⚠️ numpy no disponible, saltando procesamiento avanzado")
        except Exception as e:
            print(f"⚠️ Error en procesamiento inteligente: {e}")
        
        return img
    
    def remove_corner_elements(self, img):
        """
        Intenta remover elementos como logos o texto en las esquinas
        
        Args:
            img (PIL.Image): Imagen a procesar
        Returns:
            PIL.Image: Imagen procesada
        """
        try:
            import numpy as np
            
            arr = np.array(img)
            height, width = arr.shape[:2]
            
            # Analizar las esquinas (20% de cada lado)
            corner_size = min(width, height) // 5
            
            corners = {
                'top_left': arr[:corner_size, :corner_size],
                'top_right': arr[:corner_size, -corner_size:],
                'bottom_left': arr[-corner_size:, :corner_size],
                'bottom_right': arr[-corner_size:, -corner_size:]
            }
            
            # Detectar esquinas que tienen elementos (alta variación de color)
            for corner_name, corner_data in corners.items():
                std_dev = np.std(corner_data)
                if std_dev > 30:  # Threshold para detectar elementos
                    print(f"🎯 Elemento detectado en {corner_name}")
            
            # Por simplicidad, aplicar un crop conservador si detectamos elementos
            crop_margin = corner_size // 2
            img = img.crop((crop_margin, crop_margin, 
                           width - crop_margin, height - crop_margin))
            print(f"✂️ Márgenes de esquinas removidos: {crop_margin}px")
            
        except Exception as e:
            print(f"⚠️ Error removiendo elementos de esquinas: {e}")
        
        return img

    def write_metadata_to_file(self, file_path, metadata, thumbnail_url=None):
        """
        Escribe metadatos al archivo de audio usando mutagen
        
        Args:
            file_path (str): Ruta del archivo de audio
            metadata (dict): Diccionario con metadatos
            thumbnail_url (str): URL del thumbnail para incrustar
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.m4a':
                self._write_m4a_metadata(file_path, metadata, thumbnail_url)
            elif file_ext == '.mp3':
                self._write_mp3_metadata(file_path, metadata, thumbnail_url)
            elif file_ext == '.flac':
                self._write_flac_metadata(file_path, metadata, thumbnail_url)
            
            print("✅ Metadatos escritos correctamente")
            
        except Exception as e:
            print(f"⚠️ Error escribiendo metadatos: {e}")
    
    def _write_m4a_metadata(self, file_path, metadata, thumbnail_url):
        """Escribe metadatos para archivos M4A"""
        audio = MP4(file_path)
        
        if metadata.get('title'):
            audio['\xa9nam'] = metadata['title']
        if metadata.get('artist'):
            audio['\xa9ART'] = metadata['artist']
        if metadata.get('album'):
            audio['\xa9alb'] = metadata['album']
        if metadata.get('date'):
            audio['\xa9day'] = metadata['date']
        if metadata.get('genre'):
            audio['\xa9gen'] = metadata['genre']
            
        # Incrustar thumbnail con mejor manejo
        if thumbnail_url:
            try:
                print("🖼️ Descargando portada...")
                response = requests.get(thumbnail_url, timeout=15)
                if response.status_code == 200:
                    image_data = response.content
                    
                    # Limpiar imagen automáticamente
                    clean_image_data = self.clean_thumbnail_image(image_data)
                    
                    # Detectar formato de imagen
                    if clean_image_data.startswith(b'\xff\xd8'):  # JPEG
                        cover_format = MP4Cover.FORMAT_JPEG
                    elif clean_image_data.startswith(b'\x89PNG'):  # PNG
                        cover_format = MP4Cover.FORMAT_PNG
                    else:
                        cover_format = MP4Cover.FORMAT_JPEG  # Por defecto
                    
                    audio['covr'] = [MP4Cover(clean_image_data, cover_format)]
                    print("✅ Portada incrustada (imagen optimizada)")
                else:
                    print(f"⚠️ No se pudo descargar la portada (HTTP {response.status_code})")
            except Exception as e:
                print(f"⚠️ Error descargando portada: {e}")
                
        audio.save()
    
    def _write_mp3_metadata(self, file_path, metadata, thumbnail_url):
        """Escribe metadatos para archivos MP3"""
        try:
            audio = MP3(file_path, ID3=ID3)
            audio.add_tags()
        except:
            audio = MP3(file_path)
            
        if metadata.get('title'):
            audio.tags.add(TIT2(encoding=3, text=metadata['title']))
        if metadata.get('artist'):
            audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
        if metadata.get('album'):
            audio.tags.add(TALB(encoding=3, text=metadata['album']))
        if metadata.get('date'):
            audio.tags.add(TDRC(encoding=3, text=metadata['date']))
        if metadata.get('genre'):
            audio.tags.add(TCON(encoding=3, text=metadata['genre']))
            
        # Incrustar thumbnail con mejor manejo
        if thumbnail_url:
            try:
                print("🖼️ Descargando portada...")
                response = requests.get(thumbnail_url, timeout=15)
                if response.status_code == 200:
                    image_data = response.content
                    
                    # Limpiar imagen automáticamente
                    clean_image_data = self.clean_thumbnail_image(image_data)
                    
                    # Detectar tipo MIME
                    if clean_image_data.startswith(b'\xff\xd8'):  # JPEG
                        mime_type = 'image/jpeg'
                    elif clean_image_data.startswith(b'\x89PNG'):  # PNG
                        mime_type = 'image/png'
                    else:
                        mime_type = 'image/jpeg'  # Por defecto
                    
                    audio.tags.add(APIC(
                        encoding=3,
                        mime=mime_type,
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=clean_image_data
                    ))
                    print("✅ Portada incrustada (imagen optimizada)")
                else:
                    print(f"⚠️ No se pudo descargar la portada (HTTP {response.status_code})")
            except Exception as e:
                print(f"⚠️ Error descargando portada: {e}")
                
        audio.save()
    
    def _write_flac_metadata(self, file_path, metadata, thumbnail_url):
        """Escribe metadatos para archivos FLAC"""
        audio = FLAC(file_path)
        
        if metadata.get('title'):
            audio['TITLE'] = metadata['title']
        if metadata.get('artist'):
            audio['ARTIST'] = metadata['artist']
        if metadata.get('album'):
            audio['ALBUM'] = metadata['album']
        if metadata.get('date'):
            audio['DATE'] = metadata['date']
        if metadata.get('genre'):
            audio['GENRE'] = metadata['genre']
            
        # Para FLAC, el thumbnail es más complejo, lo omitimos por ahora
        audio.save()

    def enhance_metadata(self, info_dict):
        """
        Mejora los metadatos extrayendo información adicional
        
        Args:
            info_dict: Diccionario con información del video
        """
        metadata = {}
        
        # Título de la canción
        title = info_dict.get('title', '')
        metadata['title'] = title
        
        # Artista - Prioridad de fuentes
        artist = None
        
        # 1. Intentar obtener del campo 'artist' o 'creator' (más confiable y suele estar en romaji)
        artist = info_dict.get('artist') or info_dict.get('creator')
        
        # 2. Si el artista tiene caracteres no latinos, buscar alternativa en 'alt_title' o 'track'
        if artist and self.has_non_latin_chars(artist):
            # Buscar en campos alternativos
            alt_artist = info_dict.get('track') or info_dict.get('alt_title')
            if alt_artist and ' - ' in alt_artist:
                potential = alt_artist.split(' - ')[0].strip()
                if not self.has_non_latin_chars(potential):
                    artist = potential
        
        # 3. Si no hay, buscar en el título (formato: "Artista - Título")
        if not artist and ' - ' in title:
            parts = title.split(' - ', 1)
            if len(parts) == 2:
                potential_artist = parts[0].strip()
                # Verificar que no sea solo el título de la canción
                if len(potential_artist) < 50:
                    artist = potential_artist
        
        # 4. Buscar en la descripción
        if not artist or self.has_non_latin_chars(artist):
            description = info_dict.get('description', '')
            # Buscar patrones comunes
            for pattern in ['Artist:', 'Artista:', 'By:', 'Por:']:
                if pattern in description:
                    lines = [line for line in description.split('\n') if pattern in line]
                    if lines:
                        potential = lines[0].split(pattern)[1].strip().split('\n')[0].split('•')[0].strip()
                        if not self.has_non_latin_chars(potential):
                            artist = potential
                            break
        
        # 5. Usar uploader/channel como último recurso y limpiar
        if not artist:
            artist = info_dict.get('uploader', '') or info_dict.get('channel', '')
        
        # Limpiar el nombre del artista
        artist = self.clean_artist_name(artist)
        metadata['artist'] = artist
        
        # Álbum
        album = info_dict.get('album')
        if not album:
            # Buscar en la descripción
            description = info_dict.get('description', '')
            for pattern in ['Album:', 'Álbum:']:
                if pattern in description:
                    lines = [line for line in description.split('\n') if pattern in line]
                    if lines:
                        album = lines[0].split(pattern)[1].strip().split('\n')[0].split('•')[0].strip()
                        break
            
            # Si no se encontró, usar release_year si existe, sino el título
            if not album:
                album = info_dict.get('album') or title
        
        metadata['album'] = album
        
        # Fecha de lanzamiento - priorizar release_year
        release_year = info_dict.get('release_year')
        if release_year:
            metadata['date'] = str(release_year)
        else:
            upload_date = info_dict.get('upload_date')
            if upload_date:
                year = upload_date[:4]
                metadata['date'] = year
        
        # Duración
        duration = info_dict.get('duration')
        if duration:
            metadata['duration'] = str(duration)
            
        # Género (intentar extraer de categorías o tags)
        genre = 'Music'  # Por defecto
        categories = info_dict.get('categories', [])
        if categories:
            genre = categories[0] if 'Music' in categories else genre
        metadata['genre'] = genre
        
        return metadata
    
    def has_non_latin_chars(self, text):
        """
        Verifica si el texto contiene caracteres no latinos (japonés, chino, coreano, etc.)
        
        Args:
            text (str): Texto a verificar
        Returns:
            bool: True si contiene caracteres no latinos
        """
        if not text:
            return False
        
        for char in text:
            # Rangos Unicode para japonés, chino, coreano
            code = ord(char)
            if (0x3040 <= code <= 0x309F or  # Hiragana
                0x30A0 <= code <= 0x30FF or  # Katakana
                0x4E00 <= code <= 0x9FFF or  # Kanji/Hanzi (CJK)
                0xAC00 <= code <= 0xD7AF):   # Hangul (coreano)
                return True
        
        return False
    
    def clean_artist_name(self, artist):
        """
        Limpia el nombre del artista removiendo sufijos comunes de canales
        
        Args:
            artist (str): Nombre del artista sin limpiar
        Returns:
            str: Nombre limpio del artista
        """
        if not artist:
            return 'Unknown Artist'
        
        # Patrones a remover
        patterns_to_remove = [
            ' - Topic',
            ' Topic',
            'VEVO',
            ' Official',
            ' Official Channel',
            ' Official YouTube Channel',
            ' Official Music Video',
            ' Official Video',
            ' Official Audio',
            ' (Official)',
            'Official ',
        ]
        
        cleaned = artist
        for pattern in patterns_to_remove:
            cleaned = cleaned.replace(pattern, '')
        
        return cleaned.strip()
    
    def generate_clean_filename(self, metadata, original_path):
        """
        Genera un nombre de archivo limpio usando los metadatos mejorados
        
        Args:
            metadata (dict): Metadatos mejorados
            original_path (str): Ruta del archivo original
        Returns:
            str: Nueva ruta con nombre limpio
        """
        artist = metadata.get('artist', 'Unknown Artist')
        title = metadata.get('title', 'Unknown Title')
        
        # Limpiar caracteres no válidos para nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            artist = artist.replace(char, '')
            title = title.replace(char, '')
        
        # Obtener directorio y extensión del archivo original
        original_path = Path(original_path)
        directory = original_path.parent
        extension = original_path.suffix
        
        # Generar nuevo nombre
        new_name = f"{artist} - {title}{extension}"
        new_path = directory / new_name
        
        return str(new_path)

    def get_ydl_opts(self, format_type="best", single_video=False):
        """
        Configura las opciones de yt-dlp
        
        Args:
            format_type (str): "best", "mp3", "m4a", "flac"
            single_video (bool): Si True, evita descargar playlists completas
        """
        # Detectar ruta de deno si está instalado
        deno_path = os.path.expanduser("~/.deno/bin/deno")
        
        base_opts = {
            'outtmpl': str(self.download_path / '%(uploader)s - %(title)s.%(ext)s'),
            'extractaudio': True,
            'writeinfojson': False,  # No necesitamos JSON
            'writethumbnail': False,  # Manejaremos thumbnails manualmente
            'embedthumbnail': False,  # Lo haremos manualmente
            'addmetadata': False,     # Lo haremos manualmente con mutagen
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'noplaylist': single_video,  # Evita descargar playlists en canciones individuales
        }
        
        # Agregar deno como runtime de JavaScript si está disponible
        if os.path.exists(deno_path):
            base_opts['extractor_args'] = {'youtube': {'player_client': ['android'], 'js_runtime': [deno_path]}}
        
        # Configuración específica por formato
        if format_type == "best":
            # Para "best", preferir M4A que tiene mejor soporte de metadatos
            base_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '0',  # Mejor calidad
                }],
            })
        elif format_type == "mp3":
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',  # Mejor calidad MP3 (320kbps)
                }],
            })
        elif format_type == "m4a":
            base_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '0',
                }],
            })
        elif format_type == "flac":
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac',
                }],
            })
            
        return base_opts
    
    def download_single(self, url, format_type="best"):
        """
        Descarga una sola canción
        
        Args:
            url (str): URL de YouTube/YouTube Music
            format_type (str): Formato de audio deseado
        """
        ydl_opts = self.get_ydl_opts(format_type, single_video=True)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"📥 Descargando: {url}")
                print(f"🎵 Formato: {format_type}")
                
                # Obtener información del video
                info = ydl.extract_info(url, download=False)
                
                # Mejorar metadatos
                enhanced_metadata = self.enhance_metadata(info)
                
                print(f"🎤 Artista: {enhanced_metadata.get('artist', 'Desconocido')}")
                print(f"🎶 Título: {enhanced_metadata.get('title', 'Desconocido')}")
                print(f"💿 Álbum: {enhanced_metadata.get('album', 'Desconocido')}")
                print(f"📅 Año: {enhanced_metadata.get('date', 'Desconocido')}")
                print(f"⏱️  Duración: {enhanced_metadata.get('duration', '0')} segundos")
                
                # Descargar
                ydl.download([url])
                
                # Encontrar el archivo descargado
                expected_filename = ydl.prepare_filename(info)
                # Cambiar extensión según el formato
                if format_type == "mp3":
                    expected_filename = expected_filename.rsplit('.', 1)[0] + '.mp3'
                elif format_type == "m4a" or format_type == "best":
                    expected_filename = expected_filename.rsplit('.', 1)[0] + '.m4a'
                elif format_type == "flac":
                    expected_filename = expected_filename.rsplit('.', 1)[0] + '.flac'
                
                # Obtener la mejor URL de thumbnail
                thumbnail_url = self.get_best_thumbnail_url(info)
                
                # Escribir metadatos con mutagen
                if os.path.exists(expected_filename):
                    self.write_metadata_to_file(expected_filename, enhanced_metadata, thumbnail_url)
                    
                    # Renombrar archivo con el artista limpio
                    new_filename = self.generate_clean_filename(enhanced_metadata, expected_filename)
                    if new_filename != expected_filename and not os.path.exists(new_filename):
                        try:
                            os.rename(expected_filename, new_filename)
                            print(f"📝 Renombrado a: {Path(new_filename).name}")
                        except Exception as e:
                            print(f"⚠️ No se pudo renombrar: {e}")
                
                print("✅ Descarga completada!")
                
        except Exception as e:
            print(f"❌ Error al descargar: {e}")

    def get_best_thumbnail_url(self, info_dict):
        """
        Obtiene la mejor URL de thumbnail disponible, priorizando formatos limpios
        
        Args:
            info_dict: Información del video
        Returns:
            str: URL del thumbnail de mejor calidad
        """
        thumbnails = info_dict.get('thumbnails', [])
        if not thumbnails:
            return info_dict.get('thumbnail')
        
        # Debug: mostrar todos los thumbnails disponibles
        print("🔍 Thumbnails disponibles:")
        for i, thumb in enumerate(thumbnails):
            thumb_id = thumb.get('id', f'thumb_{i}')
            width = thumb.get('width', 'unknown')
            height = thumb.get('height', 'unknown')
            url = thumb.get('url', '')
            print(f"  {i+1}. {thumb_id} ({width}x{height}) {url[:50]}...")
        
        # Priorizar thumbnails por resolución (de mayor a menor)
        # Primero intentar obtener la mejor calidad disponible
        preferred_patterns = [
            'maxresdefault',  # 1920x1080 - Máxima calidad
            'maxres',         # Alternativa para maxresdefault
            'hq720',          # 1280x720 - Alta calidad
            'sddefault',      # 640x480 - Calidad estándar
            'hqdefault',      # 480x360 - Calidad media-alta
            'mqdefault',      # 320x180 - Calidad media
            'default',        # 120x90 - Baja calidad (último recurso)
        ]
        
        # 1. Buscar el thumbnail de mayor resolución disponible
        for pattern in preferred_patterns:
            for thumb in thumbnails:
                thumb_id = thumb.get('id', '').lower()
                thumb_url = thumb.get('url', '').lower()
                
                # Buscar tanto en el ID como en la URL
                if pattern in thumb_id or pattern in thumb_url:
                    width = thumb.get('width', 'unknown')
                    height = thumb.get('height', 'unknown')
                    print(f"✅ Seleccionado thumbnail de alta resolución: {pattern} ({width}x{height})")
                    return thumb.get('url')
        
        # 2. Si no encontramos por patrón, buscar el de mayor resolución por tamaño
        thumbnails_with_size = [t for t in thumbnails if t.get('width', 0) > 0 and t.get('height', 0) > 0]
        if thumbnails_with_size:
            # Ordenar por área (width * height) de mayor a menor
            thumbnails_with_size.sort(key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
            best_thumb = thumbnails_with_size[0]
            width = best_thumb.get('width', 0)
            height = best_thumb.get('height', 0)
            thumb_id = best_thumb.get('id', 'best_size')
            print(f"✅ Seleccionado thumbnail por tamaño: {thumb_id} ({width}x{height})")
            return best_thumb.get('url')
        
        # 3. Último recurso: el primero disponible
        if thumbnails:
            fallback = thumbnails[0]
            thumb_id = fallback.get('id', 'fallback')
            print(f"⚠️ Usando thumbnail de respaldo: {thumb_id}")
            return fallback.get('url')
        
        # Fallback final
        return info_dict.get('thumbnail')
    
    def download_playlist(self, url, format_type="best"):
        """
        Descarga una playlist completa con metadatos y portadas individuales
        
        Args:
            url (str): URL de la playlist
            format_type (str): Formato de audio deseado
        """
        ydl_opts = self.get_ydl_opts(format_type, single_video=False)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"📋 Analizando playlist: {url}")
                print(f"🎵 Formato: {format_type}")
                
                # Obtener información de la playlist SIN descargar
                info = ydl.extract_info(url, download=False)
                
                if 'entries' not in info:
                    print("❌ No se pudo obtener información de la playlist")
                    return
                
                entries = [entry for entry in info['entries'] if entry is not None]
                total_songs = len(entries)
                
                print(f"📝 Playlist: {info.get('title', 'Sin título')}")
                print(f"🔢 Total de canciones: {total_songs}")
                print(f"� Iniciando descarga con metadatos completos...\n")
                
                successful_downloads = 0
                failed_downloads = 0
                
                # Procesar cada canción individualmente
                for i, entry in enumerate(entries, 1):
                    try:
                        video_url = entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        
                        print(f"━━━ 📥 Canción {i}/{total_songs} ━━━")
                        
                        # Usar la misma lógica que download_single
                        self.download_single_from_playlist(video_url, format_type, i, total_songs)
                        
                        successful_downloads += 1
                        print(f"✅ Completada {i}/{total_songs}\n")
                        
                    except Exception as e:
                        failed_downloads += 1
                        print(f"❌ Error en canción {i}: {e}\n")
                        continue
                
                # Resumen final
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"🎉 Playlist completada!")
                print(f"✅ Exitosas: {successful_downloads}")
                if failed_downloads > 0:
                    print(f"❌ Fallidas: {failed_downloads}")
                print(f"📁 Archivos guardados en: {self.download_path}")
                
        except Exception as e:
            print(f"❌ Error al procesar playlist: {e}")

    def download_single_from_playlist(self, url, format_type, current, total):
        """
        Descarga una canción individual desde una playlist con metadatos completos
        
        Args:
            url (str): URL de la canción
            format_type (str): Formato de audio
            current (int): Número actual
            total (int): Total de canciones
        """
        ydl_opts = self.get_ydl_opts(format_type, single_video=True)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obtener información del video
                info = ydl.extract_info(url, download=False)
                
                # Mejorar metadatos
                enhanced_metadata = self.enhance_metadata(info)
                
                print(f"🎤 Artista: {enhanced_metadata.get('artist', 'Desconocido')}")
                print(f"🎶 Título: {enhanced_metadata.get('title', 'Desconocido')}")
                print(f"💿 Álbum: {enhanced_metadata.get('album', 'Desconocido')}")
                print(f"⏱️  Duración: {enhanced_metadata.get('duration', '0')} segundos")
                
                # Descargar
                ydl.download([url])
                
                # Encontrar el archivo descargado
                expected_filename = ydl.prepare_filename(info)
                # Cambiar extensión según el formato
                if format_type == "mp3":
                    expected_filename = expected_filename.rsplit('.', 1)[0] + '.mp3'
                elif format_type == "m4a" or format_type == "best":
                    expected_filename = expected_filename.rsplit('.', 1)[0] + '.m4a'
                elif format_type == "flac":
                    expected_filename = expected_filename.rsplit('.', 1)[0] + '.flac'
                
                # Obtener la mejor URL de thumbnail
                thumbnail_url = self.get_best_thumbnail_url(info)
                
                # Escribir metadatos con mutagen
                if os.path.exists(expected_filename):
                    print(f"🔖 Procesando metadatos y portada...")
                    self.write_metadata_to_file(expected_filename, enhanced_metadata, thumbnail_url)
                
        except Exception as e:
            raise Exception(f"Error descargando {url}: {e}")

    def preview_playlist(self, url):
        """
        Muestra un preview de la playlist antes de descargar
        
        Args:
            url (str): URL de la playlist
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("🔍 Analizando playlist...")
                info = ydl.extract_info(url, download=False)
                
                if 'entries' not in info:
                    print("❌ No se pudo obtener información de la playlist")
                    return
                
                entries = [entry for entry in info['entries'] if entry is not None]
                total_songs = len(entries)
                
                print(f"\n📋 PREVIEW DE PLAYLIST")
                print("═" * 50)
                print(f"📝 Título: {info.get('title', 'Sin título')}")
                print(f"🔢 Total de canciones: {total_songs}")
                print(f"👤 Autor: {info.get('uploader', 'Desconocido')}")
                
                if total_songs > 10:
                    print(f"\n🎵 Primeras 10 canciones:")
                    entries_to_show = entries[:10]
                    show_more = True
                else:
                    print(f"\n🎵 Todas las canciones:")
                    entries_to_show = entries
                    show_more = False
                
                for i, entry in enumerate(entries_to_show, 1):
                    title = entry.get('title', 'Sin título')
                    duration = entry.get('duration', 0)
                    if duration:
                        duration_str = f" ({duration//60}:{duration%60:02d})"
                    else:
                        duration_str = ""
                    print(f"  {i:2d}. {title}{duration_str}")
                
                if show_more:
                    print(f"  ... y {total_songs - 10} canciones más")
                
                # Estimar tiempo y tamaño
                avg_duration = sum(e.get('duration', 240) for e in entries) / len(entries) if entries else 240
                total_duration = sum(e.get('duration', avg_duration) for e in entries)
                hours = total_duration // 3600
                minutes = (total_duration % 3600) // 60
                
                print(f"\n⏱️  Duración total estimada: {hours}h {minutes}m")
                print(f"💾 Tamaño estimado (M4A): ~{total_songs * 4:.1f} MB")
                print(f"💾 Tamaño estimado (MP3): ~{total_songs * 3.5:.1f} MB")
                print(f"💾 Tamaño estimado (FLAC): ~{total_songs * 25:.1f} MB")
                
        except Exception as e:
            print(f"❌ Error analizando playlist: {e}")

    def search_and_download(self, query, format_type="best", max_results=1):
        """
        Busca y descarga canciones por texto
        
        Args:
            query (str): Texto a buscar
            format_type (str): Formato de audio deseado
            max_results (int): Número máximo de resultados
        """
        search_url = f"ytsearch{max_results}:{query}"
        
        ydl_opts = self.get_ydl_opts(format_type, single_video=True)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"🔍 Buscando: {query}")
                print(f"🎵 Formato: {format_type}")
                
                ydl.download([search_url])
                print("✅ Búsqueda y descarga completada!")
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")

def main():
    """Función principal con menú interactivo"""
    downloader = YouTubeMusicDownloader()
    
    print("🎵 YouTube Music Downloader 🎵")
    print("=" * 40)
    
    # Verificar dependencias
    if not downloader.check_dependencies():
        return
    
    while True:
        print("\n📋 OPCIONES:")
        print("1. Descargar canción individual")
        print("2. Descargar playlist")
        print("3. Buscar y descargar por texto")
        print("4. Cambiar carpeta de descarga")
        print("5. Salir")
        
        choice = input("\n👉 Elige una opción (1-5): ").strip()
        
        if choice == "1":
            url = input("🔗 URL de la canción: ").strip()
            format_type = input("🎵 Formato (best/mp3/m4a/flac) [best]: ").strip() or "best"
            downloader.download_single(url, format_type)
            
        elif choice == "2":
            url = input("🔗 URL de la playlist: ").strip()
            format_type = input("🎵 Formato (best/mp3/m4a/flac) [best]: ").strip() or "best"
            
            # Preguntar si quiere preview para playlists grandes
            preview = input("📋 ¿Mostrar preview de la playlist antes de descargar? (s/N): ").strip().lower()
            if preview in ['s', 'sí', 'si', 'y', 'yes']:
                downloader.preview_playlist(url)
                confirm = input("\n🚀 ¿Continuar con la descarga? (S/n): ").strip().lower()
                if confirm in ['n', 'no']:
                    print("❌ Descarga cancelada")
                    continue
            
            downloader.download_playlist(url, format_type)
            
        elif choice == "3":
            query = input("🔍 Texto a buscar: ").strip()
            max_results = input("🔢 Número de resultados [1]: ").strip() or "1"
            format_type = input("🎵 Formato (best/mp3/m4a/flac) [best]: ").strip() or "best"
            try:
                max_results = int(max_results)
                downloader.search_and_download(query, format_type, max_results)
            except ValueError:
                print("❌ Número inválido")
                
        elif choice == "4":
            new_path = input(f"📁 Nueva carpeta [{downloader.download_path}]: ").strip()
            if new_path:
                downloader = YouTubeMusicDownloader(new_path)
                print(f"✅ Carpeta cambiada a: {downloader.download_path}")
                
        elif choice == "5":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()