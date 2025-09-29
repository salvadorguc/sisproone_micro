from machine import Pin, I2C, UART
import time
import json
from lcd16x2 import LCD1602

# --- CONFIGURACIÓN RS485 ---
BAUDRATE = 9600
uart = UART(1, baudrate=BAUDRATE, tx=Pin(20), rx=Pin(21))
dere = Pin(22, Pin.OUT)
dere.value(0)  # Iniciar en RX

# --- LCD ---
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
lcd = LCD1602(i2c, addr=0x27)

# --- LEDs Semáforo ---
led_rojo = Pin(17, Pin.OUT)
led_amarillo = Pin(18, Pin.OUT)
led_verde = Pin(19, Pin.OUT)

# --- Buzzer ---
buzzer = Pin(16, Pin.OUT)

# --- Sensor de paso ---
sensor = Pin(15, Pin.IN, Pin.PULL_UP)

# --- Teclado 4x4 ---
class Teclado4x4:
    def __init__(self):
        # Pines ordenados lógicamente
        self.filas = [Pin(14, Pin.OUT), Pin(7, Pin.OUT), Pin(8, Pin.OUT), Pin(9, Pin.OUT)]
        self.cols = [Pin(11, Pin.IN, Pin.PULL_UP), Pin(2, Pin.IN, Pin.PULL_UP),
                    Pin(3, Pin.IN, Pin.PULL_UP), Pin(1, Pin.IN, Pin.PULL_UP)]

        # Teclado estándar
        self.teclado = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]

        # Inicializar filas
        for f in self.filas:
            f.value(1)

    def leer_tecla(self):
        """Lee una tecla presionada y retorna el carácter"""
        for i, fila in enumerate(self.filas):
            fila.value(0)  # Activar fila
            time.sleep_ms(10)

            # Leer columnas
            for j, col in enumerate(self.cols):
                if col.value() == 0:  # Tecla presionada
                    fila.value(1)  # Desactivar fila
                    time.sleep_ms(200)  # Debounce
                    return self.teclado[i][j]

            fila.value(1)  # Desactivar fila
            time.sleep_ms(10)

        return None

# --- Variables del Sistema ---
contador = 0
total = 0
activo = False
meta = 0
tara = 0
step_size = 1
debounce_ms = 100
buzzer_on = True
brillo = 100
pin_supervisor = "1234"
device_id = "PIC"
modo_menu = False
entrada_numero = ""
_last_ms = 0
_estado_anterior = None
log_contador = 0  # Contador total que no se reinicia

# --- Instancias ---
teclado = Teclado4x4()

# --- Funciones de Utilidad ---
def actualizar_lcd(msg1, msg2):
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.print(msg1)
    lcd.set_cursor(0, 1)
    lcd.print(msg2)

def mostrar_texto_deslizante(texto, fila=0, delay=200):
    """Muestra texto deslizante en el LCD"""
    if len(texto) <= 16:
        lcd.set_cursor(0, fila)
        lcd.print(texto)
        return

    # Texto con espacios para crear efecto de deslizamiento
    texto_completo = " " * 16 + texto + " " * 16

    for i in range(len(texto_completo) - 15):
        lcd.set_cursor(0, fila)
        lcd.print(texto_completo[i:i+16])
        time.sleep_ms(delay)

        # Verificar si se presionó una tecla para salir
        tecla = teclado.leer_tecla()
        if tecla:
            return tecla

    return None

def actualizar_semaforo(rojo, amarillo, verde):
    led_rojo.value(rojo)
    led_amarillo.value(amarillo)
    led_verde.value(verde)

def bip_largo():
    """Un bip largo o parpadeo LED verde si buzzer apagado"""
    if buzzer_on:
        buzzer.value(1)
        time.sleep_ms(500)
        buzzer.value(0)
    else:
        # Parpadeo LED verde como alerta visual
        led_verde.value(0)  # Apagar
        time.sleep_ms(100)
        led_verde.value(1)  # Encender
        time.sleep_ms(500)
        led_verde.value(0)  # Apagar

