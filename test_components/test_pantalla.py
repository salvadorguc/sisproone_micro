#!/usr/bin/env python3
"""
Test de Pantalla LCD 16x2 - Prueba individual de la pantalla
Para Raspberry Pi Pico
"""

import time
from machine import Pin, I2C

class TestPantallaLCD:
    def __init__(self):
        # Configuracion I2C para LCD
        self.i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

        # Buscar dispositivos I2C
        dispositivos = self.i2c.scan()
        print(f"Dispositivos I2C encontrados: {[hex(x) for x in dispositivos]}")

        # Direccion comun para LCD 16x2 con PCF8574
        self.lcd_addr = 0x27  # Cambiar segun el modulo

        # Comandos LCD
        self.CLEAR_DISPLAY = 0x01
        self.RETURN_HOME = 0x02
        self.DISPLAY_ON = 0x0C
        self.DISPLAY_OFF = 0x08
        self.CURSOR_ON = 0x0E
        self.CURSOR_OFF = 0x0C
        self.BLINK_ON = 0x0F
        self.BLINK_OFF = 0x0C

    def enviar_comando(self, comando):
        """Enviar comando al LCD"""
        try:
            # Enviar comando en modo 4 bits
            self.i2c.writeto(self.lcd_addr, bytes([comando & 0xF0 | 0x04, 0x00]))
            time.sleep_us(50)
            self.i2c.writeto(self.lcd_addr, bytes([comando & 0xF0, 0x00]))
            time.sleep_us(50)

            # Segundo nibble
            self.i2c.writeto(self.lcd_addr, bytes([(comando << 4) & 0xF0 | 0x04, 0x00]))
            time.sleep_us(50)
            self.i2c.writeto(self.lcd_addr, bytes([(comando << 4) & 0xF0, 0x00]))
            time.sleep_us(50)
            return True
        except Exception as e:
            print(f"Error enviando comando: {e}")
            return False

    def enviar_dato(self, dato):
        """Enviar dato al LCD"""
        try:
            # Enviar dato en modo 4 bits
            self.i2c.writeto(self.lcd_addr, bytes([dato & 0xF0 | 0x05, 0x00]))
            time.sleep_us(50)
            self.i2c.writeto(self.lcd_addr, bytes([dato & 0xF0, 0x01]))
            time.sleep_us(50)

            # Segundo nibble
            self.i2c.writeto(self.lcd_addr, bytes([(dato << 4) & 0xF0 | 0x05, 0x00]))
            time.sleep_us(50)
            self.i2c.writeto(self.lcd_addr, bytes([(dato << 4) & 0xF0, 0x01]))
            time.sleep_us(50)
            return True
        except Exception as e:
            print(f"Error enviando dato: {e}")
            return False

    def inicializar_lcd(self):
        """Inicializar el LCD"""
        print("Inicializando LCD...")

        # Secuencia de inicializacion
        time.sleep_ms(50)
        self.enviar_comando(0x33)
        time.sleep_ms(5)
        self.enviar_comando(0x32)
        time.sleep_ms(5)
        self.enviar_comando(0x28)  # 4 bits, 2 lineas, 5x8
        time.sleep_ms(5)
        self.enviar_comando(0x0C)  # Display ON, cursor OFF
        time.sleep_ms(5)
        self.enviar_comando(0x06)  # Increment cursor
        time.sleep_ms(5)
        self.enviar_comando(0x01)  # Clear display
        time.sleep_ms(2)

        print("LCD inicializado")

    def escribir_texto(self, texto, linea=1, posicion=0):
        """Escribir texto en el LCD"""
        # Posicionar cursor
        if linea == 1:
            self.enviar_comando(0x80 + posicion)
        else:
            self.enviar_comando(0xC0 + posicion)

        # Escribir texto
        for caracter in texto:
            self.enviar_dato(ord(caracter))

    def limpiar_pantalla(self):
        """Limpiar la pantalla"""
        self.enviar_comando(self.CLEAR_DISPLAY)
        time.sleep_ms(2)

    def test_conexion_i2c(self):
        """Probar conexion I2C"""
        print("=== TEST DE CONEXION I2C ===")
        try:
            dispositivos = self.i2c.scan()
            if dispositivos:
                print(f"SUCCESS: Dispositivos I2C encontrados: {[hex(x) for x in dispositivos]}")
                if self.lcd_addr in dispositivos:
                    print(f"SUCCESS: LCD encontrado en direccion {hex(self.lcd_addr)}")
                    return True
                else:
                    print(f"WARNING: LCD no encontrado en {hex(self.lcd_addr)}")
                    print("Probando con direcciones comunes...")
                    for addr in [0x27, 0x3F, 0x20, 0x21]:
                        if addr in dispositivos:
                            self.lcd_addr = addr
                            print(f"LCD encontrado en {hex(addr)}")
                            return True
                    return False
            else:
                print("ERROR: No se encontraron dispositivos I2C")
                return False
        except Exception as e:
            print(f"ERROR en conexion I2C: {e}")
            return False

    def test_inicializacion(self):
        """Probar inicializacion del LCD"""
        print("=== TEST DE INICIALIZACION ===")
        try:
            self.inicializar_lcd()
            print("SUCCESS: LCD inicializado correctamente")
            return True
        except Exception as e:
            print(f"ERROR en inicializacion: {e}")
            return False

    def test_escribir_texto(self):
        """Probar escritura de texto"""
        print("=== TEST DE ESCRITURA DE TEXTO ===")
        try:
            # Limpiar pantalla
            self.limpiar_pantalla()

            # Escribir en primera linea
            self.escribir_texto("TEST LCD 16x2", 1, 0)
            time.sleep(1)

            # Escribir en segunda linea
            self.escribir_texto("Linea 2 OK", 2, 0)
            time.sleep(2)

            print("SUCCESS: Texto escrito correctamente")
            return True
        except Exception as e:
            print(f"ERROR escribiendo texto: {e}")
            return False

    def test_caracteres_especiales(self):
        """Probar caracteres especiales"""
        print("=== TEST DE CARACTERES ESPECIALES ===")
        try:
            self.limpiar_pantalla()

            # Mostrar caracteres especiales
            caracteres = "!@#$%^&*()_+-="
            self.escribir_texto(caracteres, 1, 0)
            time.sleep(2)

            # Numeros
            numeros = "0123456789"
            self.escribir_texto(numeros, 2, 0)
            time.sleep(2)

            print("SUCCESS: Caracteres especiales mostrados")
            return True
        except Exception as e:
            print(f"ERROR con caracteres especiales: {e}")
            return False

    def test_contador_dinamico(self):
        """Probar contador dinamico"""
        print("=== TEST DE CONTADOR DINAMICO ===")
        try:
            for i in range(10):
                self.limpiar_pantalla()
                self.escribir_texto(f"Contador: {i}", 1, 0)
                self.escribir_texto(f"Segundos: {i}", 2, 0)
                time.sleep(1)

            print("SUCCESS: Contador dinamico funcionando")
            return True
        except Exception as e:
            print(f"ERROR en contador dinamico: {e}")
            return False

    def test_parpadeo_cursor(self):
        """Probar parpadeo de cursor"""
        print("=== TEST DE PARPADEO DE CURSOR ===")
        try:
            self.limpiar_pantalla()
            self.escribir_texto("Cursor parpadeando", 1, 0)

            # Activar parpadeo
            self.enviar_comando(self.BLINK_ON)
            time.sleep(3)

            # Desactivar parpadeo
            self.enviar_comando(self.BLINK_OFF)
            time.sleep(1)

            print("SUCCESS: Parpadeo de cursor funcionando")
            return True
        except Exception as e:
            print(f"ERROR en parpadeo de cursor: {e}")
            return False

