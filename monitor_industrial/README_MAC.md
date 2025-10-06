# 🍓 Monitor Industrial SISPRO - Versión Mac (Pruebas)

## 📋 Descripción

Versión de prueba del Monitor Industrial SISPRO para Mac que simula todo el hardware y permite probar la funcionalidad completa sin necesidad de Raspberry Pi o Pico.

## 🎯 Características de la Versión Mac

### ✅ **Simulaciones Incluidas:**

- **RS485 Simulado** - Simula comunicación con Raspberry Pi Pico
- **SISPRO Simulado** - Simula APIs de SISPRO con datos de prueba
- **Lecturas Automáticas** - Genera conteos de producción automáticamente
- **Interfaz Adaptada** - Optimizada para Mac (no fullscreen por defecto)

### 🖥️ **Interfaz Mac:**

- **Ventana redimensionable** (1200x800 por defecto)
- **No fullscreen** por defecto para facilitar pruebas
- **Atajos de teclado** adaptados para Mac (Cmd+Q para salir)
- **Colores optimizados** para mejor contraste en Mac

## 🚀 Instalación Rápida

### 1. Instalar dependencias

```bash
# Instalar dependencias mínimas
pip install python-dateutil

# O usar el archivo de requisitos
pip install -r requirements_mac.txt
```

### 2. Ejecutar el monitor

```bash
# Opción 1: Ejecutar directamente
python test_mac.py

# Opción 2: Usar script de ejecución
python run_mac.py

# Opción 3: Hacer ejecutable
chmod +x run_mac.py
./run_mac.py
```

## 🎮 Flujo de Prueba

### 1. **Inicio del Sistema**

- El monitor se inicia en modo simulación
- Muestra mensaje de "MODO PRUEBA MAC"
- Carga datos de prueba (estaciones y órdenes)

### 2. **Selección de Estación**

- Hacer clic en "🏭 SELECCIONAR ESTACIÓN"
- Aparecen 2 estaciones de prueba:
  - **Estación 001** - Juan Pérez - Cuadrante A
  - **Estación 002** - María García - Cuadrante B

### 3. **Selección de Orden**

- Hacer clic en "📦 SELECCIONAR ORDEN"
- Aparecen órdenes asignadas a la estación:
  - **OF-001** - Producto A (1000 unidades) - UPC: 123456789012
  - **OF-002** - Producto B (500 unidades) - UPC: 987654321098

### 4. **Validación UPC**

- Hacer clic en "📱 VALIDAR UPC"
- Ingresar uno de los UPCs de prueba:
  - `123456789012` (para OF-001)
  - `987654321098` (para OF-002)
- El sistema valida y activa la producción

### 5. **Producción Simulada**

- El Pico simulado comienza a enviar conteos automáticamente
- Los conteos aparecen en tiempo real en la interfaz
- La barra de progreso se actualiza automáticamente
- Los datos se sincronizan cada 30 segundos

### 6. **Finalización**

- Hacer clic en "✅ FINALIZAR ORDEN" para terminar
- El sistema cierra la orden y desactiva el Pico

## 🔧 Datos de Prueba

### **Estaciones de Prueba:**

```json
{
  "Estación 001": {
    "id": 1,
    "nombre": "Estación 001",
    "coordinador": "Juan Pérez",
    "cuadrante": "Cuadrante A"
  },
  "Estación 002": {
    "id": 2,
    "nombre": "Estación 002",
    "coordinador": "María García",
    "cuadrante": "Cuadrante B"
  }
}
```

### **Órdenes de Prueba:**

```json
{
  "OF-001": {
    "producto": "Producto de Prueba A",
    "cantidad": 1000,
    "upc": "123456789012",
    "presentacion": "Caja x 10"
  },
  "OF-002": {
    "producto": "Producto de Prueba B",
    "cantidad": 500,
    "upc": "987654321098",
    "presentacion": "Caja x 5"
  },
  "OF-003": {
    "producto": "Producto de Prueba C",
    "cantidad": 750,
    "upc": "112233445566",
    "presentacion": "Caja x 15"
  }
}
```

## 🎛️ Controles de la Interfaz

### **Botones Principales:**

- **🏭 SELECCIONAR ESTACIÓN** - Elegir estación de trabajo
- **📦 SELECCIONAR ORDEN** - Elegir orden de fabricación
- **📱 VALIDAR UPC** - Escanear/ingresar código de barras
- **✅ FINALIZAR ORDEN** - Terminar orden actual
- **🔄 SINCRONIZAR** - Sincronizar datos inmediatamente
- **🚪 SALIR** - Cerrar aplicación

