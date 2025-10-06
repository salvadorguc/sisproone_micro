#!/usr/bin/env python3
"""
Test de Buzzer - Prueba individual del buzzer
Para Raspberry Pi Pico
"""

import time
from machine import Pin, PWM

class TestBuzzer:
    def __init__(self):
        # Pin del buzzer (ajustar segun conexiones)
        self.buzzer_pin = Pin(15, Pin.OUT)
        self.pwm = PWM(self.buzzer_pin)

        # Frecuencias de notas musicales
        self.notas = {
            'DO': 262,    'DO#': 277,   'RE': 294,   'RE#': 311,
            'MI': 330,    'FA': 349,    'FA#': 370,  'SOL': 392,
            'SOL#': 415,  'LA': 440,    'LA#': 466,  'SI': 494,
            'DO2': 523,   'DO2#': 554,  'RE2': 587,  'RE2#': 622,
            'MI2': 659,   'FA2': 698,   'FA2#': 740, 'SOL2': 784
        }

    def sonar_frecuencia(self, frecuencia, duracion=1, duty=512):
        """Hacer sonar el buzzer a una frecuencia especifica"""
        try:
            self.pwm.freq(frecuencia)
            self.pwm.duty_u16(duty)
            time.sleep(duracion)
            self.pwm.duty_u16(0)  # Silenciar
            return True
        except Exception as e:
            print(f"Error sonando frecuencia: {e}")
            return False

    def test_conexion(self):
        """Probar conexion basica del buzzer"""
        print("=== TEST DE CONEXION DEL BUZZER ===")
        try:
            # Probar encendido/apagado simple
            self.buzzer_pin.on()
            time.sleep(0.5)
            self.buzzer_pin.off()
            time.sleep(0.5)

            print("SUCCESS: Conexion del buzzer OK")
            return True
        except Exception as e:
            print(f"ERROR en conexion: {e}")
            return False

    def test_frecuencias(self):
        """Probar diferentes frecuencias"""
        print("=== TEST DE FRECUENCIAS ===")
        frecuencias_test = [100, 200, 500, 1000, 2000, 4000]

        for freq in frecuencias_test:
            print(f"Probando frecuencia: {freq} Hz")
            self.sonar_frecuencia(freq, 0.5)
            time.sleep(0.2)

        print("SUCCESS: Todas las frecuencias probadas")
        return True

    def test_notas_musicales(self):
        """Probar notas musicales"""
        print("=== TEST DE NOTAS MUSICALES ===")

        # Escala musical
        escala = ['DO', 'RE', 'MI', 'FA', 'SOL', 'LA', 'SI', 'DO2']

        for nota in escala:
            if nota in self.notas:
                print(f"Nota: {nota} ({self.notas[nota]} Hz)")
                self.sonar_frecuencia(self.notas[nota], 0.5)
                time.sleep(0.1)

        print("SUCCESS: Escala musical completada")
        return True

    def test_volumen(self):
        """Probar diferentes niveles de volumen"""
        print("=== TEST DE VOLUMEN ===")

        volumenes = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

        for vol in volumenes:
            print(f"Volumen: {vol}/65535")
            self.pwm.freq(1000)  # 1kHz
            self.pwm.duty_u16(vol)
            time.sleep(0.5)

        self.pwm.duty_u16(0)  # Silenciar
        print("SUCCESS: Test de volumen completado")
        return True

    def test_patrones_sonido(self):
        """Probar patrones de sonido"""
        print("=== TEST DE PATRONES DE SONIDO ===")

        # Patron 1: Beep simple
        print("Patron 1: Beep simple")
        self.sonar_frecuencia(1000, 0.2)
        time.sleep(0.3)

        # Patron 2: Doble beep
        print("Patron 2: Doble beep")
        for _ in range(2):
            self.sonar_frecuencia(1500, 0.1)
            time.sleep(0.1)
        time.sleep(0.3)

        # Patron 3: Beep largo
        print("Patron 3: Beep largo")
        self.sonar_frecuencia(800, 1.0)
        time.sleep(0.3)

        # Patron 4: Ascendente
        print("Patron 4: Escala ascendente rapida")
        frecuencias = [200, 400, 600, 800, 1000, 1200]
        for freq in frecuencias:
            self.sonar_frecuencia(freq, 0.1)
            time.sleep(0.05)
        time.sleep(0.3)

        print("SUCCESS: Todos los patrones probados")
        return True

    def test_alarmas_sistema(self):
        """Probar alarmas tipicas del sistema"""
        print("=== TEST DE ALARMAS DEL SISTEMA ===")

        # Alarma de inicio
        print("Alarma: SISTEMA INICIANDO")
        self.sonar_frecuencia(800, 0.3)
        time.sleep(0.1)
        self.sonar_frecuencia(1000, 0.3)
        time.sleep(0.1)
        self.sonar_frecuencia(1200, 0.3)
        time.sleep(1)

        # Alarma de exito
        print("Alarma: OPERACION EXITOSA")
        self.sonar_frecuencia(1000, 0.2)
        time.sleep(0.1)
        self.sonar_frecuencia(1000, 0.2)
        time.sleep(1)

        # Alarma de error
        print("Alarma: ERROR DETECTADO")
        for _ in range(3):
            self.sonar_frecuencia(200, 0.5)
            time.sleep(0.2)
        time.sleep(1)

        # Alarma de advertencia
        print("Alarma: ADVERTENCIA")
        for _ in range(2):
            self.sonar_frecuencia(600, 0.3)
            time.sleep(0.1)
            self.sonar_frecuencia(800, 0.3)
            time.sleep(0.2)
        time.sleep(1)

        print("SUCCESS: Todas las alarmas probadas")
        return True

    def test_melodia_simple(self):
        """Probar melodia simple"""
        print("=== TEST DE MELODIA SIMPLE ===")

        # Melodia: "Twinkle Twinkle Little Star" (fragmento)
        melodia = [
            ('DO', 0.5), ('DO', 0.5), ('SOL', 0.5), ('SOL', 0.5),
            ('LA', 0.5), ('LA', 0.5), ('SOL', 1.0),
            ('FA', 0.5), ('FA', 0.5), ('MI', 0.5), ('MI', 0.5),
            ('RE', 0.5), ('RE', 0.5), ('DO', 1.0)
        ]

        print("Reproduciendo: Estrellita donde estas...")
        for nota, duracion in melodia:
            if nota in self.notas:
                self.sonar_frecuencia(self.notas[nota], duracion)
                time.sleep(0.1)

        print("SUCCESS: Melodia reproducida")
        return True

    def test_respuesta_rapida(self):
        """Probar respuesta rapida del buzzer"""
        print("=== TEST DE RESPUESTA RAPIDA ===")

        # Test de respuesta rapida con frecuencias variables
        inicio = time.time()
        contador = 0

        while (time.time() - inicio) < 5:  # 5 segundos
            frecuencia = 500 + (contador * 100)
            self.sonar_frecuencia(frecuencia, 0.1)
            contador += 1
            time.sleep(0.05)

        print(f"SUCCESS: {contador} sonidos en 5 segundos")
        return True

