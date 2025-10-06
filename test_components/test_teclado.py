#!/usr/bin/env python3
"""
Test de Teclado 4x4 - Prueba individual del teclado matricial
Para Raspberry Pi Pico
"""

import time
from machine import Pin

class TestTeclado:
    def __init__(self):
        # Definir pines del teclado 4x4 (ajustar segun conexiones)
        self.filas = [
            Pin(10, Pin.OUT),  # Fila 1
            Pin(11, Pin.OUT),  # Fila 2
            Pin(12, Pin.OUT),  # Fila 3
            Pin(13, Pin.OUT)   # Fila 4
        ]

        self.columnas = [
            Pin(6, Pin.IN, Pin.PULL_DOWN),   # Columna 1
            Pin(7, Pin.IN, Pin.PULL_DOWN),   # Columna 2
            Pin(8, Pin.IN, Pin.PULL_DOWN),   # Columna 3
            Pin(9, Pin.IN, Pin.PULL_DOWN)    # Columna 4
        ]

        # Matriz del teclado
        self.teclas = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]

        self.ultima_tecla = None
        self.ultimo_tiempo = 0

    def inicializar_filas(self):
        """Inicializar todas las filas en LOW"""
        for fila in self.filas:
            fila.off()

    def leer_teclado(self):
        """Leer el estado del teclado"""
        tecla_presionada = None

        for i, fila in enumerate(self.filas):
            # Activar fila actual
            fila.on()
            time.sleep_us(10)  # Pequeno delay para estabilizacion

            # Leer columnas
            for j, columna in enumerate(self.columnas):
                if columna.value() == 1:
                    tecla_presionada = self.teclas[i][j]
                    break

            # Desactivar fila
            fila.off()

            if tecla_presionada:
                break

        return tecla_presionada

    def test_todas_las_teclas(self):
        """Probar todas las teclas del teclado"""
        print("=== TEST DE TODAS LAS TECLAS ===")
        print("Presiona cada tecla en orden...")
        print("Esperando teclas...")

        teclas_presionadas = []
        timeout = 30  # 30 segundos de timeout

        inicio = time.time()

        while len(teclas_presionadas) < 16 and (time.time() - inicio) < timeout:
            tecla = self.leer_teclado()

            if tecla and tecla != self.ultima_tecla:
                teclas_presionadas.append(tecla)
                print(f"[{len(teclas_presionadas)}/16] Tecla presionada: {tecla}")
                self.ultima_tecla = tecla
                time.sleep(0.3)  # Debounce
            elif not tecla:
                self.ultima_tecla = None

            time.sleep(0.01)

        if len(teclas_presionadas) == 16:
            print("SUCCESS: Todas las teclas detectadas correctamente")
            return True
        else:
            print(f"ERROR: Solo se detectaron {len(teclas_presionadas)}/16 teclas")
            return False

    def test_tecla_individual(self, tecla_esperada):
        """Probar una tecla especifica"""
        print(f"Presiona la tecla '{tecla_esperada}'...")
        timeout = 10  # 10 segundos

        inicio = time.time()

        while (time.time() - inicio) < timeout:
            tecla = self.leer_teclado()

            if tecla == tecla_esperada and tecla != self.ultima_tecla:
                print(f"SUCCESS: Tecla '{tecla_esperada}' detectada correctamente")
                self.ultima_tecla = tecla
                return True
            elif not tecla:
                self.ultima_tecla = None

            time.sleep(0.01)

        print(f"ERROR: No se detecto la tecla '{tecla_esperada}' en el tiempo limite")
        return False

    def test_respuesta_rapida(self):
        """Probar respuesta rapida del teclado"""
        print("=== TEST DE RESPUESTA RAPIDA ===")
        print("Presiona teclas rapidamente...")

        inicio = time.time()
        teclas_detectadas = 0
        tiempo_limite = 5  # 5 segundos

        while (time.time() - inicio) < tiempo_limite:
            tecla = self.leer_teclado()

            if tecla and tecla != self.ultima_tecla:
                teclas_detectadas += 1
                print(f"Tecla {teclas_detectadas}: {tecla}")
                self.ultima_tecla = tecla
                time.sleep(0.1)  # Debounce mas rapido
            elif not tecla:
                self.ultima_tecla = None

            time.sleep(0.01)

        print(f"Teclas detectadas en {tiempo_limite}s: {teclas_detectadas}")
        if teclas_detectadas >= 10:
            print("SUCCESS: Respuesta rapida OK")
            return True
        else:
            print("ERROR: Respuesta demasiado lenta")
            return False

    def test_secuencia_codigo(self, codigo_esperado):
        """Probar entrada de codigo/contraseña"""
        print(f"=== TEST DE SECUENCIA: {codigo_esperado} ===")
        print(f"Ingresa la secuencia: {codigo_esperado}")

        codigo_ingresado = ""
        timeout = 30
        inicio = time.time()

        while (time.time() - inicio) < timeout:
            tecla = self.leer_teclado()

            if tecla and tecla != self.ultima_tecla:
                codigo_ingresado += tecla
                print(f"Codigo actual: {codigo_ingresado}")
                self.ultima_tecla = tecla

                if codigo_ingresado == codigo_esperado:
                    print("SUCCESS: Codigo ingresado correctamente")
                    return True
                elif len(codigo_ingresado) >= len(codigo_esperado):
                    print("ERROR: Codigo incorrecto, reiniciando...")
                    codigo_ingresado = ""

                time.sleep(0.3)
            elif not tecla:
                self.ultima_tecla = None

            time.sleep(0.01)

        print("ERROR: Timeout en entrada de codigo")
        return False

def main():
    """Funcion principal de prueba"""
    print("=== TEST DE TECLADO 4x4 - COMPONENTE INDIVIDUAL ===")
    print("Hardware: Raspberry Pi Pico")
    print("Componente: Teclado matricial 4x4")
    print("="*50)

    try:
        test_teclado = TestTeclado()
        test_teclado.inicializar_filas()

        # Menu de opciones
        while True:
            print("\nOpciones de prueba:")
            print("1. Probar todas las teclas")
            print("2. Probar tecla individual")
            print("3. Test de respuesta rapida")
            print("4. Test de secuencia de codigo")
            print("5. Mostrar matriz del teclado")
            print("0. Salir")

            opcion = input("\nSelecciona opcion (0-5): ").strip()

            if opcion == "0":
                print("Saliendo del test de teclado...")
                break
            elif opcion == "1":
                test_teclado.test_todas_las_teclas()
            elif opcion == "2":
                tecla = input("Ingresa la tecla a probar (1-9, 0, A-D, *, #): ").strip().upper()
                if tecla in ['1','2','3','4','5','6','7','8','9','0','A','B','C','D','*','#']:
                    test_teclado.test_tecla_individual(tecla)
                else:
                    print("ERROR: Tecla no valida")
            elif opcion == "3":
                test_teclado.test_respuesta_rapida()
            elif opcion == "4":
                codigo = input("Ingresa el codigo a probar (ej: 1234): ").strip()
                if codigo:
                    test_teclado.test_secuencia_codigo(codigo)
                else:
                    print("ERROR: Codigo vacio")
            elif opcion == "5":
                print("Matriz del teclado:")
                for fila in test_teclado.teclas:
                    print(" | ".join(fila))
            else:
                print("ERROR: Opcion no valida")

    except Exception as e:
        print(f"ERROR en test de teclado: {e}")

if __name__ == "__main__":
    main()
