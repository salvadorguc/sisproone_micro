# Test Components - Banco de Pruebas

Este directorio contiene los tests individuales para cada componente del sistema industrial antes de su integracion al proyecto principal.

## Metodologia de Pruebas

Cada componente debe ser probado individualmente antes de integrarse al proyecto principal. Esto asegura que:

1. El componente funciona correctamente por separado
2. Se identifican problemas de hardware antes de la integracion
3. Se valida la configuracion de pines y comunicaciones
4. Se establecen los parametros optimos de funcionamiento

## Componentes Disponibles

### Componentes Actuales

- **test_leds.py** - Test de LEDs de estado
- **test_teclado.py** - Test de teclado matricial 4x4
- **test_pantalla.py** - Test de pantalla LCD 16x2
- **test_buzzer.py** - Test de buzzer/piezo
- **test_rs485.py** - Test de comunicacion RS485

### Componentes Futuros

- **test_ds3231.py** - Test de reloj de tiempo real DS3231
- **test_microsd.py** - Test de lector de tarjeta microSD

## Como Usar

1. Conectar solo el componente a probar
2. Ejecutar el test correspondiente
3. Verificar que todas las pruebas pasen
4. Una vez validado, integrar al proyecto principal

## Hardware Requerido

### Raspberry Pi Pico

- MicroPython instalado
- Componentes de hardware correspondientes
- Conexiones segun especificaciones de cada test

### Pines Comunes (ajustar segun necesidad)

- I2C: SCL=Pin(1), SDA=Pin(0)
- SPI: SCK=Pin(2), MOSI=Pin(3), MISO=Pin(4)
- UART: TX=Pin(0), RX=Pin(1)
- LEDs: Pines 2, 3, 4, 5
- Teclado: Filas 10, 11, 12, 13; Columnas 6, 7, 8, 9
- Buzzer: Pin 15
- DE/RE RS485: Pin 2

## Ejemplo de Uso

```python
# Ejecutar test de LEDs
python test_leds.py

# Ejecutar test de teclado
python test_teclado.py

# Ejecutar test de pantalla
python test_pantalla.py
```

## Notas Importantes

- Todos los tests usan solo caracteres ASCII
- No se usan emojis ni caracteres especiales
- Los pines pueden necesitar ajuste segun el hardware real
- Cada test incluye menu interactivo para diferentes opciones
- Los tests son independientes entre si

## Integracion

Una vez que todos los componentes individuales pasen sus tests:

1. Verificar compatibilidad de pines
2. Crear version integrada del sistema
3. Probar interacciones entre componentes
4. Validar funcionamiento completo del sistema

## Troubleshooting

Si un test falla:

1. Verificar conexiones de hardware
2. Confirmar configuracion de pines
3. Revisar alimentacion del componente
4. Verificar que el componente no este danado
5. Consultar documentacion del componente
