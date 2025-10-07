#!/bin/bash

# Monitor Industrial SISPRO - Script de Instalacion
# Raspberry Pi - Estacion de Trabajo

set -e

echo "Instalando Monitor Industrial SISPRO..."
echo "========================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si es Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "Este script está optimizado para Raspberry Pi"
fi

# Verificar sistema operativo
if ! grep -q "Raspbian\|Raspberry Pi OS" /etc/os-release 2>/dev/null; then
    print_warning "Sistema operativo no reconocido. Continuando..."
fi

print_status "Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

print_status "Instalando dependencias del sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    redis-server \
    git \
    curl \
    wget \
    vim \
    htop

print_status "Configurando Redis..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Configurar contraseña de Redis
sudo sed -i 's/# requirepass foobared/requirepass Z67tyEr/' /etc/redis/redis.conf
sudo systemctl restart redis-server

# Verificar que Redis esté funcionando
if redis-cli -a Z67tyEr ping > /dev/null 2>&1; then
    print_success "Redis configurado correctamente con contraseña"
else
    print_error "Error configurando Redis"
    exit 1
fi

print_status "Configurando permisos de usuario..."
sudo usermod -a -G dialout $USER

print_status "Creando directorio del proyecto..."
PROJECT_DIR="$HOME/monitor_industrial"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

print_status "Creando entorno virtual de Python..."
python3 -m venv venv
source venv/bin/activate

print_status "Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

print_status "Creando directorio de logs..."
mkdir -p logs

print_status "Creando archivo de configuración inicial..."
cat > config.json << EOF
{
  "sispro": {
    "base_url": "http://localhost:3000",
    "username": "monitor_pi",
    "password": "password_segura",
    "empresa_id": 1,
    "usuario_id": 1
  },
  "rs485": {
    "port": "/dev/ttyUSB0",
    "baudrate": 9600,
    "timeout": 1
  },
  "cache": {
    "redis_host": "localhost",
    "redis_port": 6379,
    "redis_password": "Z67tyEr",
    "redis_db": 0,
    "sqlite_file": "monitor_cache.db"
  },
  "interfaz": {
    "fullscreen": true,
    "theme": "industrial",
    "update_interval": 1000
  },
  "sincronizacion": {
    "intervalo_minutos": 5,
    "max_reintentos": 3,
    "timeout_segundos": 30
  }
}
EOF

print_status "Creando script de inicio..."
cat > start_monitor.sh << 'EOF'
#!/bin/bash
cd "$HOME/monitor_industrial"
source venv/bin/activate
python main.py
EOF

chmod +x start_monitor.sh

print_status "Creando servicio systemd..."
sudo tee /etc/systemd/system/monitor-industrial.service > /dev/null << EOF
[Unit]
Description=Monitor Industrial SISPRO
After=network.target redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_status "Configurando servicio systemd..."
sudo systemctl daemon-reload
sudo systemctl enable monitor-industrial.service

print_status "Creando script de diagnostico..."
cat > diagnose.sh << 'EOF'
#!/bin/bash
echo "Diagnostico del Monitor Industrial SISPRO"
echo "=========================================="

echo "Estado del sistema:"
echo "  - Usuario: $(whoami)"
echo "  - Directorio: $(pwd)"
echo "  - Python: $(python3 --version)"
echo "  - Redis: $(redis-cli -a Z67tyEr ping 2>/dev/null || echo 'NO CONECTADO')"

echo ""
echo "Puertos RS485 disponibles:"
ls -la /dev/ttyUSB* 2>/dev/null || echo "  No se encontraron puertos USB"

echo ""
echo "Archivos del proyecto:"
ls -la

echo ""
echo "Estado de la base de datos:"
if [ -f "monitor_cache.db" ]; then
    echo "  - SQLite: $(sqlite3 monitor_cache.db 'SELECT COUNT(*) FROM lecturas_produccion;' 2>/dev/null || echo 'ERROR')"
else
    echo "  - SQLite: No existe"
fi

echo ""
echo "Estado del servicio:"
sudo systemctl status monitor-industrial.service --no-pager -l

echo ""
echo "Ultimos logs:"
tail -n 10 logs/monitor_$(date +%Y%m%d).log 2>/dev/null || echo "  No hay logs disponibles"
EOF

chmod +x diagnose.sh

print_status "Creando script de limpieza..."
cat > cleanup.sh << 'EOF'
#!/bin/bash
echo "Limpiando Monitor Industrial SISPRO"
echo "====================================="

echo "Deteniendo servicio..."
sudo systemctl stop monitor-industrial.service

echo "Limpiando cache Redis..."
redis-cli -a Z67tyEr FLUSHDB

echo "Limpiando logs antiguos..."
find logs -name "*.log" -mtime +7 -delete

echo "Limpiando base de datos SQLite..."
if [ -f "monitor_cache.db" ]; then
    sqlite3 monitor_cache.db "DELETE FROM lecturas_produccion WHERE sincronizada = TRUE AND timestamp < datetime('now', '-7 days');"
fi

echo "Limpieza completada"
EOF

chmod +x cleanup.sh

print_success "Instalacion completada"
echo ""
echo "Proximos pasos:"
echo "  1. Configurar config.json con la URL de tu SISPRO"
echo "  2. Conectar Raspberry Pi Pico con RS485"
echo "  3. Ejecutar: ./start_monitor.sh"
echo "  4. O iniciar servicio: sudo systemctl start monitor-industrial"
echo ""
echo "Comandos utiles:"
echo "  - Iniciar: ./start_monitor.sh"
echo "  - Diagnostico: ./diagnose.sh"
echo "  - Limpiar: ./cleanup.sh"
echo "  - Logs: tail -f logs/monitor_\$(date +%Y%m%d).log"
echo ""
echo "Documentacion: README.md"
echo ""
print_success "Monitor Industrial SISPRO instalado correctamente"
