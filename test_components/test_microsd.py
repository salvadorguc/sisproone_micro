#!/usr/bin/env python3
"""
Test de Lector MicroSD - Prueba individual del lector de tarjeta microSD
Para Raspberry Pi Pico con MicroPython
"""

import os
import time
from machine import Pin, SPI

class TestMicroSD:
    def __init__(self):
        # Configuracion SPI para microSD
        # Ajustar pines segun conexiones
        self.spi = SPI(0,
                      baudrate=1000000,  # 1MHz inicial
                      polarity=0,
                      phase=0,
                      bits=8,
                      firstbit=SPI.MSB,
                      sck=Pin(2),   # Clock
                      mosi=Pin(3),  # Master Out Slave In
                      miso=Pin(4))  # Master In Slave Out

        # Pin de seleccion de chip (CS)
        self.cs_pin = Pin(5, Pin.OUT)
        self.cs_pin.on()  # Desactivar por defecto

        # Configuracion de archivos de prueba
        self.archivo_test = "test_microsd.txt"
        self.directorio_test = "/sd/test"

    def activar_cs(self):
        """Activar pin CS"""
        self.cs_pin.off()
        time.sleep_us(10)

    def desactivar_cs(self):
        """Desactivar pin CS"""
        time.sleep_us(10)
        self.cs_pin.on()

    def test_conexion_spi(self):
        """Probar conexion SPI"""
        print("=== TEST DE CONEXION SPI ===")
        try:
            # Verificar que SPI este configurado
            if self.spi:
                print("SUCCESS: SPI configurado correctamente")
                print(f"Baudrate: {self.spi.baudrate}")
                print(f"SCK Pin: {self.spi.sck}")
                print(f"MOSI Pin: {self.spi.mosi}")
                print(f"MISO Pin: {self.spi.miso}")
                return True
            else:
                print("ERROR: SPI no configurado")
                return False
        except Exception as e:
            print(f"ERROR en conexion SPI: {e}")
            return False

    def test_montaje_tarjeta(self):
        """Probar montaje de la tarjeta microSD"""
        print("=== TEST DE MONTAJE DE TARJETA ===")
        try:
            # Intentar montar la tarjeta
            import sdcard
            sd = sdcard.SDCard(self.spi, self.cs_pin)

            # Montar en /sd
            os.mount(sd, '/sd')

            # Verificar que se puede acceder
            if '/sd' in os.listdir('/'):
                print("SUCCESS: Tarjeta microSD montada correctamente en /sd")
                return True
            else:
                print("ERROR: No se pudo montar la tarjeta")
                return False
        except Exception as e:
            print(f"ERROR montando tarjeta: {e}")
            return False

    def test_listado_directorios(self):
        """Probar listado de directorios"""
        print("=== TEST DE LISTADO DE DIRECTORIOS ===")
        try:
            # Listar contenido de /sd
            contenido = os.listdir('/sd')
            print(f"SUCCESS: Contenido de /sd: {contenido}")

            # Mostrar informacion de cada elemento
            for elemento in contenido:
                try:
                    stat = os.stat(f'/sd/{elemento}')
                    tipo = "DIR" if stat[0] & 0x4000 else "FILE"
                    tamanio = stat[6] if not (stat[0] & 0x4000) else 0
                    print(f"  {tipo}: {elemento} ({tamanio} bytes)")
                except:
                    print(f"  UNKNOWN: {elemento}")

            return True
        except Exception as e:
            print(f"ERROR listando directorios: {e}")
            return False

    def test_creacion_directorio(self):
        """Probar creacion de directorios"""
        print("=== TEST DE CREACION DE DIRECTORIOS ===")
        try:
            # Crear directorio de prueba
            os.mkdir('/sd/test')

            # Verificar que se creo
            if 'test' in os.listdir('/sd'):
                print("SUCCESS: Directorio /sd/test creado correctamente")
                return True
            else:
                print("ERROR: No se pudo crear el directorio")
                return False
        except Exception as e:
            if "File exists" in str(e):
                print("SUCCESS: Directorio /sd/test ya existe")
                return True
            else:
                print(f"ERROR creando directorio: {e}")
                return False

    def test_escritura_archivo(self):
        """Probar escritura de archivos"""
        print("=== TEST DE ESCRITURA DE ARCHIVOS ===")
        try:
            # Contenido de prueba
            contenido = "Test de escritura en microSD\n"
            contenido += f"Timestamp: {time.time()}\n"
            contenido += "Linea 1\n"
            contenido += "Linea 2\n"
            contenido += "Linea 3\n"

            # Escribir archivo
            with open(f'/sd/{self.archivo_test}', 'w') as f:
                f.write(contenido)

            # Verificar que se escribio
            if self.archivo_test in os.listdir('/sd'):
                print("SUCCESS: Archivo escrito correctamente")
                return True
            else:
                print("ERROR: Archivo no se creo")
                return False
        except Exception as e:
            print(f"ERROR escribiendo archivo: {e}")
            return False

    def test_lectura_archivo(self):
        """Probar lectura de archivos"""
        print("=== TEST DE LECTURA DE ARCHIVOS ===")
        try:
            # Leer archivo
            with open(f'/sd/{self.archivo_test}', 'r') as f:
                contenido = f.read()

            print("SUCCESS: Archivo leido correctamente")
            print("Contenido:")
            print("=" * 40)
            print(contenido)
            print("=" * 40)
            return True
        except Exception as e:
            print(f"ERROR leyendo archivo: {e}")
            return False

    def test_archivos_multiples(self):
        """Probar creacion de archivos multiples"""
        print("=== TEST DE ARCHIVOS MULTIPLES ===")
        try:
            # Crear varios archivos
            archivos = ['archivo1.txt', 'archivo2.txt', 'archivo3.txt']

            for i, archivo in enumerate(archivos):
                contenido = f"Archivo {i+1}\nContenido de prueba\nLinea {i+1}\n"
                with open(f'/sd/{archivo}', 'w') as f:
                    f.write(contenido)

            # Verificar que todos se crearon
            contenido_sd = os.listdir('/sd')
            archivos_creados = [a for a in archivos if a in contenido_sd]

            if len(archivos_creados) == len(archivos):
                print(f"SUCCESS: {len(archivos)} archivos creados correctamente")
                return True
            else:
                print(f"ERROR: Solo se crearon {len(archivos_creados)}/{len(archivos)} archivos")
                return False
        except Exception as e:
            print(f"ERROR creando archivos multiples: {e}")
            return False

    def test_tamanio_archivos(self):
        """Probar archivos de diferentes tamanios"""
        print("=== TEST DE TAMANIOS DE ARCHIVOS ===")
        try:
            tamanios = [100, 1000, 5000, 10000]  # bytes

            for tamanio in tamanios:
                archivo = f'archivo_{tamanio}b.txt'
                contenido = "X" * tamanio

                with open(f'/sd/{archivo}', 'w') as f:
                    f.write(contenido)

                # Verificar tamanio
                stat = os.stat(f'/sd/{archivo}')
                tamanio_real = stat[6]

                if tamanio_real == tamanio:
                    print(f"SUCCESS: Archivo {archivo} - {tamanio} bytes OK")
                else:
                    print(f"ERROR: Archivo {archivo} - Esperado: {tamanio}, Real: {tamanio_real}")
                    return False

            print("SUCCESS: Todos los tamanios de archivo correctos")
            return True
        except Exception as e:
            print(f"ERROR en test de tamanios: {e}")
            return False

    def test_velocidad_escritura(self):
        """Probar velocidad de escritura"""
        print("=== TEST DE VELOCIDAD DE ESCRITURA ===")
        try:
            # Crear archivo de 10KB
            tamanio = 10240  # 10KB
            contenido = "A" * tamanio

            inicio = time.time()

            with open('/sd/test_velocidad.txt', 'w') as f:
                f.write(contenido)

            fin = time.time()
            tiempo = fin - inicio
            velocidad = tamanio / tiempo / 1024  # KB/s

            print(f"SUCCESS: Velocidad de escritura: {velocidad:.2f} KB/s")
            print(f"Tiempo: {tiempo:.2f} segundos")
            return True
        except Exception as e:
            print(f"ERROR en test de velocidad: {e}")
            return False

    def test_velocidad_lectura(self):
        """Probar velocidad de lectura"""
        print("=== TEST DE VELOCIDAD DE LECTURA ===")
        try:
            inicio = time.time()

            with open('/sd/test_velocidad.txt', 'r') as f:
                contenido = f.read()

            fin = time.time()
            tiempo = fin - inicio
            tamanio = len(contenido)
            velocidad = tamanio / tiempo / 1024  # KB/s

            print(f"SUCCESS: Velocidad de lectura: {velocidad:.2f} KB/s")
            print(f"Tiempo: {tiempo:.2f} segundos")
            print(f"Tamanio: {tamanio} bytes")
            return True
        except Exception as e:
            print(f"ERROR en test de velocidad de lectura: {e}")
            return False

    def test_persistencia_datos(self):
        """Probar persistencia de datos"""
        print("=== TEST DE PERSISTENCIA DE DATOS ===")
        try:
            # Escribir datos especificos
            datos_originales = "Datos de prueba para persistencia\nLinea 1\nLinea 2\n"

            with open('/sd/test_persistencia.txt', 'w') as f:
                f.write(datos_originales)

            # Simular reinicio (cerrar y reabrir)
            time.sleep(1)

            # Leer datos
            with open('/sd/test_persistencia.txt', 'r') as f:
                datos_leidos = f.read()

            if datos_originales == datos_leidos:
                print("SUCCESS: Datos persistentes correctamente")
                return True
            else:
                print("ERROR: Datos no persistentes")
                print(f"Original: {repr(datos_originales)}")
                print(f"Leido: {repr(datos_leidos)}")
                return False
        except Exception as e:
            print(f"ERROR en test de persistencia: {e}")
            return False

    def limpiar_archivos_test(self):
        """Limpiar archivos de prueba"""
        print("Limpiando archivos de prueba...")
        try:
            archivos_test = [
                self.archivo_test,
                'archivo1.txt', 'archivo2.txt', 'archivo3.txt',
                'archivo_100b.txt', 'archivo_1000b.txt',
                'archivo_5000b.txt', 'archivo_10000b.txt',
                'test_velocidad.txt', 'test_persistencia.txt'
            ]

            for archivo in archivos_test:
                try:
                    os.remove(f'/sd/{archivo}')
                except:
                    pass

            print("Archivos de prueba eliminados")
        except Exception as e:
            print(f"Error limpiando archivos: {e}")