### **Atajos de Teclado:**

- **Escape** - Salir de la aplicación
- **Cmd+Q** - Salir de la aplicación (Mac)
- **F11** - Alternar modo fullscreen

### **Información en Tiempo Real:**

- **Contador** - Cantidad producida actual
- **Meta** - Cantidad objetivo
- **Progreso** - Porcentaje completado
- **Estado** - Estado actual del sistema
- **Estado Pico** - Estado del Pico simulado
- **Última Sincronización** - Timestamp de última sync

## 🔍 Simulaciones Detalladas

### **Simulador RS485:**

- Genera mensajes cada 2-5 segundos cuando está activo
- Envía conteos incrementales (1-3 por mensaje)
- Simula heartbeat y estado de inactividad
- Responde a comandos de activación/desactivación

### **Simulador SISPRO:**

- Mantiene datos de estaciones y órdenes en memoria
- Registra lecturas UPC automáticamente
- Calcula avance de órdenes basado en lecturas
- Simula cierre de órdenes

### **Cache Local:**

- Usa solo SQLite (sin Redis para simplificar)
- Almacena todas las lecturas localmente
- Marca lecturas como sincronizadas
- Mantiene estadísticas del sistema

## 📊 Monitoreo y Logs

### **Logs del Sistema:**

```bash
# Ver logs en tiempo real
tail -f logs/monitor_mac_YYYYMMDD.log

# Buscar errores
grep "ERROR" logs/monitor_mac_*.log

# Ver actividad de producción
grep "PRODUCIENDO" logs/monitor_mac_*.log
```

### **Base de Datos:**

```bash
# Ver lecturas guardadas
sqlite3 monitor_cache_mac.db "SELECT * FROM lecturas_produccion;"

# Ver estadísticas
sqlite3 monitor_cache_mac.db "SELECT COUNT(*) FROM lecturas_produccion;"

# Ver lecturas pendientes
sqlite3 monitor_cache_mac.db "SELECT COUNT(*) FROM lecturas_produccion WHERE sincronizada = FALSE;"
```

## 🐛 Solución de Problemas

### **Error de Importación:**

```bash
# Asegúrate de estar en el directorio correcto
cd monitor_industrial

# Verificar que los archivos estén presentes
ls -la *.py
```

### **Error de Tkinter:**

```bash
# En macOS, tkinter debería estar incluido
python3 -c "import tkinter; print('Tkinter OK')"

# Si no está, instalar con Homebrew
brew install python-tk
```

### **Error de Base de Datos:**

```bash
# Eliminar base de datos corrupta
rm monitor_cache_mac.db

# El sistema la recreará automáticamente
```

## 🎯 Casos de Prueba

### **Caso 1: Flujo Completo**

1. Iniciar monitor
2. Seleccionar Estación 001
3. Seleccionar OF-001
4. Validar UPC: 123456789012
5. Observar producción automática
6. Finalizar orden

### **Caso 2: UPC Inválido**

1. Seleccionar estación y orden
2. Validar UPC incorrecto: 999999999999
3. Verificar mensaje de error
4. Validar UPC correcto: 123456789012

### **Caso 3: Múltiples Órdenes**

1. Completar OF-001
2. Seleccionar OF-002
3. Validar UPC: 987654321098
4. Observar nueva producción

### **Caso 4: Sincronización**

1. Iniciar producción
2. Esperar 30 segundos
3. Verificar logs de sincronización
4. Verificar base de datos

## 🔄 Diferencias con Versión Raspberry Pi

| Característica     | Mac (Prueba) | Raspberry Pi (Producción) |
| ------------------ | ------------ | ------------------------- |
| **RS485**          | Simulado     | Hardware real             |
| **SISPRO**         | Simulado     | APIs reales               |
| **Redis**          | No usado     | Sí usado                  |
| **Fullscreen**     | Opcional     | Siempre                   |
| **Datos**          | De prueba    | Reales                    |
| **Sincronización** | 30 segundos  | 5 minutos                 |

## 📚 Próximos Pasos

1. **Probar funcionalidad** - Ejecutar casos de prueba
2. **Personalizar datos** - Modificar estaciones/órdenes de prueba
3. **Ajustar interfaz** - Cambiar colores, tamaños, etc.
4. **Implementar en Raspberry Pi** - Usar versión de producción
5. **Conectar hardware real** - Pico y RS485

---

**¡Listo para probar!** 🚀

Ejecuta `python test_mac.py` y comienza a explorar el Monitor Industrial SISPRO.