def main():
    """Funcion principal de prueba"""
    print("=== TEST DE BUZZER - COMPONENTE INDIVIDUAL ===")
    print("Hardware: Raspberry Pi Pico")
    print("Componente: Buzzer/Piezo")
    print("="*50)

    try:
        test_buzzer = TestBuzzer()

        # Menu de opciones
        while True:
            print("\nOpciones de prueba:")
            print("1. Test de conexion")
            print("2. Test de frecuencias")
            print("3. Test de notas musicales")
            print("4. Test de volumen")
            print("5. Test de patrones de sonido")
            print("6. Test de alarmas del sistema")
            print("7. Test de melodia simple")
            print("8. Test de respuesta rapida")
            print("9. Ejecutar todos los tests")
            print("0. Salir")

            opcion = input("\nSelecciona opcion (0-9): ").strip()

            if opcion == "0":
                print("Saliendo del test de buzzer...")
                # Asegurar que el buzzer este silenciado
                test_buzzer.pwm.duty_u16(0)
                break
            elif opcion == "1":
                test_buzzer.test_conexion()
            elif opcion == "2":
                test_buzzer.test_frecuencias()
            elif opcion == "3":
                test_buzzer.test_notas_musicales()
            elif opcion == "4":
                test_buzzer.test_volumen()
            elif opcion == "5":
                test_buzzer.test_patrones_sonido()
            elif opcion == "6":
                test_buzzer.test_alarmas_sistema()
            elif opcion == "7":
                test_buzzer.test_melodia_simple()
            elif opcion == "8":
                test_buzzer.test_respuesta_rapida()
            elif opcion == "9":
                print("Ejecutando todos los tests...")
                tests = [
                    test_buzzer.test_conexion,
                    test_buzzer.test_frecuencias,
                    test_buzzer.test_notas_musicales,
                    test_buzzer.test_volumen,
                    test_buzzer.test_patrones_sonido,
                    test_buzzer.test_alarmas_sistema,
                    test_buzzer.test_melodia_simple,
                    test_buzzer.test_respuesta_rapida
                ]

                for test in tests:
                    print(f"\nEjecutando {test.__name__}...")
                    test()
                    time.sleep(1)

                print("\nTodos los tests completados")
            else:
                print("ERROR: Opcion no valida")

    except Exception as e:
        print(f"ERROR en test de buzzer: {e}")
    finally:
        # Asegurar que el buzzer este silenciado
        try:
            test_buzzer.pwm.duty_u16(0)
        except:
            pass

if __name__ == "__main__":
    main()
