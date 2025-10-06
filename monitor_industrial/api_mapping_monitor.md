# Mapeo de APIs - Monitor.tsx → Python Monitor

## 📊 ANÁLISIS DEL COMPONENTE Monitor.tsx

### Interfaces Principales

#### Station Interface

```typescript
interface Station {
  id: number;
  nombre: string;
  descripcion: string;
  estado: string;
  coordinadorSupervisor: string;
  cuadrante: string;
  ordenesAsignadas: number;
  cantidadTotalFabricar: number;
  cantidadTotalPendiente: number;
}
```

#### AsignacionOrden Interface

```typescript
interface AsignacionOrden {
  id: number;
  ordenFabricacion: string;
  pt: string;
  cantidadFabricar: number;
  cantidadPendiente: number;
  avance: number;
  ptDescripcion: string;
  ptPresentacion: string;
  ptUPC: string;
  estacionNombre: string;
  estacionCoordinador: string | null;
  estacionCuadrante: string | null;
  prioridad?: 'NORMAL' | 'ALTA' | 'URGENTE';
  isClosed?: boolean;
}
```

## 🔌 ENDPOINTS IDENTIFICADOS

### 1. **Obtener Estaciones de Trabajo**

```typescript
// Frontend: components/Monitor.tsx:88
const response = await axios.get<ApiEstacionesResponse>('/api/estacionesTrabajo', {
  headers: {
    'empresa-id': empresa.id,
  },
});
```

**✅ API EXISTENTE: `pages/api/estacionesTrabajo.ts`**

**Mapeo Python:**

```python
# GET /api/estacionesTrabajo
async def obtener_estaciones(empresa_id: int) -> List[Estacion]:
    headers = {
        'empresa-id': str(empresa_id)
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SISPRO_BASE_URL}/api/estacionesTrabajo", headers=headers) as response:
            data = await response.json()
            return data['data'] if data['success'] else []
```

### 2. **Obtener Órdenes Asignadas**

```typescript
// Frontend: components/Monitor.tsx:132
const response = await axios.get<{
  success: boolean;
  data: AsignacionOrden[];
}>(`/api/ordenesDeFabricacion/listarAsignadas?estacionTrabajoId=${selectedStation.id}`, {
  headers: {
    'empresa-id': empresa.id.toString(),
  },
});
```

**✅ API EXISTENTE: `pages/api/ordenesDeFabricacion/listarAsignadas.ts`**

**Mapeo Python:**

```python
# GET /api/ordenesDeFabricacion/listarAsignadas?estacionTrabajoId=1
async def obtener_ordenes_asignadas(empresa_id: int, estacion_id: int) -> List[AsignacionOrden]:
    headers = {
        'empresa-id': str(empresa_id)
    }
    params = {'estacionTrabajoId': estacion_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{SISPRO_BASE_URL}/api/ordenesDeFabricacion/listarAsignadas",
            headers=headers,
            params=params
        ) as response:
            data = await response.json()
            return data['data'] if data['success'] else []
```

### 3. **Cambiar Prioridad de Orden**

```typescript
// Frontend: components/Monitor.tsx:202
await axios.post(
  '/api/ordenesDeFabricacion/cambiarPrioridad',
  {
    ordenFabricacion,
    prioridad,
    estacionId: selectedStation?.id,
  },
  {
    headers: {
      'empresa-id': empresa?.id.toString(),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  }
);
```

**Mapeo Python:**

```python
# POST /api/ordenesDeFabricacion/cambiarPrioridad
async def cambiar_prioridad_orden(empresa_id: int, orden_fabricacion: str, prioridad: str, estacion_id: int):
    headers = {
        'empresa-id': str(empresa_id),
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'ordenFabricacion': orden_fabricacion,
        'prioridad': prioridad,
        'estacionId': estacion_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{SISPRO_BASE_URL}/api/ordenesDeFabricacion/cambiarPrioridad",
            headers=headers,
            json=data
        ) as response:
            return await response.json()
```

### 4. **Cerrar Orden**