def bip_corto():
    """Un bip corto o parpadeo LED verde si buzzer apagado"""
    if buzzer_on:
        buzzer.value(1)
        time.sleep_ms(100)
        buzzer.value(0)
    else:
        # Parpadeo LED verde como alerta visual
        led_verde.value(0)  # Apagar
        time.sleep_ms(50)
        led_verde.value(1)  # Encender
        time.sleep_ms(100)
        led_verde.value(0)  # Apagar

def dos_bips_cortos():
    """Dos bips cortos o parpadeos LED verde si buzzer apagado"""
    if buzzer_on:
        for _ in range(2):
            bip_corto()
            time.sleep_ms(50)
    else:
        # Parpadeos LED verde como alerta visual
        for _ in range(2):
            led_verde.value(0)  # Apagar
            time.sleep_ms(50)
            led_verde.value(1)  # Encender
            time.sleep_ms(100)
            led_verde.value(0)  # Apagar
            time.sleep_ms(50)

def dos_bips_largos():
    """Dos bips largos o parpadeos LED verde si buzzer apagado"""
    if buzzer_on:
        for _ in range(2):
            bip_largo()
            time.sleep_ms(100)
    else:
        # Parpadeos LED verde como alerta visual
        for _ in range(2):
            led_verde.value(0)  # Apagar
            time.sleep_ms(100)
            led_verde.value(1)  # Encender
            time.sleep_ms(500)
            led_verde.value(0)  # Apagar
            time.sleep_ms(100)

def send_rs485(tag: str, value: int):
    """Función para enviar datos al bus RS485"""
    message = f"{device_id}:{tag}:{value}\n"
    data_to_send = message.encode('utf-8')
    dere.value(1)
    uart.write(data_to_send)
    time.sleep_ms(50)
    dere.value(0)

def guardar_config():
    """Guarda la configuración en flash"""
    config = {
        "meta": meta,
        "tara": tara,
        "step_size": step_size,
        "debounce_ms": debounce_ms,
        "buzzer_on": buzzer_on,
        "brillo": brillo,
        "pin_supervisor": pin_supervisor,
        "device_id": device_id,
        "log_contador": log_contador
    }
    try:
        with open("/config.json", "w") as f:
            json.dump(config, f)
    except:
        pass

def cargar_config():
    """Carga la configuración desde flash"""
    global meta, tara, step_size, debounce_ms, buzzer_on, brillo, pin_supervisor, device_id, log_contador
    try:
        with open("/config.json", "r") as f:
            config = json.load(f)
            meta = config.get("meta", 0)
            tara = config.get("tara", 0)
            step_size = config.get("step_size", 1)
            debounce_ms = config.get("debounce_ms", 100)
            buzzer_on = config.get("buzzer_on", True)
            brillo = config.get("brillo", 100)
            pin_supervisor = config.get("pin_supervisor", "1234")
            device_id = config.get("device_id", "PIC")
            log_contador = config.get("log_contador", 0)
    except:
        pass

# --- Funciones del Sistema ---
def modo_espera():
    """Modo Espera - Armado de Sistema"""
    actualizar_semaforo(0, 0, 1)  # Verde
    time.sleep_ms(200)
    actualizar_semaforo(0, 1, 0)  # Amarillo
    time.sleep_ms(200)
    actualizar_semaforo(1, 0, 0)  # Rojo
    time.sleep_ms(200)
    actualizar_semaforo(0, 1, 0)  # Amarillo Fijo
    bip_largo()

def iniciar_conteo():
    """Control de Conteo - Inicio de Lectura"""
    actualizar_semaforo(0, 1, 0)  # Amarillo - Modo lectura
    if buzzer_on:
        dos_bips_cortos()
    else:
        # Parpadeos LED verde como alerta visual
        for _ in range(2):
            led_verde.value(0)  # Apagar
            time.sleep_ms(50)
            led_verde.value(1)  # Encender
            time.sleep_ms(100)
            led_verde.value(0)  # Apagar
            time.sleep_ms(50)

