#!/usr/bin/env python3
"""
Test de LEDs - Prueba individual de componentes LED
Para Raspberry Pi Pico
"""

import time
from machine import Pin

class TestLEDs:
    def __init__(self):
        # Definir pines de LEDs (ajustar segun conexiones)
        self.leds = {
            'rojo': Pin(2, Pin.OUT),      # LED rojo - Error/Estado
            'verde': Pin(3, Pin.OUT),     # LED verde - Exito/Activo
            'azul': Pin(4, Pin.OUT),      # LED azul - Info/Proceso
            'amarillo': Pin(5, Pin.OUT)   # LED amarillo - Advertencia
        }

    def test_individual_led(self, color, duracion=1):
        """Probar un LED individual"""
        print(f"Probando LED {color}...")
        self.leds[color].on()
        time.sleep(duracion)
        self.leds[color].off()
        print(f"LED {color} - [SUCCESS]")

    def test_todos_leds(self):
        """Probar todos los LEDs en secuencia"""
        print("=== TEST DE TODOS LOS LEDs ===")
        for color in self.leds.keys():
            self.test_individual_led(color, 0.5)
            time.sleep(0.2)
        print("Todos los LEDs probados correctamente")

    def test_parpadeo(self, color, veces=5, intervalo=0.3):
        """Probar parpadeo de un LED"""
        print(f"Probando parpadeo de LED {color} ({veces} veces)...")
        for i in range(veces):
            self.leds[color].on()
            time.sleep(intervalo)
            self.leds[color].off()
            time.sleep(intervalo)
        print(f"Parpadeo LED {color} - [SUCCESS]")

    def test_estados_sistema(self):
        """Simular estados del sistema con LEDs"""
        print("=== SIMULACION DE ESTADOS DEL SISTEMA ===")

        # Estado: Iniciando
        print("Estado: INICIANDO")
        self.leds['azul'].on()
        time.sleep(1)
        self.leds['azul'].off()

        # Estado: Activo
        print("Estado: ACTIVO")
        self.leds['verde'].on()
        time.sleep(1)
        self.leds['verde'].off()

        # Estado: Advertencia
        print("Estado: ADVERTENCIA")
        self.leds['amarillo'].on()
        time.sleep(1)
        self.leds['amarillo'].off()

        # Estado: Error
        print("Estado: ERROR")
        self.leds['rojo'].on()
        time.sleep(1)
        self.leds['rojo'].off()

        print("Simulacion de estados completada")

    def apagar_todos(self):
        """Apagar todos los LEDs"""
        for led in self.leds.values():
            led.off()
        print("Todos los LEDs apagados")

def main():
    """Funcion principal de prueba"""
    print("=== TEST DE LEDs - COMPONENTE INDIVIDUAL ===")
    print("Hardware: Raspberry Pi Pico")
    print("Componente: LEDs de estado")
    print("="*50)

    try:
        test_leds = TestLEDs()

        # Menu de opciones
        while True:
            print("\nOpciones de prueba:")
            print("1. Probar todos los LEDs")
            print("2. Probar LED individual")
            print("3. Probar parpadeo")
            print("4. Simular estados del sistema")
            print("5. Apagar todos")
            print("0. Salir")

            opcion = input("\nSelecciona opcion (0-5): ").strip()

            if opcion == "0":
                print("Saliendo del test de LEDs...")
                break
            elif opcion == "1":
                test_leds.test_todos_leds()
            elif opcion == "2":
                print("LEDs disponibles: rojo, verde, azul, amarillo")
                color = input("Color del LED: ").strip().lower()
                if color in test_leds.leds:
                    test_leds.test_individual_led(color)
                else:
                    print("ERROR: Color no valido")
            elif opcion == "3":
                print("LEDs disponibles: rojo, verde, azul, amarillo")
                color = input("Color del LED: ").strip().lower()
                if color in test_leds.leds:
                    test_leds.test_parpadeo(color)
                else:
                    print("ERROR: Color no valido")
            elif opcion == "4":
                test_leds.test_estados_sistema()
            elif opcion == "5":
                test_leds.apagar_todos()
            else:
                print("ERROR: Opcion no valida")

    except Exception as e:
        print(f"ERROR en test de LEDs: {e}")
    finally:
        # Asegurar que todos los LEDs esten apagados
        try:
            test_leds.apagar_todos()
        except:
            pass

if __name__ == "__main__":
    main()
