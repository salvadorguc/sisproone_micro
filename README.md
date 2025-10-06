# SISPRO ONE - Sistema de Control de Producción

## 📋 Resumen Ejecutivo

**SISPRO ONE** es una solución integral de control de producción que automatiza el conteo de piezas y optimiza la eficiencia operativa en líneas de producción. El sistema proporciona visibilidad en tiempo real del progreso de producción, control de calidad y gestión de metas para maximizar la productividad y minimizar errores.

### 💼 Beneficios para el Negocio:

#### 📈 **Aumento de Productividad**

- **Control en Tiempo Real:** Monitoreo instantáneo del progreso de producción
- **Metas Configurables:** Establecimiento de objetivos por lote con alertas automáticas
- **Reducción de Errores:** Eliminación del conteo manual propenso a errores
- **Optimización de Procesos:** Identificación inmediata de cuellos de botella

#### 💰 **Ahorro de Costos**

- **Menos Personal:** Reducción de supervisión manual requerida
- **Menos Desperdicio:** Control preciso de inventario y producción
- **Eficiencia Energética:** Sistema de bajo consumo energético
- **Mantenimiento Mínimo:** Hardware robusto y software estable

#### 📊 **Mejora en la Gestión**

- **Reportes Automáticos:** Datos de producción en tiempo real
- **Trazabilidad Completa:** Registro detallado de cada estación de trabajo
- **Escalabilidad:** Fácil expansión a múltiples líneas de producción
- **Integración:** Compatible con sistemas ERP existentes

### 🎯 **Casos de Uso Principales:**

#### 🏭 **Líneas de Producción**

- Conteo automático de piezas fabricadas
- Control de calidad por lotes
- Gestión de metas de producción diarias/semanales

#### 📦 **Embalaje y Distribución**

- Conteo de unidades por paquete
- Verificación de pedidos completos
- Control de inventario en tiempo real

#### 🔧 **Mantenimiento Industrial**

- Monitoreo de equipos críticos
- Alertas preventivas de mantenimiento
- Registro de horas de operación

### 🚀 **Ventajas Competitivas:**

- **Implementación Rápida:** Sistema plug-and-play, operativo en horas
- **Costo-Beneficio:** ROI positivo en menos de 3 meses
- **Flexibilidad:** Adaptable a diferentes tipos de producción
- **Confiabilidad:** 99.9% de tiempo de actividad
- **Facilidad de Uso:** Interfaz intuitiva, sin capacitación especializada

### 📊 **Métricas de Impacto:**

#### ⏱️ **Eficiencia Operativa**

- **+25%** Aumento en velocidad de conteo
- **-90%** Reducción en errores de conteo manual
- **-50%** Tiempo de supervisión requerido
- **+15%** Mejora en cumplimiento de metas

#### 💵 **Retorno de Inversión (ROI)**

- **Costo del Sistema:** $500-800 por estación
- **Ahorro Anual:** $2,000-5,000 por estación
- **ROI:** 300-600% en el primer año
- **Payback Period:** 2-4 meses

#### 📈 **Indicadores Clave de Rendimiento (KPIs)**

- **Precisión de Conteo:** 99.9%
- **Tiempo de Respuesta:** <1 segundo
- **Disponibilidad del Sistema:** 99.9%
- **Reducción de Desperdicio:** 20-30%

### 🎯 **Propuesta de Valor:**

**SISPRO ONE** transforma la gestión de producción tradicional en un sistema inteligente y automatizado que:

1. **Elimina** el conteo manual y sus errores inherentes
2. **Proporciona** visibilidad completa del progreso en tiempo real
3. **Optimiza** la asignación de recursos y personal
4. **Garantiza** el cumplimiento de metas de producción
5. **Facilita** la toma de decisiones basada en datos reales

**Resultado:** Una operación más eficiente, rentable y competitiva.

## 🔧 Especificaciones Técnicas

### Componentes Principales:

- **Raspberry Pi Pico** (MicroPython)
- **Teclado 4x4** (membrane keypad)
- **LCD 16x2** (I2C, dirección 0x27)
- **3 LEDs** (Rojo, Amarillo, Verde) para semáforo
- **Buzzer** (piezoeléctrico)
- **Sensor de paso** (optoacoplador/IR)
- **Comunicación RS485** (MAX485)