def main():
    """Funcion principal de prueba"""
    print("=== TEST DE LECTOR MICROSD - COMPONENTE INDIVIDUAL ===")
    print("Hardware: Raspberry Pi Pico")
    print("Componente: Lector de tarjeta microSD")
    print("="*50)

    try:
        test_microsd = TestMicroSD()

        # Menu de opciones
        while True:
            print("\nOpciones de prueba:")
            print("1. Test de conexion SPI")
            print("2. Test de montaje de tarjeta")
            print("3. Test de listado de directorios")
            print("4. Test de creacion de directorios")
            print("5. Test de escritura de archivos")
            print("6. Test de lectura de archivos")
            print("7. Test de archivos multiples")
            print("8. Test de tamanios de archivos")
            print("9. Test de velocidad de escritura")
            print("10. Test de velocidad de lectura")
            print("11. Test de persistencia de datos")
            print("12. Ejecutar todos los tests")
            print("13. Limpiar archivos de prueba")
            print("0. Salir")

            opcion = input("\nSelecciona opcion (0-13): ").strip()

            if opcion == "0":
                print("Saliendo del test de microSD...")
                break
            elif opcion == "1":
                test_microsd.test_conexion_spi()
            elif opcion == "2":
                test_microsd.test_montaje_tarjeta()
            elif opcion == "3":
                test_microsd.test_listado_directorios()
            elif opcion == "4":
                test_microsd.test_creacion_directorio()
            elif opcion == "5":
                test_microsd.test_escritura_archivo()
            elif opcion == "6":
                test_microsd.test_lectura_archivo()
            elif opcion == "7":
                test_microsd.test_archivos_multiples()
            elif opcion == "8":
                test_microsd.test_tamanio_archivos()
            elif opcion == "9":
                test_microsd.test_velocidad_escritura()
            elif opcion == "10":
                test_microsd.test_velocidad_lectura()
            elif opcion == "11":
                test_microsd.test_persistencia_datos()
            elif opcion == "12":
                print("Ejecutando todos los tests...")
                tests = [
                    test_microsd.test_conexion_spi,
                    test_microsd.test_montaje_tarjeta,
                    test_microsd.test_listado_directorios,
                    test_microsd.test_creacion_directorio,
                    test_microsd.test_escritura_archivo,
                    test_microsd.test_lectura_archivo,
                    test_microsd.test_archivos_multiples,
                    test_microsd.test_tamanio_archivos,
                    test_microsd.test_velocidad_escritura,
                    test_microsd.test_velocidad_lectura,
                    test_microsd.test_persistencia_datos
                ]

                for test in tests:
                    print(f"\nEjecutando {test.__name__}...")
                    test()
                    time.sleep(1)

                print("\nTodos los tests completados")
            elif opcion == "13":
                test_microsd.limpiar_archivos_test()
            else:
                print("ERROR: Opcion no valida")

    except Exception as e:
        print(f"ERROR en test de microSD: {e}")
    finally:
        # Limpiar archivos de prueba al salir
        try:
            test_microsd.limpiar_archivos_test()
        except:
            pass

if __name__ == "__main__":
    main()