```typescript
// Frontend: components/Monitor.tsx:225
await axios.post(
  '/api/ordenesDeFabricacion/cerrarOrden',
  {
    ordenFabricacion,
    estacionId: selectedStation?.id,
  },
  {
    headers: {
      'empresa-id': empresa?.id.toString(),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  }
);
```

**Mapeo Python:**

```python
# POST /api/ordenesDeFabricacion/cerrarOrden
async def cerrar_orden(empresa_id: int, orden_fabricacion: str, estacion_id: int):
    headers = {
        'empresa-id': str(empresa_id),
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'ordenFabricacion': orden_fabricacion,
        'estacionId': estacion_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{SISPRO_BASE_URL}/api/ordenesDeFabricacion/cerrarOrden",
            headers=headers,
            json=data
        ) as response:
            return await response.json()
```

### 5. **Reabrir Orden**

```typescript
// Frontend: components/Monitor.tsx:247
await axios.post(
  '/api/ordenesDeFabricacion/reabrirOrden',
  {
    ordenFabricacion,
    estacionId: selectedStation?.id,
  },
  {
    headers: {
      'empresa-id': empresa?.id.toString(),
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  }
);
```

**Mapeo Python:**

```python
# POST /api/ordenesDeFabricacion/reabrirOrden
async def reabrir_orden(empresa_id: int, orden_fabricacion: str, estacion_id: int):
    headers = {
        'empresa-id': str(empresa_id),
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'ordenFabricacion': orden_fabricacion,
        'estacionId': estacion_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{SISPRO_BASE_URL}/api/ordenesDeFabricacion/reabrirOrden",
            headers=headers,
            json=data
        ) as response:
            return await response.json()
```

### 6. **Registrar Lectura UPC**

```typescript
// Frontend: LecturaUPCModal component
await axios.post(
  '/api/lecturaUPC/registrar',
  {
    ordenFabricacion,
    upc,
    estacionId,
    usuarioId,
  },
  {
    headers: {
      'empresa-id': empresaId.toString(),
    },
  }
);
```

**✅ API EXISTENTE: `pages/api/lecturaUPC/registrar.ts`**

**Mapeo Python:**

```python
# POST /api/lecturaUPC/registrar
async def registrar_lectura_upc(empresa_id: int, orden_fabricacion: str, upc: str, estacion_id: int, usuario_id: int):
    headers = {
        'empresa-id': str(empresa_id),
        'Content-Type': 'application/json'
    }
    data = {
        'ordenFabricacion': orden_fabricacion,
        'upc': upc,
        'estacionId': estacion_id,
        'usuarioId': usuario_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{SISPRO_BASE_URL}/api/lecturaUPC/registrar",
            headers=headers,
            json=data
        ) as response:
            return await response.json()
```

### 7. **Consultar Lecturas UPC**

```typescript
// Frontend: LecturaUPCModal component
await axios.get(
  `/api/lecturaUPC/consultar?fechaInicial=${fechaInicial}&fechaFinal=${fechaFinal}&estacionId=${estacionId}`,
  {
    headers: {
      'empresa-id': empresaId.toString(),
    },
  }
);
```

**✅ API EXISTENTE: `pages/api/lecturaUPC/consultar.ts`**

**Mapeo Python:**

```python
# GET /api/lecturaUPC/consultar
async def consultar_lecturas_upc(empresa_id: int, fecha_inicial: str, fecha_final: str, estacion_id: int):
    headers = {
        'empresa-id': str(empresa_id)
    }
    params = {
        'fechaInicial': fecha_inicial,
        'fechaFinal': fecha_final,
        'estacionId': estacion_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{SISPRO_BASE_URL}/api/lecturaUPC/consultar",
            headers=headers,
            params=params
        ) as response:
            data = await response.json()
            return data['data'] if data['success'] else []
```

### 8. **Consultar Avance de Orden**

```typescript
// Frontend: Monitor component
await axios.get(`/api/ordenesDeFabricacion/avance?ordenFabricacion=${ordenFabricacion}`, {
  headers: {
    'empresa-id': empresaId.toString(),
  },
});
```

**✅ API EXISTENTE: `pages/api/ordenesDeFabricacion/avance.ts`**

**Mapeo Python:**

