# Cursor Rules - Monitor Industrial Python (Raspberry Pi)

## 🍓 INFORMACIÓN DEL PROYECTO

**Nombre**: monitor-industrial-python
**Descripción**: Monitor industrial para Raspberry Pi que se comunica con SISPRO (Next.js) y Raspberry Pi Pico
**Tipo**: Aplicación Python standalone
**Lenguaje Principal**: Python 3.9+
**Hardware**: Raspberry Pi + Raspberry Pi Pico
**Comunicación**: RS485 (Pi ↔ Pico), HTTP/WebSocket (Pi ↔ SISPRO)

## 🏗️ ARQUITECTURA DEL SISTEMA

### Componentes Principales

```
Raspberry Pi (Python)
├── MonitorRS485 (comunicación con Pico)
├── SISPROConnector (comunicación con Next.js)
├── BarcodeValidator (validación UPC)
├── CacheManager (Redis + SQLite)
├── WebSocketServer (tiempo real)
└── EstadoManager (gestión de estados)

Raspberry Pi Pico
├── Sensor RS485
├── Envío de conteos
└── Recepción de comandos
```

## 🔌 COMUNICACIÓN CON SISPRO (Next.js)

### ✅ **TODAS LAS APIs YA EXISTEN** - No crear APIs adicionales

#### 0. **Conexión con SISPRO** ✅ (SIN AUTENTICACIÓN JWT)

```python
# Configuración de conexión (LOGIN LOCAL - Sin autenticación JWT)
SISPRO_CONFIG = {
    "base_url": "http://100.24.193.207:3000",  # IP alternativa: sisproone.net
    "empresa_id": 1  # Siempre usar empresa-id 1
}

# Verificar conectividad con SISPRO
async def verificar_conectividad():
    """Verificar que SISPRO esté disponible"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SISPRO_CONFIG['base_url']}/api/estacionesTrabajo",
                headers={'empresa-id': str(SISPRO_CONFIG["empresa_id"])},
                timeout=10
            ) as response:
                return response.status == 200
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
        return False

# Headers estándar para todas las APIs (SIN TOKEN)
def get_headers():
    return {
        'empresa-id': str(SISPRO_CONFIG["empresa_id"]),
        'Content-Type': 'application/json'
    }

# Ejemplo de uso
if await verificar_conectividad():
    print(f"✅ SISPRO conectado - Empresa ID: {SISPRO_CONFIG['empresa_id']}")
else:
    print(f"❌ Error de conectividad con SISPRO")
```

#### 1. **Obtener Estaciones de Trabajo** ✅

```python
# GET /api/estacionesTrabajo
# Headers: { "empresa-id": "1" }  # Siempre usar empresa-id 1
# Respuesta: {
#   "success": true,
#   "data": [
#     {
#       "id": 1,
#       "nombre": "Estación 001",
#       "descripcion": "Descripción",
#       "estado": "ASIGNADA",
#       "coordinadorSupervisor": "Juan",
#       "cuadrante": "Cuadrante A"
#     }
#   ]
# }
```

#### 2. **Obtener Órdenes Asignadas** ✅

```python
# GET /api/ordenesDeFabricacion/listarAsignadas?estacionTrabajoId=1
# Headers: { "empresa-id": "1" }  # Siempre usar empresa-id 1
# Respuesta: {
#   "success": true,
#   "data": [
#     {
#       "id": 1,
#       "ordenFabricacion": "OF-001",
#       "pt": "PT-001",
#       "cantidadFabricar": 1000,
#       "cantidadPendiente": 500,
#       "avance": 0.5,
#       "ptDescripcion": "Producto A",
#       "ptPresentacion": "Caja x 10",
#       "ptUPC": "1234567890",
#       "estacionNombre": "Estación 001",
#       "estacionCoordinador": "Juan",
#       "estacionCuadrante": "Cuadrante A",
#       "prioridad": "NORMAL",
#       "isClosed": false
#     }
#   ]
# }
```

#### 3. **Validar UPC** ✅

```python
# POST /api/lecturaUPC/registrar
# Headers: { "empresa-id": "1" }  # Siempre usar empresa-id 1
# Body: {
#   "ordenFabricacion": "OF-001",
#   "upc": "1234567890",
#   "estacionId": 1,
#   "usuarioId": 1
# }
# Respuesta: { "success": true, "message": "Lectura registrada correctamente" }
```