def pausar_conteo():
    """Control Temporal - Pausa de Lectura"""
    for _ in range(10):
        actualizar_semaforo(0, 1, 0)
        time.sleep_ms(100)
        actualizar_semaforo(0, 0, 0)
        time.sleep_ms(100)
    bip_corto()

def mostrar_total():
    """Consulta de Dato - Mostrar Conteo Total"""
    actualizar_semaforo(1, 0, 0)  # Rojo Fijo
    bip_corto()

def reiniciar_conteo():
    """Borrar Conteo - Reiniciar a Cero"""
    actualizar_semaforo(1, 0, 0)  # Rojo Fijo
    time.sleep_ms(1000)
    actualizar_semaforo(0, 0, 1)  # Verde Fijo
    time.sleep_ms(1000)
    dos_bips_largos()

def mostrar_estado_rapido():
    """Muestra estado rápido del sistema con efecto deslizante"""
    estado = "ACTIVO" if activo else "PAUSA" if contador > 0 else "DETENIDO"
    porcentaje = int((contador / meta * 100)) if meta > 0 else 0

    # Mostrar información con efecto deslizante
    lcd.clear()
    mostrar_texto_deslizante(f"ESTADO: {estado}", 0, 150)
    time.sleep_ms(300)

    if meta > 0:
        mostrar_texto_deslizante(f"CONT: {contador}/{meta}", 0, 150)
        time.sleep_ms(300)
        mostrar_texto_deslizante(f"TOTAL: {total} - {porcentaje}%", 0, 150)
        time.sleep_ms(300)
        # Mostrar resumen final con meta
        actualizar_lcd(f"{estado} {contador}/{meta}", f"TOTAL:{total} {porcentaje}%")
    else:
        mostrar_texto_deslizante(f"CONT: {contador} (Libre)", 0, 150)
        time.sleep_ms(300)
        mostrar_texto_deslizante(f"TOTAL: {total}", 0, 150)
        time.sleep_ms(300)
        # Mostrar resumen final sin meta
        actualizar_lcd(f"{estado} {contador} (Libre)", f"TOTAL:{total}")

# --- Funciones del Teclado ---
def entrada_numerica(titulo, valor_actual=0):
    """Función para entrada numérica con el teclado"""
    global entrada_numero
    entrada_numero = str(valor_actual)
    actualizar_lcd(titulo, entrada_numero)

    while True:
        tecla = teclado.leer_tecla()
        if tecla:
            if tecla.isdigit():
                entrada_numero += tecla
                actualizar_lcd(titulo, entrada_numero)
            elif tecla == '*':  # CANCEL
                return None
            elif tecla == '#':  # ENTER
                try:
                    return int(entrada_numero)
                except:
                    return None
            elif tecla == 'C':  # UNDO/BACKSPACE
                if entrada_numero:
                    entrada_numero = entrada_numero[:-1]
                    actualizar_lcd(titulo, entrada_numero)
        time.sleep_ms(50)

def entrada_texto(titulo, valor_actual=""):
    """Función para entrada de texto con el teclado"""
    global entrada_numero
    entrada_numero = str(valor_actual)
    actualizar_lcd(titulo, entrada_numero)

    while True:
        tecla = teclado.leer_tecla()
        if tecla:
            if tecla.isdigit() or tecla.isalpha():
                if len(entrada_numero) < 8:  # Máximo 8 caracteres
                    entrada_numero += tecla
                    actualizar_lcd(titulo, entrada_numero)
                else:
                    # Mostrar mensaje de límite alcanzado
                    actualizar_lcd("MAX 8 CHARS", entrada_numero)
                    time.sleep_ms(1000)
                    actualizar_lcd(titulo, entrada_numero)
            elif tecla == '*':  # BORRAR CARACTER (solo si hay más de 3 caracteres)
                if len(entrada_numero) > 3:
                    entrada_numero = entrada_numero[:-1]
                    actualizar_lcd(titulo, entrada_numero)
            elif tecla == '#':  # GUARDAR
                return entrada_numero if entrada_numero else None
        time.sleep_ms(50)