```python
# GET /api/ordenesDeFabricacion/avance
async def consultar_avance_orden(empresa_id: int, orden_fabricacion: str):
    headers = {
        'empresa-id': str(empresa_id)
    }
    params = {'ordenFabricacion': orden_fabricacion}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{SISPRO_BASE_URL}/api/ordenesDeFabricacion/avance",
            headers=headers,
            params=params
        ) as response:
            data = await response.json()
            return data['data'] if data['success'] else None
```

## 📝 ENDPOINTS ADICIONALES RECOMENDADOS

### 1. **Registrar Lectura de Producción RS485** (RECOMENDADO)

```typescript
// CREAR: /api/ordenesDeFabricacion/registrarLecturaRS485
export async function POST(request: NextRequest) {
  const validationResponse = await validateToken(request);
  if (validationResponse) return validationResponse;

  const empresaId = request.headers.get('empresa-id');
  if (!empresaId) {
    return NextResponse.json(
      { success: false, message: 'Se requiere empresa-id' },
      { status: 400 }
    );
  }

  const { ordenFabricacion, estacionId, usuarioId, cantidad, timestamp, fuente } =
    await request.json();

  if (!ordenFabricacion || !estacionId || !usuarioId || !cantidad) {
    return NextResponse.json(
      { success: false, message: 'Faltan datos requeridos' },
      { status: 400 }
    );
  }

  try {
    // Obtener empresa y databaseUrl
    const empresa = await prismaClient.empresa.findUnique({
      where: { id: Number(empresaId) },
      select: { databaseUrl: true },
    });

    if (!empresa?.databaseUrl) {
      return NextResponse.json(
        { success: false, message: 'Empresa no encontrada' },
        { status: 404 }
      );
    }

    const prisma = new PrismaClient({
      datasources: { db: { url: empresa.databaseUrl } },
    });

    // Registrar lectura de producción
    const lectura = await prisma.lecturaProduccion.create({
      data: {
        ordenFabricacion,
        estacionId: Number(estacionId),
        usuarioId: Number(usuarioId),
        cantidad: Number(cantidad),
        timestamp: timestamp ? new Date(timestamp) : new Date(),
        fuente: fuente || 'RS485',
        validada: true,
      },
    });

    // Actualizar cantidad pendiente en ordenEstacion
    await prisma.ordenEstacion.updateMany({
      where: {
        ordenFabricacion,
        estacionId: Number(estacionId),
      },
      data: {
        cantidadPendiente: {
          decrement: Number(cantidad),
        },
      },
    });

    return NextResponse.json({
      success: true,
      message: 'Lectura registrada correctamente',
      data: lectura,
    });
  } catch (error) {
    logger.error('Error al registrar lectura:', error);
    return NextResponse.json(
      { success: false, message: 'Error al registrar lectura' },
      { status: 500 }
    );
  }
}
```

### 2. **Actualizar Estado de Orden** (RECOMENDADO)

```typescript
// CREAR: /api/ordenesDeFabricacion/actualizarEstado
export async function POST(request: NextRequest) {
  const validationResponse = await validateToken(request);
  if (validationResponse) return validationResponse;

  const empresaId = request.headers.get('empresa-id');
  if (!empresaId) {
    return NextResponse.json(
      { success: false, message: 'Se requiere empresa-id' },
      { status: 400 }
    );
  }

  const { ordenFabricacion, estacionId, estado, cantidadPendiente } = await request.json();

  if (!ordenFabricacion || !estacionId || !estado) {
    return NextResponse.json(
      { success: false, message: 'Faltan datos requeridos' },
      { status: 400 }
    );
  }

  try {
    const empresa = await prismaClient.empresa.findUnique({
      where: { id: Number(empresaId) },
      select: { databaseUrl: true },
    });

    if (!empresa?.databaseUrl) {
      return NextResponse.json(
        { success: false, message: 'Empresa no encontrada' },
        { status: 404 }
      );
    }

    const prisma = new PrismaClient({
      datasources: { db: { url: empresa.databaseUrl } },
    });

    // Actualizar estado de la orden
    const updateData: any = {
      estado,
      updatedAt: new Date(),
    };

    if (cantidadPendiente !== undefined) {
      updateData.cantidadPendiente = cantidadPendiente;
    }

    await prisma.ordenEstacion.updateMany({
      where: {
        ordenFabricacion,
        estacionId: Number(estacionId),
      },
      data: updateData,
    });

    return NextResponse.json({
      success: true,
      message: 'Estado actualizado correctamente',
    });
  } catch (error) {
    logger.error('Error al actualizar estado:', error);
    return NextResponse.json(
      { success: false, message: 'Error al actualizar estado' },
      { status: 500 }
    );
  }
}
```