#### 4. **Sincronizar Lecturas del Pico** ✅

```python
# POST /api/lecturaUPC/registrar (usar para sincronizar lecturas del Pico)
# Headers: { "empresa-id": "1" }
# Body: {
#   "ordenFabricacion": "OF-001",
#   "upc": "RS485_BATCH",  # Identificador para lecturas del Pico
#   "estacionId": 1,
#   "usuarioId": 1
# }
# Respuesta: { "success": true, "message": "Lectura registrada correctamente" }
```

#### 5. **Consultar Avance de Orden** ✅

```python
# GET /api/ordenesDeFabricacion/avance?ordenFabricacion=OF-001
# Headers: { "empresa-id": "1" }  # Siempre usar empresa-id 1
# Respuesta: {
#   "success": true,
#   "data": {
#     "cantidadPendiente": 450,
#     "avance": 0.55
#   }
# }
```

#### 6. **Consultar Detalles Completos de Orden** ✅

```python
# GET /api/ordenesDeFabricacion/estatus?orden=OF-001
# Headers: { "empresa-id": "1" }
# Respuesta: {
#   "success": true,
#   "data": {
#     "ordenFabricacion": "OF-001",
#     "estatus": "EN_PROCESO",
#     "fechaInicio": "2024-12-01",
#     "fechaFin": "2024-12-15",
#     "cliente": "Cliente ABC",
#     "razonSocial": "Empresa ABC S.A.",
#     "articuloPT": "PT-001",
#     "descripcionPT": "Producto Terminado",
#     "cantidadPlanificada": 1000,
#     "caja": "Caja x 10",
#     "partidas": [
#       {
#         "articuloMP": "MP-001",
#         "descripcionMP": "Materia Prima A",
#         "cantidad": 500
#       }
#     ]
#   }
# }
```

#### 7. **Consultar Cajas Registradas** ✅

```python
# GET /api/lecturaUPC/cajas?ordenFabricacion=OF-001
# Headers: { "empresa-id": "1" }
# Respuesta: {
#   "success": true,
#   "total": 125  # Número de cajas registradas
# }
```

#### 8. **Registrar Caja (UPC Especial)** ✅

```python
# POST /api/lecturaUPC/registrarCaja
# Headers: { "empresa-id": "1" }
# Body: {
#   "ordenFabricacion": "OF-001",
#   "upc": "1234567890",
#   "estacionId": 1,
#   "usuarioId": 1
# }
# Respuesta: { "success": true, "message": "Caja registrada correctamente" }
```

#### 9. **Registrar Lote de Lecturas** ✅

```python
# POST /api/lecturaUPC/registrarLote
# Headers: { "empresa-id": "1" }
# Body: {
#   "lecturas": [
#     {
#       "ordenFabricacion": "OF-001",
#       "upc": "1234567890",
#       "estacionId": 1,
#       "usuarioId": 1,
#       "fechaLectura": "2024-12-01T10:30:00.000Z"
#     }
#   ]
# }
# Respuesta: { "success": true, "message": "Lote registrado correctamente" }
```

#### 10. **Obtener Imagen del Artículo** ✅

```python
# GET /api/articulos/imagen?articulo=PT-001
# Headers: { "empresa-id": "1" }
# Respuesta: {
#   "success": true,
#   "data": {
#     "url": "https://sisproone.net/images/articulos/PT-001.jpg"
#   }
# }
```

## 🎯 FLUJO DE TRABAJO

### 1. **Inicialización**

```python
# 1. Cargar configuración guardada (estación, empresa_id=1)
# 2. Autenticar con SISPRO usando credenciales MONITORPI
# 3. Conectar a RS485
# 4. Iniciar WebSocket server
```

### 2. **Selección de Estación**

```python
# 1. Consultar estaciones disponibles desde SISPRO
# 2. Mostrar lista de estaciones
# 3. Seleccionar estación (se guarda globalmente)
# 4. Consultar órdenes asignadas para la estación
```

### 3. **Selección de Orden**