def verificar_pin():
    """Función para verificar PIN de 4 dígitos"""
    global entrada_numero
    entrada_numero = ""
    actualizar_lcd("PIN (4 digitos):", "****")

    while True:
        tecla = teclado.leer_tecla()
        if tecla:
            if tecla.isdigit() and len(entrada_numero) < 4:
                entrada_numero += tecla
                # Mostrar asteriscos
                asteriscos = "*" * len(entrada_numero) + "_" * (4 - len(entrada_numero))
                actualizar_lcd("PIN (4 digitos):", asteriscos)
            elif tecla == '*':  # CANCEL
                return False
            elif tecla == '#':  # ENTER
                if len(entrada_numero) == 4:
                    if entrada_numero == pin_supervisor:
                        actualizar_lcd("PIN OK", "Acceso autorizado")
                        time.sleep_ms(1000)
                        return True
                    else:
                        actualizar_lcd("PIN ERROR", "Acceso denegado")
                        time.sleep_ms(1000)
                        return False
                else:
                    actualizar_lcd("PIN INCOMPLETO", "Ingrese 4 digitos")
                    time.sleep_ms(1000)
                    entrada_numero = ""
                    actualizar_lcd("PIN (4 digitos):", "****")
            elif tecla == 'C':  # UNDO/BACKSPACE
                if entrada_numero:
                    entrada_numero = entrada_numero[:-1]
                    asteriscos = "*" * len(entrada_numero) + "_" * (4 - len(entrada_numero))
                    actualizar_lcd("PIN (4 digitos):", asteriscos)
        time.sleep_ms(50)

def menu_principal():
    """Menú principal del sistema"""
    global modo_menu, meta, tara, step_size, debounce_ms, buzzer_on, brillo, contador, total, activo, device_id

    # Guardar log_contador al acceder al menú para actualizar
    guardar_config()

    # Mostrar título del menú con efecto deslizante
    lcd.clear()
    mostrar_texto_deslizante("MENU", 0, 80)
    time.sleep_ms(500)

    # Mostrar opciones con efecto deslizante
    opciones = [
        "1: META",
        "2: BORRAR META",
        "3: TOTAL",
        "4: BUZZER",
        "5: ID",
        "6: LOG CONTADOR",
        "0: SALIR"
    ]

    while modo_menu:
        # Mostrar opciones una por una con efecto deslizante
        for i, opcion in enumerate(opciones):
            lcd.clear()
            lcd.set_cursor(0, 0)
            lcd.print(f"Opcion {i+1}/7:")
            tecla = mostrar_texto_deslizante(opcion, 1, 80)

            if tecla and tecla in ['1', '2', '3', '4', '5', '6', '0']:
                break
            time.sleep_ms(800)

        # Si no se presionó tecla válida, esperar una
        if not tecla:
            tecla = None
            while tecla is None and modo_menu:
                tecla = teclado.leer_tecla()
                time.sleep_ms(50)

        if not modo_menu:
            break

        if tecla == '1':  # SET META
            lcd.clear()
            if verificar_pin():
                nueva_meta = entrada_numerica("META:", meta)
                if nueva_meta is not None:
                    meta = nueva_meta
                    guardar_config()
                    actualizar_lcd("META OK:", str(meta))
                    # Enviar meta actualizada
                    send_rs485("META", meta)
                    send_rs485("CONT", contador)
                    send_rs485("TOTAL", total)
                    send_rs485("ESTADO", 1 if activo else 0)
                    send_rs485("LOG", log_contador)
                    time.sleep_ms(1000)
            else:
                actualizar_lcd("META CANCELADA", "PIN incorrecto")
                time.sleep_ms(1000)
            # Continuar en el menú

        elif tecla == '2':  # BORRAR META
            lcd.clear()
            if verificar_pin():
                meta = 0
                guardar_config()
                actualizar_lcd("META BORRADA", "Sin meta fija")
                time.sleep_ms(1000)
            else:
                actualizar_lcd("BORRAR CANCELADO", "PIN incorrecto")
                time.sleep_ms(1000)
            # Continuar en el menú

        elif tecla == '3':  # MOSTRAR TOTAL
            lcd.clear()
            mostrar_estado_rapido()
            time.sleep_ms(3000)
            # Continuar en el menú

        elif tecla == '4':  # BUZZER ON/OFF
            lcd.clear()
            buzzer_on = not buzzer_on
            guardar_config()
            actualizar_lcd("BUZZER:", "ON" if buzzer_on else "OFF")
            time.sleep_ms(1000)
            # Continuar en el menú

        elif tecla == '5':  # CONFIGURAR ID
            lcd.clear()
            nuevo_id = entrada_texto("ID:", device_id)
            if nuevo_id is not None and len(nuevo_id) > 0:
                device_id = nuevo_id
                guardar_config()
                actualizar_lcd("ID OK:", device_id)
                time.sleep_ms(1000)
            # Continuar en el menú

        elif tecla == '6':  # LOG CONTADOR
            lcd.clear()
            # Guardar antes de mostrar para asegurar datos actualizados
            guardar_config()
            actualizar_lcd("LOG CONTADOR", f"TOTAL: {log_contador}")
            time.sleep_ms(3000)
            # Continuar en el menú

        elif tecla == '0':  # SALIR
            # Guardar log_contador antes de salir
            guardar_config()
            modo_menu = False
            return


