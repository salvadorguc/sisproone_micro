# 🏗️ Arquitectura Simplificada - Monitor Industrial

## 🎯 **ENFOQUE SIMPLIFICADO**

La Raspberry Pi maneja **TODO localmente** y solo sincroniza con SISPRO al final.

## 📊 **FLUJO DE TRABAJO ACTUALIZADO**

```
┌─────────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI (PYTHON)                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. Inicialización                                              │
│    ├── Cargar configuración guardada                          │
│    ├── Autenticar con SISPRO (una sola vez)                   │
│    └── Conectar a RS485                                       │
│                                                                 │
│ 2. Configuración Inicial                                       │
│    ├── Consultar estaciones → /api/estacionesTrabajo          │
│    ├── Seleccionar estación (se guarda globalmente)           │
│    ├── Consultar órdenes → /api/ordenesDeFabricacion/listarAsignadas │
│    └── Seleccionar orden de fabricación                       │
│                                                                 │
│ 3. Validación UPC (Una sola vez)                              │
│    ├── Escanear código de barras                              │
│    ├── Validar contra ptUPC de la orden                       │
│    └── Confirmar producto correcto                            │
│                                                                 │
│ 4. PRODUCCIÓN LOCAL (Tiempo real)                             │
│    ├── Activar escucha RS485 del Pico                         │
│    ├── Recibir conteos en tiempo real                         │
│    ├── Almacenar en cache local (Redis + SQLite)              │
│    ├── Mostrar progreso en pantalla                           │
│    └── Manejar estados localmente                             │
│                                                                 │
│ 5. SINCRONIZACIÓN (Cada 5 minutos)                            │
│    ├── Agregar lecturas acumuladas                            │
│    ├── Enviar a SISPRO → /api/lecturaUPC/registrar            │
│    ├── Actualizar avance → /api/ordenesDeFabricacion/avance   │
│    └── Limpiar cache local                                    │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                    SISPRO (NEXT.JS)                            │
├─────────────────────────────────────────────────────────────────┤
│ ✅ /api/estacionesTrabajo - Obtener estaciones                │
│ ✅ /api/ordenesDeFabricacion/listarAsignadas - Listar órdenes │
│ ✅ /api/lecturaUPC/registrar - Sincronizar lecturas           │
│ ✅ /api/ordenesDeFabricacion/avance - Actualizar avance       │
│ ✅ /api/lecturaUPC/consultar - Consultar historial            │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI PICO                           │
├─────────────────────────────────────────────────────────────────┤
│ ├── Sensor RS485                                               │
│ ├── Envío de conteos: "EST001:CONT:1250"                      │
│ ├── Recepción de comandos: "EST001:ACTIVAR:PROD123"           │
│ └── Comunicación serial con Pi                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 **VENTAJAS DE ESTA ARQUITECTURA**

### **Para la Raspberry Pi**

- ✅ **Independencia total** - Funciona sin conexión a internet
- ✅ **Procesamiento local** - Sin latencia de red
- ✅ **Cache inteligente** - Datos en memoria + disco
- ✅ **Recuperación automática** - Reinicia solo si falla
- ✅ **Sincronización eficiente** - Solo cambios importantes

### **Para SISPRO**

- ✅ **Sin cambios** - Usa APIs existentes
- ✅ **Compatibilidad** - Funciona con sistema actual
- ✅ **Escalabilidad** - Fácil agregar más monitores
- ✅ **Auditoría** - Todas las lecturas en la misma base de datos

### **Para el Operador**

- ✅ **Velocidad** - Conteo en tiempo real
- ✅ **Confiabilidad** - No depende de la red
- ✅ **Simplicidad** - Un scan y listo
- ✅ **Visibilidad** - Progreso en pantalla local

## 📱 **INTERFAZ LOCAL DEL MONITOR**

```
┌─────────────────────────────────────────────────────────────────┐
│ 🍓 MONITOR INDUSTRIAL SISPRO - ESTACIÓN 001                   │
├─────────────────────────────────────────────────────────────────┤
│ 📦 Orden: OF-001 | Producto: PROD-12345                       │
│ 🔢 Contador: 1,247 / 5,000 | Progreso: ████████░░ 24.9%      │
│ 🟢 Estado: PRODUCIENDO | Fuente: RS485                        │
├─────────────────────────────────────────────────────────────────┤
│ 📊 ESTADÍSTICAS LOCALES                                        │
│ ├── Lecturas por minuto: 45                                   │
│ ├── Tiempo estimado restante: 1h 23m                          │
│ ├── Última sincronización: 10:25:30                           │
│ └── Lecturas pendientes: 23                                   │
├─────────────────────────────────────────────────────────────────┤
│ 🔧 COMANDOS                                                    │
│ ├── [P] Pausar producción                                     │
│ ├── [R] Reanudar producción                                   │
│ ├── [S] Sincronizar ahora                                     │
│ ├── [C] Cambiar orden                                         │
│ └── [Q] Salir                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🗄️ **GESTIÓN DE DATOS LOCAL**

