# 🍓 Monitor Industrial SISPRO - Raspberry Pi

## 📋 Descripción

Monitor industrial para estaciones de trabajo que se comunica con el sistema SISPRO (Next.js) y la Raspberry Pi Pico mediante RS485. Proporciona una interfaz industrial fullscreen para operadores de producción.

## 🏗️ Arquitectura

```
Raspberry Pi (Monitor Industrial)
├── Interfaz Industrial Fullscreen (tkinter)
├── Comunicación SISPRO (HTTP/APIs)
├── Comunicación RS485 (Pico)
├── Validación de Códigos de Barras
├── Cache Local (Redis + SQLite)
└── Gestión de Estados
```

## 🚀 Instalación

### 1. Instalar dependencias del sistema

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y herramientas
sudo apt install python3 python3-pip python3-venv redis-server -y

# Instalar dependencias de desarrollo
sudo apt install python3-dev build-essential -y
```

### 2. Configurar Redis

```bash
# Iniciar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar que Redis esté funcionando
redis-cli ping
```

### 3. Crear entorno virtual

```bash
# Crear directorio del proyecto
mkdir -p ~/monitor_industrial
cd ~/monitor_industrial

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Configurar permisos RS485

```bash
# Agregar usuario al grupo dialout para acceso serial
sudo usermod -a -G dialout $USER

# Reiniciar sesión o ejecutar
newgrp dialout
```

## ⚙️ Configuración

### 1. Archivo de configuración

Crear `config.json` en el directorio del proyecto:

```json
{
  "sispro": {
    "base_url": "http://tu-sispro.com",
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
```

### 2. Variables de entorno (opcional)

```bash
# Crear archivo .env
export SISPRO_BASE_URL="http://tu-sispro.com"
export SISPRO_USERNAME="monitor_pi"
export SISPRO_PASSWORD="password_segura"
export RS485_PORT="/dev/ttyUSB0"
```

## 🚀 Uso

### 1. Ejecutar el monitor

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar monitor
python main.py
```

### 2. Flujo de trabajo

1. **Inicialización**: El monitor se conecta a SISPRO y RS485
2. **Selección de Estación**: Elegir estación de trabajo
3. **Selección de Orden**: Elegir orden de fabricación asignada
4. **Validación UPC**: Escanear código de barras del producto
5. **Producción**: El Pico envía conteos en tiempo real
6. **Sincronización**: Datos se sincronizan con SISPRO cada 5 minutos

### 3. Controles de la interfaz

- **🏭 SELECCIONAR ESTACIÓN**: Elegir estación de trabajo
- **📦 SELECCIONAR ORDEN**: Elegir orden de fabricación
- **📱 VALIDAR UPC**: Escanear código de barras
- **✅ FINALIZAR ORDEN**: Terminar orden actual
- **🔄 SINCRONIZAR**: Sincronizar datos inmediatamente
- **🚪 SALIR**: Cerrar aplicación

### 4. Atajos de teclado

- **Escape**: Salir de la aplicación
- **F11**: Alternar modo fullscreen
- **Ctrl+Q**: Salir de la aplicación

## 🔧 Configuración Avanzada

### 1. Personalizar interfaz

Modificar colores y fuentes en `interfaz_industrial.py`:

```python
self.colores = {
    'fondo': '#1a1a1a',
    'panel': '#2d2d2d',
    'texto': '#ffffff',
    'accento': '#00ff00',
    # ... más colores
}
```

### 2. Configurar sincronización

Ajustar intervalo de sincronización en `config.json`:

```json
{
  "sincronizacion": {
    "intervalo_minutos": 5, // Cambiar intervalo
    "max_reintentos": 3,
    "timeout_segundos": 30
  }
}
```

### 3. Configurar logs

Los logs se guardan en `logs/monitor_YYYYMMDD.log`:

```bash
# Ver logs en tiempo real
tail -f logs/monitor_$(date +%Y%m%d).log