# --- Interrupción del sensor ---
def on_detect(pin):
    global contador, total, _last_ms, log_contador
    now = time.ticks_ms()
    if activo and time.ticks_diff(now, _last_ms) > debounce_ms:
        contador += step_size
        total += step_size
        log_contador += step_size  # Incrementar log que no se reinicia

        # Guardar log_contador cada 50 lecturas para evitar escritura excesiva
        if log_contador % (step_size * 50) == 0:
            guardar_config()

        # Alerta visual o sonora
        if buzzer_on:
            buzzer.value(1)
            time.sleep_ms(100)
            buzzer.value(0)
        else:
            # Un solo parpadeo LED verde como alerta visual
            led_verde.value(0)  # Apagar
            time.sleep_ms(100)
            led_verde.value(1)  # Encender
            time.sleep_ms(150)
            led_verde.value(0)  # Apagar
            time.sleep_ms(50)

        # Envía el conteo actual por RS485
        send_rs485("CONT", contador)
        send_rs485("TOTAL", total)
        send_rs485("META", meta)
        send_rs485("ESTADO", 1 if activo else 0)
        send_rs485("LOG", log_contador)

        # Verificar meta
        if meta > 0:
            if contador >= meta:
                actualizar_semaforo(1, 0, 0)  # Rojo - Meta alcanzada
                actualizar_lcd("META OK!", str(contador))
            elif contador >= meta - 10:  # Últimas 10 piezas
                actualizar_semaforo(0, 1, 0)  # Amarillo intermitente
                actualizar_lcd("FALTA:", str(meta - contador))
            else:
                actualizar_semaforo(0, 1, 0)  # Amarillo - Modo lectura
                actualizar_lcd("CONT:", str(contador))
        else:
            actualizar_semaforo(0, 1, 0)  # Amarillo - Modo lectura
            actualizar_lcd("CONT:", str(contador))

        time.sleep_ms(100)
        if buzzer_on:
            buzzer.value(0)
        _last_ms = now

sensor.irq(trigger=Pin.IRQ_FALLING, handler=on_detect)

# --- Inicio ---
cargar_config()

# Mostrar mensaje de bienvenida con efecto deslizante
lcd.clear()
mostrar_texto_deslizante("=== SISPRO ONE  ===", 0, 80)
time.sleep_ms(500)
mostrar_texto_deslizante(f"=== {device_id} ===", 0, 80)
time.sleep_ms(1000)