```python
# 1. Mostrar órdenes disponibles
# 2. Seleccionar orden de fabricación
# 3. Consultar detalles completos de la orden (/api/ordenesDeFabricacion/estatus)
# 4. Obtener imagen del artículo (/api/articulos/imagen)
# 5. Consultar cajas ya registradas (/api/lecturaUPC/cajas)
# 6. Cambiar estado a "ESPERANDO_UPC"
# 7. Activar escucha de código de barras
```

### 4. **Validación UPC**

```python
# 1. Escanear código de barras
# 2. Validar contra ptUPC de la orden
# 3. UPC especial "1234567890128" = Cierre de caja
# 4. Si válido: agregar a lote local y cambiar estado a "PRODUCIENDO"
# 5. Si inválido: mostrar error y reintentar
# 6. Consultar progreso actual (/api/ordenesDeFabricacion/avance)
```

### 5. **Producción Local**

```python
# 1. Activar escucha RS485 del Pico
# 2. Recibir conteos en tiempo real
# 3. Almacenar en cache local (Redis + SQLite)
# 4. Mostrar progreso en pantalla
# 5. Manejar estados localmente
```

### 6. **Sincronización**

```python
# 1. Acumular lecturas del Pico en lotes locales (máximo 50 lecturas)
# 2. Enviar lotes usando /api/lecturaUPC/registrarLote
# 3. Registrar cajas especiales usando /api/lecturaUPC/registrarCaja
# 4. Consultar progreso actual (/api/ordenesDeFabricacion/avance)
# 5. Verificar estatus de orden (/api/ordenesDeFabricacion/estatus)
# 6. Limpiar cache local
# 7. Repetir cada 5 minutos o cuando se complete un lote
```

## 📊 ESTRUCTURA DE DATOS

### Estación

```python
class Estacion:
    id: int
    nombre: str
    descripcion: str
    estado: str  # ASIGNADA, INACTIVA
    coordinador_supervisor: str
    cuadrante: str
```

### Orden de Fabricación

```python
class OrdenFabricacion:
    id: int
    orden_fabricacion: str
    pt: str
    cantidad_fabricar: int
    cantidad_pendiente: int
    avance: float
    pt_descripcion: str
    pt_presentacion: str
    pt_upc: str
    estacion_nombre: str
    estacion_coordinador: str
    estacion_cuadrante: str
    prioridad: str  # NORMAL, ALTA, URGENTE
    is_closed: bool
```

### Detalles Completos de Orden

```python
class DetallesOrden:
    orden_fabricacion: str
    estatus: str  # EN_PROCESO, CANCELADA, COMPLETADA
    fecha_inicio: str
    fecha_fin: str
    cliente: str
    razon_social: str
    articulo_pt: str
    descripcion_pt: str
    cantidad_planificada: int
    caja: str
    partidas: List[MateriaPrima]

class MateriaPrima:
    articulo_mp: str
    descripcion_mp: str
    cantidad: int
```

### Lectura de Producción

```python
class LecturaProduccion:
    orden_fabricacion: str
    upc: str
    estacion_id: int
    usuario_id: int
    fecha_lectura: str  # ISO timestamp
    fuente: str  # RS485, BARCODE
    validada: bool

class LoteLecturas:
    lecturas: List[LecturaProduccion]
    timestamp_envio: datetime
    estado: str  # PENDIENTE, ENVIADO, ERROR
    intentos: int

class CajaRegistrada:
    orden_fabricacion: str
    upc: str
    estacion_id: int
    usuario_id: int
    fecha_registro: str
```

## 🔧 IMPLEMENTACIÓN TÉCNICA

### Configuración

```python
# config.py
SISPRO_CONFIG = {
    "base_url": "http://100.24.193.207:3000",  # IP alternativa: sisproone.net
    "username": "MONITORPI",
    "password": "56fg453drJ",
    "empresa_id": 1  # Siempre usar empresa-id 1
}

# Configuración de hardware
RS485_PORT = "/dev/ttyUSB0"
RS485_BAUDRATE = 9600

# Configuración de cache
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Configuración de servicios
WEBSOCKET_PORT = 8765

# Configuración de sincronización
SYNC_INTERVAL = 300  # 5 minutos en segundos
MAX_RETRIES = 3
TIMEOUT = 30  # segundos

# Configuración de lotes
MAX_BATCH_SIZE = 50  # Máximo de lecturas por lote
BATCH_TIMEOUT = 60  # Enviar lote después de X segundos sin actividad
UPC_CIERRE_CAJA = "1234567890128"  # UPC especial para cierre de caja
```

