# 🔐 Configuración Redis con Contraseña - Monitor Industrial SISPRO

## 📋 Configuración de Redis

El Monitor Industrial SISPRO ahora incluye soporte para Redis con contraseña de autenticación.

### 🔑 Credenciales Redis

```bash
REDIS_HOST = "localhost"
REDIS_PORT = "6379"
REDIS_PASSWORD = "Z67tyEr"
```

## 🚀 Instalación con Redis Seguro

### 1. Ejecutar script de instalación

```bash
# El script configurará automáticamente Redis con contraseña
./install.sh
```

### 2. Configuración manual (si es necesario)

```bash
# Configurar contraseña en Redis
sudo sed -i 's/# requirepass foobared/requirepass Z67tyEr/' /etc/redis/redis.conf

# Reiniciar Redis
sudo systemctl restart redis-server

# Verificar conexión con contraseña
redis-cli -a Z67tyEr ping
```

## ⚙️ Archivos de Configuración

### `config.json` (Producción)

```json
{
  "cache": {
    "redis_host": "localhost",
    "redis_port": 6379,
    "redis_password": "Z67tyEr",
    "redis_db": 0,
    "sqlite_file": "monitor_cache.db"
  }
}
```

### `config_redis.json` (Plantilla)

Archivo de plantilla con la configuración de Redis ya incluida.

## 🔧 Verificación de Conexión

### 1. Verificar Redis con contraseña

```bash
# Probar conexión
redis-cli -a Z67tyEr ping

# Debería responder: PONG
```

### 2. Verificar desde Python

```python
import redis

# Conectar con contraseña
r = redis.Redis(
    host='localhost',
    port=6379,
    password='Z67tyEr',
    db=0,
    decode_responses=True
)

# Probar conexión
print(r.ping())  # Debería imprimir: True
```

## 🛠️ Comandos de Diagnóstico

### 1. Estado de Redis

```bash
# Verificar estado del servicio
sudo systemctl status redis-server

# Ver logs de Redis
sudo journalctl -u redis-server -f
```

### 2. Limpiar cache

```bash
# Limpiar base de datos Redis
redis-cli -a Z67tyEr FLUSHDB

# Ver información de la base de datos
redis-cli -a Z67tyEr INFO
```

### 3. Monitoreo en tiempo real

```bash
# Monitorear comandos Redis
redis-cli -a Z67tyEr MONITOR

# Ver claves almacenadas
redis-cli -a Z67tyEr KEYS "*"
```

## 🔒 Seguridad

### 1. Cambiar contraseña

```bash
# Editar configuración de Redis
sudo nano /etc/redis/redis.conf

# Cambiar la línea:
# requirepass Z67tyEr

# Reiniciar Redis
sudo systemctl restart redis-server
```

### 2. Configurar firewall (opcional)

```bash
# Permitir solo conexiones locales
sudo ufw allow from 127.0.0.1 to any port 6379
sudo ufw deny 6379
```

## 🐛 Solución de Problemas

### 1. Error de autenticación

```bash
# Verificar que Redis esté ejecutándose
sudo systemctl status redis-server

# Verificar configuración
sudo grep requirepass /etc/redis/redis.conf

# Reiniciar Redis
sudo systemctl restart redis-server
```

### 2. Error de conexión

```bash
# Verificar que el puerto esté abierto
sudo netstat -tlnp | grep 6379

# Verificar logs de Redis
sudo tail -f /var/log/redis/redis-server.log
```

### 3. Error de permisos

```bash
# Verificar permisos del archivo de configuración
sudo chown redis:redis /etc/redis/redis.conf
sudo chmod 640 /etc/redis/redis.conf
```

## 📊 Monitoreo del Cache

### 1. Estadísticas de Redis

```bash
# Ver estadísticas generales
redis-cli -a Z67tyEr INFO

# Ver estadísticas de memoria
redis-cli -a Z67tyEr INFO memory

# Ver estadísticas de claves
redis-cli -a Z67tyEr INFO keyspace
```

### 2. Ver datos del monitor

```bash
# Ver lecturas almacenadas
redis-cli -a Z67tyEr HGETALL "lectura:1"

# Ver estado de estaciones
redis-cli -a Z67tyEr HGETALL "estacion:1"

# Ver lecturas pendientes
redis-cli -a Z67tyEr LRANGE "lecturas_pendientes" 0 -1
```

## 🔄 Backup y Restauración

### 1. Backup de Redis

```bash
# Crear backup
redis-cli -a Z67tyEr BGSAVE

# El backup se guarda en: /var/lib/redis/dump.rdb
```

### 2. Restaurar desde backup

```bash
# Detener Redis
sudo systemctl stop redis-server

# Copiar archivo de backup
sudo cp /var/lib/redis/dump.rdb.backup /var/lib/redis/dump.rdb

# Iniciar Redis
sudo systemctl start redis-server
```

## 📈 Optimización

### 1. Configuración de memoria

```bash
# Editar configuración de Redis
sudo nano /etc/redis/redis.conf

# Configurar límite de memoria (ejemplo: 512MB)
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### 2. Persistencia

```bash
# Configurar persistencia (ya está habilitada por defecto)
save 900 1
save 300 10
save 60 10000
```

## 🎯 Próximos Pasos

1. **Ejecutar instalación** - `./install.sh`
2. **Verificar conexión** - `redis-cli -a Z67tyEr ping`
3. **Configurar SISPRO** - Actualizar `config.json` con URL real
4. **Probar monitor** - Ejecutar `python main.py`
5. **Monitorear logs** - `tail -f logs/monitor_*.log`

---

**¡Redis configurado con seguridad!** 🔐

El Monitor Industrial SISPRO ahora usa Redis con autenticación para mayor seguridad en producción.
