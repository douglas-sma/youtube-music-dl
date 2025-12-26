#!/bin/bash

echo "🎵 Configurando YouTube Music Downloader 🎵"
echo "============================================"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias de Python
echo "📦 Instalando dependencias de Python..."
pip install -r requirements.txt

# Verificar ffmpeg
echo "🔧 Verificando ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg no está instalado"
    echo "Instalando ffmpeg..."
    
    # Detectar el sistema operativo
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y ffmpeg
        # CentOS/RHEL/Fedora
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y ffmpeg
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "Por favor instala Homebrew primero: https://brew.sh/"
        fi
    fi
else
    echo "✅ ffmpeg ya está instalado"
fi

# Hacer el script ejecutable
chmod +x youtube_music_downloader.py

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "🚀 Para usar el descargador:"
echo "   1. Activa el entorno virtual: source venv/bin/activate"
echo "   2. Ejecuta: python3 youtube_music_downloader.py"
echo "   3. Para desactivar el entorno: deactivate"
echo ""
echo "   python3 youtube_music_downloader.py"
echo ""
echo "💡 O hazlo ejecutable directamente:"
echo "   ./youtube_music_downloader.py"