## 🔄 FLUJO DE DATOS COMPLETO

### 1. **Inicialización del Monitor Python**

```python
# 1. Cargar configuración guardada
config = cargar_configuracion()

# 2. Autenticar con SISPRO
token = await autenticar_sispro(config['username'], config['password'])
empresa_id = config['empresa_id']

# 3. Conectar a RS485
monitor_rs485 = MonitorRS485(port=config['rs485_port'], baudrate=config['rs485_baudrate'])
monitor_rs485.conectar()

# 4. Iniciar servicios
cache_manager = CacheManager()
websocket_server = WebSocketServer()
```

### 2. **Selección de Estación**

```python
# 1. Consultar estaciones disponibles
estaciones = await obtener_estaciones(empresa_id)

# 2. Mostrar lista y seleccionar
estacion_seleccionada = mostrar_menu_estaciones(estaciones)

# 3. Guardar configuración
guardar_configuracion({'estacion_id': estacion_seleccionada.id})

# 4. Consultar órdenes asignadas
ordenes = await obtener_ordenes_asignadas(empresa_id, estacion_seleccionada.id)
```

### 3. **Selección de Orden**

```python
# 1. Mostrar órdenes disponibles
orden_seleccionada = mostrar_menu_ordenes(ordenes)

# 2. Cambiar estado a ESPERANDO_UPC
await cambiar_estado_orden(empresa_id, orden_seleccionada.ordenFabricacion, 'ESPERANDO_UPC')

# 3. Activar escucha de código de barras
barcode_validator.activar_escucha()
```

### 4. **Validación UPC y Producción**

```python
# 1. Escanear código de barras
codigo_upc = await escanear_codigo_barras()

# 2. Validar contra orden seleccionada
if barcode_validator.validar_upc(codigo_upc, orden_seleccionada.ptUPC):
    # 3. Cambiar estado a PRODUCIENDO
    await cambiar_estado_orden(empresa_id, orden_seleccionada.ordenFabricacion, 'PRODUCIENDO')

    # 4. Activar escucha RS485
    monitor_rs485.activar_escucha()

    # 5. Procesar conteos en tiempo real
    async def procesar_conteo(conteo):
        await registrar_lectura(
            empresa_id,
            orden_seleccionada.ordenFabricacion,
            estacion_seleccionada.id,
            usuario_id,
            conteo,
            'RS485'
        )
```

## 📊 ESTRUCTURA DE CACHE

### SQLite (Persistencia)

```sql
CREATE TABLE estaciones (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    descripcion TEXT,
    estado TEXT,
    coordinador_supervisor TEXT,
    cuadrante TEXT,
    ultima_actualizacion TIMESTAMP
);

CREATE TABLE ordenes_fabricacion (
    id INTEGER PRIMARY KEY,
    orden_fabricacion TEXT,
    pt TEXT,
    cantidad_fabricar INTEGER,
    cantidad_pendiente INTEGER,
    avance REAL,
    pt_descripcion TEXT,
    pt_presentacion TEXT,
    pt_upc TEXT,
    estacion_id INTEGER,
    prioridad TEXT,
    is_closed BOOLEAN,
    ultima_actualizacion TIMESTAMP
);

CREATE TABLE lecturas_produccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_fabricacion TEXT,
    estacion_id INTEGER,
    usuario_id INTEGER,
    cantidad INTEGER,
    timestamp TIMESTAMP,
    fuente TEXT,
    validada BOOLEAN,
    sincronizada BOOLEAN DEFAULT FALSE
);
```

### Redis (Cache Rápido)

