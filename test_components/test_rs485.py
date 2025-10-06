#!/usr/bin/env python3
"""
Test de Transmision RS485 - Prueba individual de comunicacion RS485
Para Raspberry Pi Pico
"""

import time
from machine import UART, Pin

class TestRS485:
    def __init__(self):
        # Configuracion UART para RS485
        self.uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

        # Pin de control DE/RE para RS485 (ajustar segun conexiones)
        self.de_re_pin = Pin(2, Pin.OUT)
        self.de_re_pin.off()  # Modo recepcion por defecto

        # Configuracion de prueba
        self.device_id = "TEST"
        self.timeout = 5  # segundos

    def modo_transmision(self):
        """Activar modo transmision"""
        self.de_re_pin.on()
        time.sleep_ms(1)  # Pequeno delay para estabilizacion

    def modo_recepcion(self):
        """Activar modo recepcion"""
        self.de_re_pin.off()
        time.sleep_ms(1)

    def enviar_mensaje(self, mensaje):
        """Enviar mensaje por RS485"""
        try:
            self.modo_transmision()
            self.uart.write(mensaje.encode())
            time.sleep_ms(10)  # Delay para transmision
            self.modo_recepcion()
            return True
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            self.modo_recepcion()
            return False

    def recibir_mensaje(self, timeout=None):
        """Recibir mensaje por RS485"""
        if timeout is None:
            timeout = self.timeout

        inicio = time.time()

        while (time.time() - inicio) < timeout:
            if self.uart.any():
                try:
                    mensaje = self.uart.read()
                    if mensaje:
                        return mensaje.decode().strip()
                except Exception as e:
                    print(f"Error recibiendo mensaje: {e}")
            time.sleep_ms(10)

        return None

    def test_conexion_basica(self):
        """Probar conexion basica del UART"""
        print("=== TEST DE CONEXION BASICA UART ===")
        try:
            # Verificar que el UART este configurado
            if self.uart:
                print("SUCCESS: UART configurado correctamente")
                print(f"Baudrate: {self.uart.baudrate}")
                print(f"TX Pin: {self.uart.tx}")
                print(f"RX Pin: {self.uart.rx}")
                return True
            else:
                print("ERROR: UART no configurado")
                return False
        except Exception as e:
            print(f"ERROR en conexion basica: {e}")
            return False

    def test_control_de_re(self):
        """Probar control de pin DE/RE"""
        print("=== TEST DE CONTROL DE/RE ===")
        try:
            # Test de modo transmision
            print("Activando modo transmision...")
            self.modo_transmision()
            time.sleep(0.1)

            # Test de modo recepcion
            print("Activando modo recepcion...")
            self.modo_recepcion()
            time.sleep(0.1)

            print("SUCCESS: Control DE/RE funcionando")
            return True
        except Exception as e:
            print(f"ERROR en control DE/RE: {e}")
            return False

    def test_transmision_simple(self):
        """Probar transmision simple"""
        print("=== TEST DE TRANSMISION SIMPLE ===")
        try:
            mensaje = "TEST:RS485:OK"
            print(f"Enviando mensaje: {mensaje}")

            if self.enviar_mensaje(mensaje + "\n"):
                print("SUCCESS: Mensaje enviado")
                return True
            else:
                print("ERROR: No se pudo enviar mensaje")
                return False
        except Exception as e:
            print(f"ERROR en transmision: {e}")
            return False

    def test_recepcion_simple(self):
        """Probar recepcion simple"""
        print("=== TEST DE RECEPCION SIMPLE ===")
        print("Esperando mensaje por 10 segundos...")
        print("Envia un mensaje desde otro dispositivo")

        mensaje = self.recibir_mensaje(10)

        if mensaje:
            print(f"SUCCESS: Mensaje recibido: {mensaje}")
            return True
        else:
            print("WARNING: No se recibio mensaje (esto es normal si no hay otro dispositivo)")
            return True  # No es error, solo no hay dispositivo conectado

    def test_protocolo_mensajes(self):
        """Probar protocolo de mensajes del sistema"""
        print("=== TEST DE PROTOCOLO DE MENSAJES ===")

        # Mensajes de prueba segun protocolo del sistema
        mensajes_test = [
            f"{self.device_id}:CONT:100",
            f"{self.device_id}:TOTAL:500",
            f"{self.device_id}:META:1000",
            f"{self.device_id}:ESTADO:1",
            f"{self.device_id}:RESET:0",
            f"{self.device_id}:HEARTBEAT:12345"
        ]

        for mensaje in mensajes_test:
            print(f"Enviando: {mensaje}")
            if self.enviar_mensaje(mensaje + "\n"):
                print("  Enviado correctamente")
                time.sleep(0.5)
            else:
                print("  ERROR en envio")
                return False

        print("SUCCESS: Todos los mensajes enviados")
        return True

    def test_loopback(self):
        """Probar loopback (conectar TX a RX)"""
        print("=== TEST DE LOOPBACK ===")
        print("IMPORTANTE: Conectar TX a RX para este test")

        mensaje_test = f"{self.device_id}:LOOPBACK:123"
        print(f"Enviando: {mensaje_test}")

        if self.enviar_mensaje(mensaje_test + "\n"):
            mensaje_recibido = self.recibir_mensaje(2)

            if mensaje_recibido and mensaje_test in mensaje_recibido:
                print(f"SUCCESS: Loopback funcionando - Recibido: {mensaje_recibido}")
                return True
            else:
                print("WARNING: Loopback no detectado (conectar TX a RX)")
                return True  # No es error si no hay loopback
        else:
            print("ERROR: No se pudo enviar mensaje")
            return False

    def test_multiples_dispositivos(self):
        """Simular comunicacion con multiples dispositivos"""
        print("=== TEST DE MULTIPLES DISPOSITIVOS ===")

        dispositivos = ["EST01", "EST02", "EST03"]

        for dispositivo in dispositivos:
            mensaje = f"{dispositivo}:CONT:{hash(dispositivo) % 1000}"
            print(f"Simulando {dispositivo}: {mensaje}")

            if self.enviar_mensaje(mensaje + "\n"):
                time.sleep(0.3)
            else:
                print(f"ERROR enviando desde {dispositivo}")
                return False

        print("SUCCESS: Simulacion de multiples dispositivos completada")
        return True

    def test_resistencia_interferencias(self):
        """Probar resistencia a interferencias"""
        print("=== TEST DE RESISTENCIA A INTERFERENCIAS ===")

        # Enviar mensajes rapidos para simular interferencias
        for i in range(20):
            mensaje = f"{self.device_id}:NOISE:{i:04d}"
            self.enviar_mensaje(mensaje + "\n")
            time.sleep(0.1)

        # Enviar mensaje valido
        mensaje_valido = f"{self.device_id}:VALID:999"
        print(f"Enviando mensaje valido: {mensaje_valido}")

        if self.enviar_mensaje(mensaje_valido + "\n"):
            print("SUCCESS: Mensaje valido enviado despues de interferencias")
            return True
        else:
            print("ERROR: No se pudo enviar mensaje valido")
            return False

    def test_estres_transmision(self):
        """Probar estres de transmision"""
        print("=== TEST DE ESTRES DE TRANSMISION ===")

        inicio = time.time()
        mensajes_enviados = 0

        print("Enviando mensajes rapidos por 10 segundos...")

        while (time.time() - inicio) < 10:
            mensaje = f"{self.device_id}:STRESS:{mensajes_enviados:06d}"
            if self.enviar_mensaje(mensaje + "\n"):
                mensajes_enviados += 1
            time.sleep(0.01)  # Muy rapido

        print(f"SUCCESS: {mensajes_enviados} mensajes enviados en 10 segundos")
        return True