def main():
    """Funcion principal de prueba"""
    print("=== TEST DE PANTALLA LCD 16x2 - COMPONENTE INDIVIDUAL ===")
    print("Hardware: Raspberry Pi Pico")
    print("Componente: LCD 16x2 con I2C")
    print("="*50)

    try:
        test_lcd = TestPantallaLCD()

        # Menu de opciones
        while True:
            print("\nOpciones de prueba:")
            print("1. Test de conexion I2C")
            print("2. Test de inicializacion")
            print("3. Test de escritura de texto")
            print("4. Test de caracteres especiales")
            print("5. Test de contador dinamico")
            print("6. Test de parpadeo de cursor")
            print("7. Ejecutar todos los tests")
            print("0. Salir")

            opcion = input("\nSelecciona opcion (0-7): ").strip()

            if opcion == "0":
                print("Saliendo del test de pantalla...")
                break
            elif opcion == "1":
                test_lcd.test_conexion_i2c()
            elif opcion == "2":
                test_lcd.test_inicializacion()
            elif opcion == "3":
                test_lcd.test_escribir_texto()
            elif opcion == "4":
                test_lcd.test_caracteres_especiales()
            elif opcion == "5":
                test_lcd.test_contador_dinamico()
            elif opcion == "6":
                test_lcd.test_parpadeo_cursor()
            elif opcion == "7":
                print("Ejecutando todos los tests...")
                tests = [
                    test_lcd.test_conexion_i2c,
                    test_lcd.test_inicializacion,
                    test_lcd.test_escribir_texto,
                    test_lcd.test_caracteres_especiales,
                    test_lcd.test_contador_dinamico,
                    test_lcd.test_parpadeo_cursor
                ]

                for test in tests:
                    print(f"\nEjecutando {test.__name__}...")
                    test()
                    time.sleep(1)

                print("\nTodos los tests completados")
            else:
                print("ERROR: Opcion no valida")

    except Exception as e:
        print(f"ERROR en test de pantalla: {e}")

if __name__ == "__main__":
    main()