```python
# Estructura de claves Redis
estacion:{estacion_id} -> {
    "id": 1,
    "nombre": "Estación 001",
    "estado": "PRODUCIENDO",
    "orden_actual": "OF-001",
    "contador": 1250,
    "meta": 5000,
    "progreso": 25.0
}

orden:{orden_fabricacion} -> {
    "id": 1,
    "ordenFabricacion": "OF-001",
    "pt": "PT-001",
    "cantidadFabricar": 5000,
    "cantidadPendiente": 3750,
    "avance": 0.25,
    "ptUPC": "1234567890"
}
```

## 🚀 IMPLEMENTACIÓN RECOMENDADA

### 1. **Clase Principal del Monitor**

```python
class MonitorIndustrial:
    def __init__(self):
        self.config = ConfigManager()
        self.sispro = SISPROConnector()
        self.rs485 = MonitorRS485()
        self.barcode = BarcodeValidator()
        self.cache = CacheManager()
        self.websocket = WebSocketServer()
        self.estado = EstadoManager()

    async def inicializar(self):
        # Cargar configuración
        await self.config.cargar()

        # Autenticar con SISPRO
        await self.sispro.autenticar()

        # Conectar RS485
        self.rs485.conectar()

        # Iniciar servicios
        await self.websocket.iniciar()

    async def ejecutar(self):
        while True:
            await self.procesar_ciclo()
            await asyncio.sleep(0.1)
```

### 2. **Manejo de Estados**

```python
class EstadoManager:
    def __init__(self):
        self.estado_actual = "INACTIVO"
        self.estacion_actual = None
        self.orden_actual = None

    async def cambiar_estado(self, nuevo_estado):
        self.estado_actual = nuevo_estado
        await self.ejecutar_acciones_estado()

    async def ejecutar_acciones_estado(self):
        if self.estado_actual == "ESPERANDO_UPC":
            self.barcode.activar_escucha()
        elif self.estado_actual == "PRODUCIENDO":
            self.rs485.activar_escucha()
```

## 📊 RESUMEN DE APIS DISPONIBLES

### ✅ **APIs EXISTENTES (Pages Router)**

- **`/api/estacionesTrabajo`** - Obtener estaciones de trabajo
- **`/api/ordenesDeFabricacion/listarAsignadas`** - Listar órdenes asignadas
- **`/api/ordenesDeFabricacion/asignar`** - Asignar orden a estación
- **`/api/ordenesDeFabricacion/avance`** - Consultar avance de orden
- **`/api/lecturaUPC/registrar`** - Registrar lectura UPC
- **`/api/lecturaUPC/consultar`** - Consultar lecturas UPC
- **`/api/ordenesDeFabricacion/cambiarPrioridad`** - Cambiar prioridad
- **`/api/ordenesDeFabricacion/cerrarOrden`** - Cerrar orden
- **`/api/ordenesDeFabricacion/reabrirOrden`** - Reabrir orden

### 🔧 **APIs RECOMENDADAS (Crear)**

- **`/api/ordenesDeFabricacion/registrarLecturaRS485`** - Para conteos del Pico
- **`/api/ordenesDeFabricacion/actualizarEstado`** - Para estados de producción

### 🎯 **FLUJO DE INTEGRACIÓN COMPLETO**

1. **Monitor Python se conecta** → Autentica con SISPRO
2. **Consulta estaciones** → `/api/estacionesTrabajo`
3. **Selecciona estación** → Se guarda globalmente
4. **Consulta órdenes** → `/api/ordenesDeFabricacion/listarAsignadas`
5. **Selecciona orden** → Cambia estado a "ESPERANDO_UPC"
6. **Valida UPC** → `/api/lecturaUPC/registrar` (una sola vez)
7. **Activa RS485** → Escucha conteos del Pico
8. **Registra lecturas** → `/api/ordenesDeFabricacion/registrarLecturaRS485`
9. **Actualiza avance** → `/api/ordenesDeFabricacion/avance`
10. **Sincroniza datos** → Cada 5 minutos

Este mapeo proporciona una guía completa para implementar el monitor Python que se integre perfectamente con el sistema SISPRO existente, utilizando las APIs ya disponibles en Pages Router.