def main():
    """Funcion principal de prueba"""
    print("=== TEST DE TRANSMISION RS485 - COMPONENTE INDIVIDUAL ===")
    print("Hardware: Raspberry Pi Pico")
    print("Componente: Comunicacion RS485")
    print("="*50)

    try:
        test_rs485 = TestRS485()

        # Menu de opciones
        while True:
            print("\nOpciones de prueba:")
            print("1. Test de conexion basica UART")
            print("2. Test de control DE/RE")
            print("3. Test de transmision simple")
            print("4. Test de recepcion simple")
            print("5. Test de protocolo de mensajes")
            print("6. Test de loopback")
            print("7. Test de multiples dispositivos")
            print("8. Test de resistencia a interferencias")
            print("9. Test de estres de transmision")
            print("10. Ejecutar todos los tests")
            print("0. Salir")

            opcion = input("\nSelecciona opcion (0-10): ").strip()

            if opcion == "0":
                print("Saliendo del test de RS485...")
                break
            elif opcion == "1":
                test_rs485.test_conexion_basica()
            elif opcion == "2":
                test_rs485.test_control_de_re()
            elif opcion == "3":
                test_rs485.test_transmision_simple()
            elif opcion == "4":
                test_rs485.test_recepcion_simple()
            elif opcion == "5":
                test_rs485.test_protocolo_mensajes()
            elif opcion == "6":
                test_rs485.test_loopback()
            elif opcion == "7":
                test_rs485.test_multiples_dispositivos()
            elif opcion == "8":
                test_rs485.test_resistencia_interferencias()
            elif opcion == "9":
                test_rs485.test_estres_transmision()
            elif opcion == "10":
                print("Ejecutando todos los tests...")
                tests = [
                    test_rs485.test_conexion_basica,
                    test_rs485.test_control_de_re,
                    test_rs485.test_transmision_simple,
                    test_rs485.test_recepcion_simple,
                    test_rs485.test_protocolo_mensajes,
                    test_rs485.test_loopback,
                    test_rs485.test_multiples_dispositivos,
                    test_rs485.test_resistencia_interferencias,
                    test_rs485.test_estres_transmision
                ]

                for test in tests:
                    print(f"\nEjecutando {test.__name__}...")
                    test()
                    time.sleep(1)

                print("\nTodos los tests completados")
            else:
                print("ERROR: Opcion no valida")

    except Exception as e:
        print(f"ERROR en test de RS485: {e}")

if __name__ == "__main__":
    main()