### Estados del Monitor

```python
class EstadoMonitor:
    INACTIVO = "INACTIVO"
    CONSULTANDO = "CONSULTANDO"
    ESPERANDO_UPC = "ESPERANDO_UPC"
    PRODUCIENDO = "PRODUCIENDO"
    PAUSADO = "PAUSADO"
    ERROR = "ERROR"
```

### Cache Manager

```python
class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.db = sqlite3.connect('monitor_cache.db')

    def guardar_lectura(self, estacion_id: str, datos: dict):
        # Guardar en SQLite (persistencia)
        # Guardar en Redis (acceso rápido)
        pass

    def obtener_estado(self, estacion_id: str = None):
        # Obtener desde Redis
        pass

    def obtener_lecturas_pendientes(self, estacion_id: str):
        # Obtener lecturas no enviadas
        pass
```

### Lote Manager

```python
class LoteManager:
    def __init__(self):
        self.lecturas_pendientes = []
        self.ultimo_timestamp = None
        self.max_batch_size = MAX_BATCH_SIZE
        self.batch_timeout = BATCH_TIMEOUT

    def agregar_lectura(self, lectura: LecturaProduccion):
        """Agregar lectura al lote actual"""
        self.lecturas_pendientes.append(lectura)
        self.ultimo_timestamp = datetime.now()

        # Enviar si alcanzamos el tamaño máximo
        if len(self.lecturas_pendientes) >= self.max_batch_size:
            return self.enviar_lote()

    def verificar_timeout(self):
        """Verificar si debemos enviar por timeout"""
        if (self.ultimo_timestamp and
            datetime.now() - self.ultimo_timestamp > timedelta(seconds=self.batch_timeout)):
            return self.enviar_lote()

    def enviar_lote(self):
        """Enviar lote actual a SISPRO"""
        if not self.lecturas_pendientes:
            return

        lote = self.lecturas_pendientes.copy()
        self.lecturas_pendientes.clear()
        return lote

    def obtener_cantidad_pendiente(self):
        """Obtener cantidad de lecturas pendientes"""
        return len(self.lecturas_pendientes)
```

### Clase Principal del Monitor

```python
class MonitorIndustrial:
    def __init__(self):
        self.config = SISPRO_CONFIG
        self.empresa_id = SISPRO_CONFIG["empresa_id"]
        self.sispro = SISPROConnector()
        self.rs485 = MonitorRS485()
        self.barcode = BarcodeValidator()
        self.cache = CacheManager()
        self.lote_manager = LoteManager()
        self.websocket = WebSocketServer()
        self.estado = EstadoManager()

    async def inicializar(self):
        """Inicializar el monitor (sin autenticación JWT)"""
        try:
            # 1. Verificar conectividad con SISPRO
            print("🔐 Verificando conectividad con SISPRO...")
            if not await self.sispro.verificar_conectividad():
                print("❌ Error de conectividad con SISPRO")
                return False
            print(f"✅ SISPRO conectado - Empresa ID: {self.empresa_id}")

            # 2. Conectar RS485
            print("🔌 Conectando a RS485...")
            if not self.rs485.conectar():
                print("❌ Error conectando RS485")
                return False
            print("✅ RS485 conectado")

            # 3. Iniciar servicios
            print("🚀 Iniciando servicios...")
            await self.websocket.iniciar()
            await self.cache.inicializar()
            print("✅ Servicios iniciados")

            return True

        except Exception as e:
            print(f"❌ Error en inicialización: {e}")
            return False

    async def ejecutar(self):
        """Ejecutar el ciclo principal del monitor"""
        print("🏭 Monitor Industrial iniciado")

        while True:
            try:
                # Procesar ciclo principal
                await self.procesar_ciclo()
                await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                print("\n🛑 Deteniendo monitor...")
                break
            except Exception as e:
                print(f"❌ Error en ciclo principal: {e}")
                await asyncio.sleep(5)  # Esperar antes de reintentar

    async def procesar_ciclo(self):
        """Procesar un ciclo del monitor"""
        # Lógica del ciclo principal
        pass
```