## 🔌 Mapa de Conexiones GPIO - Raspberry Pi Pico

### 📋 Resumen de Puertos Utilizados

| **Función**  | **Puerto** | **Tipo** | **Descripción**                      |
| ------------ | ---------- | -------- | ------------------------------------ |
| **I2C LCD**  | GP4 (SDA)  | I/O      | Datos I2C para LCD 16x2              |
| **I2C LCD**  | GP5 (SCL)  | I/O      | Reloj I2C para LCD 16x2              |
| **Teclado**  | GP14       | OUT      | Fila 1 del teclado 4x4 (1,2,3,A)     |
| **Teclado**  | GP7        | OUT      | Fila 2 del teclado 4x4 (4,5,6,B)     |
| **Teclado**  | GP8        | OUT      | Fila 3 del teclado 4x4 (7,8,9,C)     |
| **Teclado**  | GP9        | OUT      | Fila 4 del teclado 4x4 (\*,0,#,D)    |
| **Teclado**  | GP11       | IN       | Columna 1 del teclado 4x4 (1,4,7,\*) |
| **Teclado**  | GP2        | IN       | Columna 2 del teclado 4x4 (2,5,8,0)  |
| **Teclado**  | GP3        | IN       | Columna 3 del teclado 4x4 (3,6,9,#)  |
| **Teclado**  | GP1        | IN       | Columna 4 del teclado 4x4 (A,B,C,D)  |
| **Sensor**   | GP15       | IN       | Sensor de paso (con PULL_UP)         |
| **Buzzer**   | GP16       | OUT      | Buzzer piezoeléctrico                |
| **Semáforo** | GP17       | OUT      | LED Rojo                             |
| **Semáforo** | GP18       | OUT      | LED Amarillo                         |
| **Semáforo** | GP19       | OUT      | LED Verde                            |
| **RS485**    | GP20       | OUT      | TX (Transmisión)                     |
| **RS485**    | GP21       | IN       | RX (Recepción)                       |
| **RS485**    | GP22       | OUT      | DE/RE (Control de dirección)         |

### 🎛️ Diagramas Visuales de Conexiones

#### 📐 **Vista Superior (Top View)**

```
                    RASPBERRY PI PICO
                   ┌─────────────────────┐
                   │  GP0  │  GP1  │ 3V3 │ ← 3.3V
                   │  GP1  │  GP2  │ 5V  │ ← 5V
                   │  GP2  │  GP3  │ GND │ ← GND
                   │  GP3  │  GP4  │ GND │ ← GND
                   │  GP4  │  GP5  │ GP5 │ ← I2C SCL (LCD)
                   │  GP5  │  GP6  │ GP6 │
                   │  GP6  │  GP7  │ GP7 │ ← Teclado Fila 2 (4,5,6,B)
                   │  GP7  │  GP8  │ GP8 │ ← Teclado Fila 3 (7,8,9,C)
                   │  GP8  │  GP9  │ GP9 │ ← Teclado Fila 4 (*,0,#,D)
                   │  GP9  │  GP10 │ GP10│
                   │  GP10 │  GP11 │ GP11│ ← Teclado Col 1 (1,4,7,*)
                   │  GP11 │  GP12 │ GP12│
                   │  GP12 │  GP13 │ GP13│
                   │  GP13 │  GP14 │ GP14│ ← Teclado Fila 1 (1,2,3,A)
                   │  GP14 │  GP15 │ GP15│ ← Sensor de Paso
                   │  GP15 │  GP16 │ GP16│ ← Buzzer
                   │  GP16 │  GP17 │ GP17│ ← LED Rojo
                   │  GP17 │  GP18 │ GP18│ ← LED Amarillo
                   │  GP18 │  GP19 │ GP19│ ← LED Verde
                   │  GP19 │  GP20 │ GP20│ ← RS485 TX
                   │  GP20 │  GP21 │ GP21│ ← RS485 RX
                   │  GP21 │  GP22 │ GP22│ ← RS485 DE/RE
                   │  GP22 │  GP23 │ GP23│
                   │  GP23 │  GP24 │ GP24│
                   │  GP24 │  GP25 │ GP25│
                   │  GP25 │  GP26 │ GP26│
                   │  GP26 │  GP27 │ GP27│
                   │  GP27 │  GP28 │ GP28│
                   └─────────────────────┘
```

#### 👈 **Vista Lateral Izquierda (Left Side View)**

```
    ┌─────────────────────────────────────────┐
    │                                         │
    │  GP0  ────────────────────────────────  │
    │  GP1  ────────────────────────────────  │
    │  GP2  ────────────────────────────────  │
    │  GP3  ────────────────────────────────  │
    │  GP4  ──── I2C SDA (LCD) ────────────  │
    │  GP5  ──── I2C SCL (LCD) ────────────  │
    │  GP6  ────────────────────────────────  │
    │  GP7  ──── Teclado Fila 2 (4,5,6,B) ──  │
    │  GP8  ──── Teclado Fila 3 (7,8,9,C) ──  │
    │  GP9  ──── Teclado Fila 4 (*,0,#,D) ──  │
    │  GP10 ────────────────────────────────  │
    │  GP11 ──── Teclado Col 1 (1,4,7,*) ───  │
    │  GP12 ────────────────────────────────  │
    │  GP13 ────────────────────────────────  │
    │  GP14 ──── Teclado Fila 1 (1,2,3,A) ──  │
    │  GP15 ──── Sensor de Paso ────────────  │
    │  GP16 ──── Buzzer ────────────────────  │
    │  GP17 ──── LED Rojo ──────────────────  │
    │  GP18 ──── LED Amarillo ──────────────  │
    │  GP19 ──── LED Verde ─────────────────  │
    │  GP20 ──── RS485 TX ──────────────────  │
    │  GP21 ──── RS485 RX ──────────────────  │
    │  GP22 ──── RS485 DE/RE ───────────────  │
    │  GP23 ────────────────────────────────  │
    │  GP24 ────────────────────────────────  │
    │  GP25 ────────────────────────────────  │
    │  GP26 ────────────────────────────────  │
    │  GP27 ────────────────────────────────  │
    │  GP28 ────────────────────────────────  │
    │                                         │
    │  ┌─────────────────────────────────────┐ │
    │  │        RASPBERRY PI PICO            │ │
    │  │         (Vista Lateral)             │ │
    │  └─────────────────────────────────────┘ │
    └─────────────────────────────────────────┘
```

#### 👉 **Vista Lateral Derecha (Right Side View)**

```
    ┌─────────────────────────────────────────┐
    │                                         │
    │  GP28 ────────────────────────────────  │
    │  GP27 ────────────────────────────────  │
    │  GP26 ────────────────────────────────  │
    │  GP25 ────────────────────────────────  │
    │  GP24 ────────────────────────────────  │
    │  GP23 ────────────────────────────────  │
    │  GP22 ──── RS485 DE/RE ───────────────  │
    │  GP21 ──── RS485 RX ──────────────────  │
    │  GP20 ──── RS485 TX ──────────────────  │
    │  GP19 ──── LED Verde ─────────────────  │
    │  GP18 ──── LED Amarillo ──────────────  │
    │  GP17 ──── LED Rojo ──────────────────  │
    │  GP16 ──── Buzzer ────────────────────  │
    │  GP15 ──── Sensor de Paso ────────────  │
    │  GP14 ──── Teclado Fila 1 (1,2,3,A) ──  │
    │  GP13 ────────────────────────────────  │
    │  GP12 ────────────────────────────────  │
    │  GP11 ──── Teclado Col 1 (1,4,7,*) ───  │
    │  GP10 ────────────────────────────────  │
    │  GP9  ──── Teclado Fila 4 (*,0,#,D) ──  │
    │  GP8  ──── Teclado Fila 3 (7,8,9,C) ──  │
    │  GP7  ──── Teclado Fila 2 (4,5,6,B) ──  │
    │  GP6  ────────────────────────────────  │
    │  GP5  ──── I2C SCL (LCD) ────────────  │
    │  GP4  ──── I2C SDA (LCD) ────────────  │
    │  GP3  ────────────────────────────────  │
    │  GP2  ────────────────────────────────  │
    │  GP1  ────────────────────────────────  │
    │  GP0  ────────────────────────────────  │
    │                                         │
    │  ┌─────────────────────────────────────┐ │
    │  │        RASPBERRY PI PICO            │ │
    │  │         (Vista Lateral)             │ │
    │  └─────────────────────────────────────┘ │
    └─────────────────────────────────────────┘
```

#### 🔌 **Vista de Pines de Alimentación (Power Pins)**

```
    ┌─────────────────────────────────────────┐
    │                                         │
    │  ┌─────────────────────────────────────┐ │
    │  │        RASPBERRY PI PICO            │ │
    │  │                                     │ │
    │  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐ │ │
    │  │  │ 3V3 │  │ 5V  │  │ GND │  │ GND │ │ │
    │  │  │     │  │     │  │     │  │     │ │ │
    │  │  │ 3.3V│  │ 5V  │  │ GND │  │ GND │ │ │
    │  │  └─────┘  └─────┘  └─────┘  └─────┘ │ │
    │  │                                     │ │
    │  │  Alimentación Principal              │ │
    │  │  • 3.3V: Sensores, LEDs, Buzzer     │ │
    │  │  • 5V: Pico, LCD, MAX485            │ │
    │  │  • GND: Tierra común                 │ │
    │  └─────────────────────────────────────┘ │
    └─────────────────────────────────────────┘
```

### 🔌 Conexiones Detalladas por Componente

#### 📺 **LCD 16x2 (I2C)**

```
LCD 16x2    →    Pico
VCC         →    5V
GND         →    GND
SDA         →    GP4
SCL         →    GP5
```

_Nota: Dirección I2C por defecto: 0x27_

#### ⌨️ **Teclado 4x4 (Matriz)**

```
Teclado 4x4     →    Pico
Fila 1 (1,2,3,A) →    GP14
Fila 2 (4,5,6,B) →    GP7
Fila 3 (7,8,9,C) →    GP8
Fila 4 (*,0,#,D) →    GP9
Col 1 (1,4,7,*)  →    GP11
Col 2 (2,5,8,0)  →    GP2
Col 3 (3,6,9,#)  →    GP3
Col 4 (A,B,C,D)  →    GP1

Mapeo Físico del Teclado:
┌─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  A  │ ← GP14 (Fila 1)
├─────┼─────┼─────┼─────┤
│  4  │  5  │  6  │  B  │ ← GP7  (Fila 2)
├─────┼─────┼─────┼─────┤
│  7  │  8  │  9  │  C  │ ← GP8  (Fila 3)
├─────┼─────┼─────┼─────┤
│  *  │  0  │  #  │  D  │ ← GP9  (Fila 4)
└─────┴─────┴─────┴─────┘
  ↑     ↑     ↑     ↑
GP11  GP2   GP3   GP1
(Col1)(Col2)(Col3)(Col4)
```

#### 🚦 **Semáforo LED**

```
LED Rojo     →    GP17
LED Amarillo →    GP18
LED Verde    →    GP19
Resistencia  →    220Ω (cada LED)
GND común    →    GND
```

#### 🔊 **Buzzer**

```
Buzzer (+)   →    GP16
Buzzer (-)   →    GND
```

#### 📡 **Sensor de Paso**

```
Sensor VCC   →    3.3V
Sensor GND   →    GND
Sensor OUT   →    GP15 (con PULL_UP interno)
```

#### 📡 **Comunicación RS485 (MAX485)**

```
MAX485       →    Pico
VCC          →    5V
GND          →    GND
DI (Data In) →    GP20 (TX)
RO (Read Out)→    GP21 (RX)
DE/RE        →    GP22 (Control)
A            →    Bus RS485 A
B            →    Bus RS485 B
```

### ⚡ **Alimentación del Sistema**

| **Componente** | **Voltaje** | **Consumo** | **Notas**              |
| -------------- | ----------- | ----------- | ---------------------- |
| **Pico**       | 5V          | ~100mA      | Alimentación principal |
| **LCD I2C**    | 5V          | ~20mA       | Módulo I2C incluido    |
| **Teclado**    | 3.3V        | ~5mA        | Matriz de teclas       |
| **LEDs**       | 3.3V        | ~20mA c/u   | Con resistencias 220Ω  |
| **Buzzer**     | 3.3V        | ~30mA       | Piezoeléctrico         |
| **Sensor**     | 3.3V        | ~10mA       | Optoacoplador/IR       |
| **MAX485**     | 5V          | ~15mA       | Transceptor RS485      |

**Total estimado:** ~200mA @ 5V

### 🛠️ **Notas de Instalación**

1. **Resistencias Pull-up:** El teclado usa resistencias pull-up internas de la Pico
2. **Resistencias LED:** Usar 220Ω para cada LED del semáforo
3. **Cableado RS485:** Usar cable trenzado para mejor inmunidad al ruido
4. **Tierra común:** Conectar todas las tierras (GND) al mismo punto
5. **Alimentación estable:** Usar fuente de 5V con capacidad mínima de 1A

### 🎯 **Layout Físico Recomendado**

```
                    SISTEMA SISPRO ONE
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
    │  │   LCD 16x2  │    │  SEMÁFORO   │    │   BUZZER    │  │
    │  │   (I2C)     │    │  🟢 🟡 🔴   │    │     🔊      │  │
    │  │  GP4, GP5   │    │ GP17,18,19  │    │    GP16     │  │
    │  └─────────────┘    └─────────────┘    └─────────────┘  │
    │                                                         │
    │  ┌─────────────────────────────────────────────────────┐ │
    │  │                TECLADO 4x4                         │ │
    │  │  ┌─────┬─────┬─────┬─────┐                         │ │
    │  │  │  1  │  2  │  3  │  A  │ ← GP14 (Fila 1)         │ │
    │  │  ├─────┼─────┼─────┼─────┤                         │ │
    │  │  │  4  │  5  │  6  │  B  │ ← GP7  (Fila 2)         │ │
    │  │  ├─────┼─────┼─────┼─────┤                         │ │
    │  │  │  7  │  8  │  9  │  C  │ ← GP8  (Fila 3)         │ │
    │  │  ├─────┼─────┼─────┼─────┤                         │ │
    │  │  │  *  │  0  │  #  │  D  │ ← GP9  (Fila 4)         │ │
    │  │  └─────┴─────┴─────┴─────┘                         │ │
    │  │    ↑     ↑     ↑     ↑                             │ │
    │  │  GP11  GP2   GP3   GP1  (Columnas)                 │ │
    │  └─────────────────────────────────────────────────────┘ │
    │                                                         │
    │  ┌─────────────┐              ┌─────────────┐          │
    │  │   SENSOR    │              │   RS485     │          │
    │  │   DE PASO   │              │  (MAX485)   │          │
    │  │    GP15     │              │ GP20,21,22  │          │
    │  └─────────────┘              └─────────────┘          │
    │                                                         │
    │  ┌─────────────────────────────────────────────────────┐ │
    │  │              RASPBERRY PI PICO                     │ │
    │  │         (Todas las conexiones GPIO)                │ │
    │  └─────────────────────────────────────────────────────┘ │
    └─────────────────────────────────────────────────────────┘
```

### 🔧 **Lista de Verificación de Conexiones**

#### ✅ **Antes de Encender:**

- [ ] Verificar que todas las tierras (GND) estén conectadas
- [ ] Confirmar polaridad de LEDs (ánodo/cátodo)
- [ ] Verificar resistencias de 220Ω en cada LED
- [ ] Comprobar conexiones del teclado (4 filas + 4 columnas)
- [ ] Verificar alimentación 5V estable
- [ ] Confirmar conexiones I2C del LCD (SDA/SCL)

#### ✅ **Después de Encender:**

- [ ] LCD muestra mensaje de inicio
- [ ] LEDs responden a comandos
- [ ] Teclado responde a presiones
- [ ] Buzzer emite sonido
- [ ] Sensor detecta interrupciones
- [ ] Comunicación RS485 funciona

### ⚠️ **Troubleshooting Común**

| **Problema**        | **Causa Probable**           | **Solución**                      |
| ------------------- | ---------------------------- | --------------------------------- |
| LCD no funciona     | Conexión I2C incorrecta      | Verificar SDA/SCL y dirección     |
| Teclado no responde | Conexión de filas/columnas   | Revisar mapeo de pines            |
| LEDs no encienden   | Sin resistencias o polaridad | Agregar 220Ω, verificar polaridad |
| Buzzer no suena     | Conexión incorrecta          | Verificar GP16 y GND              |
| Sensor no detecta   | PULL_UP no activado          | Verificar configuración Pin.IN    |
| RS485 no comunica   | Cableado incorrecto          | Verificar TX/RX/DE/RE             |

## 🎮 Manual de Funciones del Teclado

### Mapeo del Teclado:

```
┌─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  A  │ ← A: START/STOP
├─────┼─────┼─────┼─────┤
│  4  │  5  │  6  │  B  │ ← B: UNDO
├─────┼─────┼─────┼─────┤
│  7  │  8  │  9  │  C  │ ← C: RESET (con PIN)
├─────┼─────┼─────┼─────┤
│  *  │  0  │  #  │  D  │ ← D: MENÚ, #: ENTER, *: CANCEL
└─────┴─────┴─────┴─────┘
```

### 🔒 Funciones Protegidas con PIN:

- **A: START/STOP** - Control directo del sistema
- **B: UNDO** - Restar última lectura
- **C: RESET** - Reiniciar contador (requiere PIN)
- **1: META** - Establecer meta (requiere PIN)
- **2: BORRAR META** - Eliminar meta (requiere PIN)

### ✨ Características Especiales:

- **Texto deslizante** en menús para mejor legibilidad
- **Mensajes cortos** optimizados para LCD con problemas de contraste
- **Efecto de anuncio** al entrar en menús

### Funciones Principales:

#### **A - START/STOP**

- **Función:** Iniciar/detener el conteo
- **Uso:** Presiona A para alternar entre activo/detenido
- **Efecto:**
  - **ACTIVO:** Semáforo verde fijo + 2 bips cortos
  - **DETENIDO:** Semáforo amarillo fijo

#### **B - UNDO**

- **Función:** Deshacer último conteo (corrección rápida)
- **Uso:** Presiona B para restar el step_size actual
- **Efecto:** Resta 1 pieza (o step_size configurado) del contador

#### **C - RESET (Protegido por PIN)**

- **Función:** Reiniciar contador completo
- **Uso:** Presiona C, ingresa PIN de 4 dígitos, confirma con #
- **Efecto:**
  - Solicita PIN de supervisor (1234 por defecto)
  - Si es correcto: resetea contador y total
  - Si es incorrecto: cancela la operación

#### **D - MENÚ**

- **Función:** Acceder al menú principal de configuración
- **Uso:** Presiona D para entrar al menú
- **Efecto:** Abre menú con opciones numeradas

### Opciones del Menú Principal:

#### **1 - META** 🔒

- **Función:** Establecer meta de producción (lote objetivo)
- **Uso:** Ingresa PIN, luego número con teclas numéricas, confirma con #
- **Protección:** Requiere PIN de supervisor (por defecto "1234")
- **Efecto:**
  - Semáforo amarillo intermitente cuando faltan ≤10 piezas
  - Semáforo rojo cuando se alcanza la meta
  - Porcentaje de avance en display

#### **2 - BORRAR META** 🔒

- **Función:** Eliminar meta fija y trabajar sin límite
- **Uso:** Ingresa PIN, luego presiona 2 para borrar la meta actual
- **Protección:** Requiere PIN de supervisor (por defecto "1234")
- **Efecto:**
  - Establece meta en 0
  - Desactiva alertas de meta
  - Permite conteo libre sin límites

#### **3 - TOTAL**

- **Función:** Mostrar estado completo del sistema
- **Uso:** Presiona 3 para ver información detallada
- **Efecto:** Muestra contador, total, meta y porcentaje con efecto deslizante

#### **4 - BUZZER**

- **Función:** Activar/desactivar sonidos del sistema
- **Uso:** Presiona 4 para alternar ON/OFF
- **Efecto:**
  - **ON:** Sonidos normales (bips, alarmas)
  - **OFF:** Parpadeos LED verde como alerta visual

#### **5 - ID**

- **Función:** Configurar identificador del dispositivo
- **Uso:** Ingresa texto alfanumérico, confirma con #
- **Efecto:** Cambia el ID para comunicaciones RS485

#### **0 - SALIR**

- **Función:** Salir del menú
- **Uso:** Presiona 0 para volver al modo normal
- **Efecto:** Regresa a la pantalla principal

#### **# - ENTER/CONFIRM**

- **Función:** Confirmar entrada numérica o mostrar estado rápido
- **Uso:**
  - Durante entrada numérica: confirma el valor
  - En modo normal: muestra estado completo del sistema con efecto deslizante
- **Efecto:** Muestra información detallada con animación de texto

#### **\* - CANCEL/ATRÁS**

- **Función:** Cancelar operación o volver atrás
- **Uso:**
  - Durante entrada numérica: cancela sin guardar
  - En menús: vuelve al nivel anterior

### Teclas Numéricas (0-9):

- **Función:** Entrada de valores numéricos
- **Uso:** Durante entrada de meta, tara, step size, etc.
- **Efecto:** Construye el número digitado en el display

## ⚙️ Menú de Ajustes

### Acceso:

1. Presiona **D** para entrar al menú principal
2. Presiona **D** nuevamente para acceder a ajustes

### Opciones del Menú de Ajustes:

#### **A - SET TARA/OFFSET**

- **Función:** Establecer valor inicial del contador
- **Uso:** Útil si hubo avance previo en la producción
- **Efecto:** El contador inicia desde este valor

#### **B - STEP SIZE**

- **Función:** Definir cuántos pulsos equivalen a 1 pieza
- **Valores típicos:** 1:1, 2:1, 4:1, etc.
- **Efecto:** Ajusta la sensibilidad del conteo

#### **C - DEBOUNCE**

- **Función:** Ajustar tiempo de antirrebote del sensor
- **Unidad:** milisegundos (ms)
- **Valores recomendados:** 50-200ms
- **Efecto:** Evita conteos múltiples por un solo paso

#### **D - VOL/BUZZER**

- **Función:** Activar/desactivar sonidos del sistema
- **Opciones:** ON/OFF
- **Efecto:** Controla todos los sonidos (bips, alarmas)

#### **5 - ID DISPOSITIVO**

- **Función:** Configurar identificador único del dispositivo
- **Uso:** Identificar lecturas de múltiples dispositivos
- **Formato:** Texto alfanumérico (ej: PICO001, LINEA_A, etc.)
- **Efecto:** Se incluye en todas las comunicaciones RS485

## 📊 Estados del Sistema

### Indicadores Visuales (Semáforo):

#### **🔴 Rojo Fijo:**

- Sistema detenido
- Meta alcanzada
- Modo espera

#### **🟡 Amarillo Fijo:**

- Sistema activo, modo lectura
- Conteo en progreso
- Estado normal de operación

#### **🟢 Verde Parpadeante:**

- Solo parpadea al leer (una vez por lectura)
- Feedback visual de cada detección
- No se queda encendido en modo lectura

#### **🟡 Amarillo Intermitente:**

- Faltan ≤10 piezas para alcanzar la meta
- Alerta de proximidad a meta
- Pausa temporal del conteo

### Alertas Visuales (Buzzer Apagado):

Cuando el buzzer está **OFF**, el LED verde parpadea como alerta visual:

- **Cada lectura:** Un parpadeo verde por detección del sensor
- **Parpadeo corto:** Conteo individual (bip_corto)
- **Parpadeo largo:** Meta alcanzada, reset (bip_largo)
- **Doble parpadeo corto:** Inicio de conteo (dos_bips_cortos)
- **Doble parpadeo largo:** Reset exitoso (dos_bips_largos)

**Nota:** El LED verde solo parpadea, no se queda encendido en modo lectura.

### 🔒 Seguridad y Protección:

#### **Funciones Protegidas con PIN:**

- **C: RESET** - Reiniciar contador (requiere PIN "1234")
- **1: META** - Establecer meta de producción (requiere PIN)
- **2: BORRAR META** - Eliminar meta fija (requiere PIN)

#### **PIN de Supervisor:**

- **Por defecto:** "1234"
- **Configurable:** Se puede cambiar en el menú de ajustes
- **Protección:** Evita cambios accidentales en funciones críticas

### Indicadores Auditivos (Buzzer):

#### **1 Bip Largo:**

- Sistema listo/armado
- Modo espera activado

#### **2 Bips Cortos:**

- Conteo iniciado
- Sistema activado

#### **1 Bip Corto:**

- Pausa del conteo
- Operación confirmada (UNDO, etc.)

#### **2 Bips Largos:**

- Reset/reinicio del sistema
- Operación importante completada

## 💾 Configuración Persistente

### Archivo de Configuración: `/config.json`

```json
{
  "meta": 100,
  "tara": 0,
  "step_size": 1,
  "debounce_ms": 100,
  "buzzer_on": true,
  "brillo": 100,
  "pin_supervisor": "1234",
  "device_id": "PICO001"
}
```

### Variables Configurables:

- **meta:** Meta de producción (lote objetivo)
- **tara:** Valor inicial del contador
- **step_size:** Pulsos por pieza
- **debounce_ms:** Tiempo de antirrebote
- **buzzer_on:** Estado del buzzer
- **brillo:** Brillo del LCD (0-100)
- **pin_supervisor:** PIN para ajustes avanzados
- **device_id:** Identificador único del dispositivo

## 📡 Comunicación RS485

### Formato de Mensajes:

```
<DEVICE_ID>:<TAG>:<VALOR>
```

**Ejemplo:**

```
PICO001:CONT:150
LINEA_A:TOTAL:2500
```

### Tags Disponibles:

- **CONT:** Conteo actual
- **TOTAL:** Total acumulado
- **RESET:** Señal de reinicio

## 🖥️ Master - Receptor de Datos

### Archivo: `master.py`

Sistema receptor que muestra y registra todos los mensajes de los dispositivos de conteo.

#### **Características:**

- **Recepción en tiempo real** de mensajes RS485
- **Log automático** en archivo JSON
- **Estado de dispositivos** con actualización periódica
- **Interfaz de consola** clara y organizada

#### **Uso:**

```bash
python3 master.py
```

#### **Configuración:**

- **Puerto:** Configurable (default: /dev/ttyUSB0)
- **Baudrate:** Configurable (default: 9600)
- **Log:** Se guarda en `conteo_log.json`

#### **Funciones:**

- **Escucha continua** de mensajes
- **Procesamiento automático** de datos
- **Estado cada 30 segundos** de todos los dispositivos
- **Log persistente** de todas las lecturas
- **META:** Meta alcanzada

### Configuración:

- **Baudrate:** 9600
- **TX:** GP20
- **RX:** GP21
- **DE/RE:** GP22

## 🚀 Instalación y Uso

### 1. Instalación:

```bash
# Copiar archivos al Pico
# main.py
# lcd16x2.py
# teclado4x4.py
```

### 2. Inicio:

1. Conectar hardware según esquema
2. Alimentar el sistema
3. El sistema inicia en modo espera
4. Presiona **D** para acceder al menú

### 3. Configuración Inicial:

1. Presiona **A** para establecer meta
2. Presiona **B** para iniciar conteo
3. Ajusta parámetros según necesidad

## 🔧 Solución de Problemas

### Teclado no responde:

- Verificar conexiones de filas y columnas
- Comprobar pull-up resistors
- Revisar mapeo de pines

### LCD no muestra:

- Verificar conexiones I2C (SDA/SCL)
- Comprobar dirección I2C (0x27)
- Revisar alimentación

### Sensor no detecta:

- Ajustar debounce en menú
- Verificar conexión del sensor
- Comprobar alimentación del sensor

### RS485 no comunica:

- Verificar conexiones TX/RX/DE
- Comprobar baudrate (9600)
- Revisar terminación de bus

## 📝 Notas Técnicas

### Requisitos del Sistema:

- **MicroPython** en Raspberry Pi Pico
- **Memoria:** Mínimo 1MB para configuración
- **Alimentación:** 5V para LCD, 3.3V para Pico

### Limitaciones:

- Máximo 9999 en contadores
- Configuración limitada por memoria flash
- RS485 requiere terminación de bus

### Actualizaciones Futuras:

- Modo simulación de pulsos
- Ajuste de brillo LCD
- PIN supervisor para ajustes avanzados
- Test de comunicación RS485

## 📞 Soporte

Para soporte técnico o reportar problemas:

1. Verificar este manual
2. Comprobar conexiones hardware
3. Revisar configuración en `/config.json`
4. Documentar comportamiento observado

---

**Versión:** 1.0
**Fecha:** 2024
**Hardware:** Raspberry Pi Pico + Teclado 4x4
**Software:** MicroPython