# Ver logs de error
grep "ERROR" logs/monitor_*.log
```

## 🛠️ Mantenimiento

### 1. Limpiar cache

```bash
# Limpiar Redis
redis-cli FLUSHDB

# Limpiar SQLite (eliminar lecturas antiguas)
python -c "
from cache_manager import CacheManager
from config import Config
cache = CacheManager(Config())
cache.limpiar_lecturas_antiguas(7)  # Eliminar lecturas de más de 7 días
"
```

### 2. Verificar estado del sistema

```bash
# Verificar Redis
redis-cli ping

# Verificar puerto RS485
ls -la /dev/ttyUSB*

# Verificar procesos
ps aux | grep python
```

### 3. Reiniciar servicios

```bash
# Reiniciar Redis
sudo systemctl restart redis-server

# Reiniciar monitor
pkill -f "python main.py"
python main.py &
```

## 🐛 Solución de Problemas

### 1. Error de conexión RS485

```bash
# Verificar permisos
ls -la /dev/ttyUSB0

# Verificar si el puerto está en uso
sudo lsof /dev/ttyUSB0

# Cambiar permisos si es necesario
sudo chmod 666 /dev/ttyUSB0
```

### 2. Error de conexión Redis

```bash
# Verificar estado de Redis
sudo systemctl status redis-server

# Reiniciar Redis
sudo systemctl restart redis-server

# Verificar logs
sudo journalctl -u redis-server
```

### 3. Error de conexión SISPRO

```bash
# Verificar conectividad de red
ping tu-sispro.com

# Verificar APIs
curl -H "empresa-id: 1" http://tu-sispro.com/api/estacionesTrabajo
```

### 4. Interfaz no responde

```bash
# Verificar si hay procesos colgados
ps aux | grep python

# Matar procesos colgados
pkill -f "python main.py"

# Reiniciar monitor
python main.py
```

## 📊 Monitoreo

### 1. Estadísticas del sistema

El monitor proporciona estadísticas en tiempo real:

- Estado del sistema
- Estado del Pico
- Tiempo de inactividad
- Última sincronización
- Contador de producción
- Progreso de la orden

### 2. Logs del sistema

```bash
# Ver logs en tiempo real
tail -f logs/monitor_$(date +%Y%m%d).log

# Buscar errores específicos
grep "ERROR" logs/monitor_*.log | tail -20

# Buscar actividad de producción
grep "PRODUCIENDO" logs/monitor_*.log | tail -10
```

### 3. Estado de la base de datos

```bash
# Ver estadísticas de SQLite
sqlite3 monitor_cache.db "SELECT COUNT(*) FROM lecturas_produccion;"

# Ver lecturas pendientes
sqlite3 monitor_cache.db "SELECT COUNT(*) FROM lecturas_produccion WHERE sincronizada = FALSE;"
```

## 🔒 Seguridad

### 1. Configuración segura

- Usar contraseñas seguras en `config.json`
- Restringir acceso a archivos de configuración
- Usar HTTPS para comunicación con SISPRO
- Mantener el sistema actualizado

### 2. Permisos de archivos

```bash
# Configurar permisos seguros
chmod 600 config.json
chmod 600 monitor_cache.db
chmod 755 main.py
```

## 📈 Rendimiento

### 1. Optimizaciones

- Usar SSD para mejor rendimiento de SQLite
- Configurar Redis con persistencia adecuada
- Ajustar intervalo de sincronización según necesidades
- Monitorear uso de memoria y CPU

### 2. Escalabilidad

- El sistema soporta múltiples estaciones
- Cache distribuido con Redis
- Sincronización eficiente con SISPRO
- Recuperación automática de errores

## 🤝 Soporte

Para soporte técnico o reportar problemas:

1. Revisar logs del sistema
2. Verificar configuración
3. Consultar documentación
4. Contactar al equipo de desarrollo

---

**Versión**: 1.0.0
**Última actualización**: Diciembre 2024
**Mantenido por**: Equipo de Desarrollo sisproone