actualizar_lcd("Sistema Listo", "Presiona D para menu")
modo_espera()

# --- Bucle Principal ---
while True:
    tecla = teclado.leer_tecla()

    if tecla:
        if tecla == 'D':  # MENÚ/OK
            modo_menu = True
            menu_principal()

        elif tecla == 'A':  # START/STOP
            if not activo:
                activo = True
                actualizar_lcd("ACTIVO", f"CONT:{contador}")
                iniciar_conteo()
                # Enviar estado actualizado
                send_rs485("ESTADO", 1)
                send_rs485("CONT", contador)
                send_rs485("TOTAL", total)
                send_rs485("META", meta)
                send_rs485("LOG", log_contador)
            else:
                activo = False
                actualizar_lcd("DETENIDO", f"CONT:{contador}")
                actualizar_semaforo(0, 1, 0)
                # Enviar estado actualizado
                send_rs485("ESTADO", 0)
                send_rs485("CONT", contador)
                send_rs485("TOTAL", total)
                send_rs485("META", meta)
                send_rs485("LOG", log_contador)
            time.sleep_ms(300)

        elif tecla == 'B':  # UNDO
            if contador > 0:
                contador -= step_size
                total -= step_size
                actualizar_lcd("UNDO", f"CONT:{contador}")
                bip_corto()
                # Enviar datos actualizados después del UNDO
                send_rs485("CONT", contador)
                send_rs485("TOTAL", total)
                send_rs485("META", meta)
                send_rs485("ESTADO", 1 if activo else 0)
                send_rs485("LOG", log_contador)
            time.sleep_ms(300)

        elif tecla == 'C':  # RESET CON PIN
            lcd.clear()
            if verificar_pin():
                contador = tara
                total = 0
                actualizar_lcd("RESET OK", f"CONT:{contador}")
                bip_largo()
            else:
                actualizar_lcd("RESET CANCELADO", "PIN incorrecto")
            time.sleep_ms(1000)

        elif tecla == '0':  # CANCEL
            if modo_menu:
                modo_menu = False
                actualizar_lcd("Sistema Listo", "Presiona D para menu")

        elif tecla == '#':  # ENTER - Mostrar estado rápido
            mostrar_estado_rapido()
            time.sleep_ms(2000)
            if activo:
                actualizar_lcd("ACTIVO", f"CONT:{contador}")
            else:
                actualizar_lcd("DETENIDO", f"CONT:{contador}")

    # Actualizar display si no está en menú (solo cuando hay cambios de estado)
    if not modo_menu and not tecla:
        estado_actual = "ACTIVO" if activo else "DETENIDO"

        if activo:
            if meta > 0 and contador >= meta:
                # Meta alcanzada - detener automáticamente
                activo = False
                actualizar_lcd("META OK!", str(contador))
                actualizar_semaforo(1, 0, 0)  # Rojo
                if buzzer_on:
                    bip_largo()
                else:
                    # Parpadeo LED verde como alerta visual
                    led_verde.value(0)
                    time.sleep_ms(100)
                    led_verde.value(1)
                    time.sleep_ms(500)
                    led_verde.value(0)
                _estado_anterior = "META_OK"
            elif _estado_anterior != estado_actual:
                # Solo actualizar cuando cambie de estado
                actualizar_semaforo(0, 1, 0)  # Amarillo - Modo lectura
                if meta > 0:
                    actualizar_lcd("ACTIVO", f"CONT:{contador}")
                else:
                    actualizar_lcd("ACTIVO (LIBRE)", f"CONT:{contador}")
                _estado_anterior = estado_actual
        else:
            if _estado_anterior != estado_actual:
                # Solo actualizar cuando cambie de estado
                actualizar_semaforo(1, 0, 0)  # Rojo - Modo detenido
                if meta > 0:
                    actualizar_lcd("DETENIDO", f"CONT:{contador}")
                else:
                    actualizar_lcd("DETENIDO (LIBRE)", f"CONT:{contador}")
                _estado_anterior = estado_actual

    time.sleep_ms(50)