## 🚀 COMANDOS RS485

### Comandos para Pico

```python
# Activar estación
comando = f"{device_id}:ACTIVAR:{producto_id}"

# Pausar estación
comando = f"{device_id}:PAUSAR:0"

# Resetear estación
comando = f"{device_id}:RESET:0"

# Establecer meta
comando = f"{device_id}:META:{cantidad}"
```

### Respuestas del Pico

```python
# Formato: "DEVICE_ID:TAG:VALOR"
# Ejemplos:
# "EST001:CONT:1250"     # Contador actual
# "EST001:TOTAL:5000"    # Total acumulado
# "EST001:ESTADO:1"      # 1=Activo, 0=Inactivo
# "EST001:RESET:0"       # Reset confirmado
```

## 📱 INTERFAZ DE USUARIO

### Menú Principal

```
┌─────────────────────────────────────┐
│ 🍓 MONITOR INDUSTRIAL SISPRO       │
├─────────────────────────────────────┤
│ 📍 Estación: EST001                │
│ 🔄 Estado: PRODUCIENDO             │
│ 📦 Orden: OF-001                   │
│ 🔢 Contador: 1,247 / 5,000        │
│ 📊 Progreso: ████████░░ 24.9%     │
├─────────────────────────────────────┤
│ 1. Configurar estación             │
│ 2. Consultar carga de trabajo      │
│ 3. Seleccionar orden               │
│ 4. Ver estado actual               │
│ 5. Salir                          │
└─────────────────────────────────────┘
```

### Estados Visuales

- 🔴 **INACTIVO**: Monitor apagado
- 🟡 **CONSULTANDO**: Consultando SISPRO
- 🟡 **ESPERANDO_UPC**: Esperando código de barras
- 🟢 **PRODUCIENDO**: Contando con Pico
- 🟠 **PAUSADO**: Producción pausada
- 🔴 **ERROR**: Error de comunicación

## 🔄 SINCRONIZACIÓN

### Sincronización con SISPRO

```python
# Cada 5 minutos
async def sincronizar_datos():
    datos = cache.obtener_estado()
    await sispro.enviar_lecturas(datos)
    await sispro.actualizar_estados(datos)
```

### Sincronización con Pico

```python
# Tiempo real
async def procesar_mensaje_rs485(mensaje):
    datos = parsear_mensaje(mensaje)
    cache.guardar_lectura(datos)
    await websocket.broadcast(datos)
```

## 🛠️ DEPENDENCIAS

### Python Packages

```txt
aiohttp>=3.8.0
asyncio
pyserial>=3.5
redis>=4.0.0
websockets>=10.0
sqlite3
datetime
json
```

### Hardware

- Raspberry Pi 4B+
- Raspberry Pi Pico
- Módulo RS485
- Lector de código de barras USB
- Pantalla táctil (opcional)

## 📁 ESTRUCTURA DE ARCHIVOS

```
monitor_industrial/
├── main.py                 # Punto de entrada
├── config.py              # Configuración
├── monitor_rs485.py       # Comunicación RS485
├── sispro_connector.py    # Comunicación SISPRO
├── barcode_validator.py   # Validación UPC
├── cache_manager.py       # Gestión de cache
├── websocket_server.py    # Servidor WebSocket
├── estado_manager.py      # Gestión de estados
├── interfaz.py           # Interfaz de usuario
├── requirements.txt      # Dependencias
├── monitor_cache.db      # Base de datos local
└── logs/                 # Archivos de log
```

### Script Principal (main.py)

```python
#!/usr/bin/env python3
"""
Monitor Industrial - Punto de entrada principal
"""

import asyncio
import sys
from monitor_industrial import MonitorIndustrial

async def main():
    """Función principal del monitor"""
    print("🍓 MONITOR INDUSTRIAL SISPRO")
    print("=" * 50)

    # Crear instancia del monitor
    monitor = MonitorIndustrial()

    # Inicializar el monitor
    if not await monitor.inicializar():
        print("❌ No se pudo inicializar el monitor")
        sys.exit(1)

    try:
        # Ejecutar el monitor
        await monitor.ejecutar()
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔒 SEGURIDAD

### Autenticación

- **Credenciales específicas**:
  - Usuario: `MONITORPI`
  - Password: `56fg453drJ`
  - URL: `http://100.24.193.207:3000` (alternativa: `sisproone.net`)
  - Empresa ID: `1` (fijo)