### **SQLite (Persistencia)**

```sql
-- Cache local de lecturas
CREATE TABLE lecturas_pendientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_fabricacion TEXT,
    cantidad INTEGER,
    timestamp DATETIME,
    sincronizada BOOLEAN DEFAULT FALSE
);

-- Configuración de la estación
CREATE TABLE configuracion (
    clave TEXT PRIMARY KEY,
    valor TEXT,
    actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Redis (Cache Rápido)**

```python
# Estado actual de la estación
estacion:EST001 = {
    "orden_actual": "OF-001",
    "producto": "PROD-12345",
    "contador": 1247,
    "meta": 5000,
    "estado": "PRODUCIENDO",
    "ultima_lectura": "2024-12-19T10:30:00Z"
}

# Lecturas pendientes de sincronización
lecturas_pendientes:EST001 = [
    {"cantidad": 50, "timestamp": "2024-12-19T10:25:00Z"},
    {"cantidad": 45, "timestamp": "2024-12-19T10:26:00Z"},
    {"cantidad": 52, "timestamp": "2024-12-19T10:27:00Z"}
]
```

## ⚡ **SINCRONIZACIÓN INTELIGENTE**

### **Estrategia de Sincronización**

```python
async def sincronizar_lecturas():
    """Sincronizar lecturas pendientes con SISPRO"""

    # 1. Obtener lecturas pendientes del cache local
    lecturas_pendientes = cache.obtener_lecturas_pendientes()

    if not lecturas_pendientes:
        return

    # 2. Agregar lecturas acumuladas
    cantidad_total = sum(lectura['cantidad'] for lectura in lecturas_pendientes)

    # 3. Enviar a SISPRO usando API existente
    await sispro.registrar_lectura_upc(
        orden_fabricacion=orden_actual,
        upc='RS485_BATCH',  # Identificador para lecturas del Pico
        estacion_id=estacion_id,
        usuario_id=usuario_id
    )

    # 4. Marcar como sincronizadas
    cache.marcar_como_sincronizadas(lecturas_pendientes)

    # 5. Actualizar avance
    await sispro.consultar_avance(orden_actual)
```

## 🚀 **IMPLEMENTACIÓN RECOMENDADA**

### **1. No Crear APIs Adicionales** ✅

- Todas las APIs necesarias ya existen
- Solo usar `/api/lecturaUPC/registrar` para sincronizar

### **2. Implementar Monitor Python**

- Seguir la guía en `cursorrules_python_monitor.md`
- Usar el mapeo en `api_mapping_monitor.md`

### **3. Configurar Hardware**

- Raspberry Pi + Raspberry Pi Pico
- Comunicación RS485
- Lector de código de barras

### **4. Probar Integración**

- Flujo completo de producción
- Sincronización de datos
- Manejo de errores

## 🎯 **RESULTADO FINAL**

**¡El proyecto está 100% listo para implementar!**

- ✅ **Sin APIs adicionales** - Usa las existentes
- ✅ **Arquitectura simple** - Todo local + sincronización
- ✅ **Máxima eficiencia** - Tiempo real + confiabilidad
- ✅ **Fácil mantenimiento** - Un solo sistema de APIs