- **Token JWT** para SISPRO obtenido via middleware
- **Renovación automática** de tokens cuando expire
- **Manejo seguro** de credenciales en variables de entorno

### Validación

- Validación de UPC contra orden asignada
- Verificación de estación autorizada
- Logs de todas las operaciones

## ⚡ PERFORMANCE

### Optimizaciones

- Cache local para datos frecuentes
- Sincronización asíncrona con SISPRO
- Procesamiento en tiempo real de RS485
- WebSocket para actualizaciones instantáneas

### Monitoreo

- Logs de rendimiento
- Métricas de comunicación
- Alertas de errores
- Estado de conexiones

## 🧪 TESTING

### Tests Unitarios

- Validación de UPC
- Comunicación RS485
- Cache management
- Sincronización SISPRO

### Tests de Integración

- Flujo completo de producción
- Comunicación Pi ↔ Pico
- Comunicación Pi ↔ SISPRO
- Recuperación de errores

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Base

- [ ] Configuración inicial
- [ ] Comunicación RS485
- [ ] Cache local (SQLite + Redis)
- [ ] Interfaz básica

### Fase 2: SISPRO (APIs ya existen)

- [ ] Autenticación
- [ ] Consulta de estaciones
- [ ] Consulta de órdenes
- [ ] Validación UPC
- [ ] Sincronización de lecturas

### Fase 3: Producción

- [ ] Validación UPC
- [ ] Estados de producción
- [ ] Sincronización
- [ ] WebSocket server

### Fase 4: Optimización

- [ ] Manejo de errores
- [ ] Recuperación automática
- [ ] Logs y monitoreo
- [ ] Tests

## 🚨 CONSIDERACIONES IMPORTANTES

### Robustez

- Manejo de desconexiones de red
- Recuperación automática de errores
- Persistencia de datos críticos
- Logs detallados para debugging

### Escalabilidad

- Soporte para múltiples estaciones
- Configuración flexible
- Fácil mantenimiento
- Documentación completa

### Mantenimiento

- Logs rotativos
- Monitoreo de salud
- Alertas automáticas
- Actualizaciones remotas

## 🚀 **RESUMEN EJECUTIVO**

### ✅ **TODAS LAS APIs YA EXISTEN**

- **No crear APIs adicionales** - Usar las existentes en SISPRO
- **Integración completa** - Se conecta directamente con el sistema actual
- **Máxima eficiencia** - Todo local + sincronización inteligente

### 🎯 **ARQUITECTURA SIMPLIFICADA**

- **Raspberry Pi maneja TODO localmente** - Sin dependencias de red
- **Solo sincroniza al final** - Cada 5 minutos o cuando sea necesario
- **Cache inteligente** - Datos en memoria + disco
- **Recuperación automática** - Reinicia solo si falla

### 📊 **FLUJO DE TRABAJO**

1. **Inicialización** → Cargar config + autenticar SISPRO
2. **Selección de Estación** → Consultar estaciones + guardar globalmente
3. **Selección de Orden** → Consultar órdenes asignadas + mostrar menú
4. **Validación UPC** → Escanear código + validar contra orden
5. **Producción Local** → Activar RS485 + procesar conteos localmente
6. **Sincronización** → Subir lecturas a SISPRO cada 5 minutos

### 🎉 **RESULTADO FINAL**

**¡El proyecto está 100% listo para implementar!**

- ✅ **Sin APIs adicionales** - Usa las existentes
- ✅ **Arquitectura simple** - Todo local + sincronización
- ✅ **Máxima eficiencia** - Tiempo real + confiabilidad
- ✅ **Fácil mantenimiento** - Un solo sistema de APIs

---

**Versión**: 1.1.0
**Última actualización**: Diciembre 2024
**Mantenido por**: Equipo de Desarrollo sisproone
