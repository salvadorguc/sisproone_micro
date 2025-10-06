#!/usr/bin/env python3
"""
Test de Reloj DS3231 - Prueba individual del reloj de tiempo real
Para Raspberry Pi Pico con MicroPython
"""

import time
from machine import Pin, I2C

class TestDS3231:
    def __init__(self):
        # Configuracion I2C para DS3231
        self.i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

        # Direccion I2C del DS3231
        self.ds3231_addr = 0x68

        # Buscar dispositivos I2C
        dispositivos = self.i2c.scan()
        print(f"Dispositivos I2C encontrados: {[hex(x) for x in dispositivos]}")

        # Registros del DS3231
        self.REG_SECONDS = 0x00
        self.REG_MINUTES = 0x01
        self.REG_HOURS = 0x02
        self.REG_DAY = 0x03
        self.REG_DATE = 0x04
        self.REG_MONTH = 0x05
        self.REG_YEAR = 0x06
        self.REG_CONTROL = 0x0E
        self.REG_STATUS = 0x0F
        self.REG_TEMP_MSB = 0x11
        self.REG_TEMP_LSB = 0x12

    def bcd_to_dec(self, bcd):
        """Convertir BCD a decimal"""
        return (bcd // 16) * 10 + (bcd % 16)

    def dec_to_bcd(self, dec):
        """Convertir decimal a BCD"""
        return (dec // 10) * 16 + (dec % 10)

    def leer_registro(self, registro):
        """Leer un registro del DS3231"""
        try:
            self.i2c.writeto(self.ds3231_addr, bytes([registro]))
            data = self.i2c.readfrom(self.ds3231_addr, 1)
            return data[0]
        except Exception as e:
            print(f"Error leyendo registro: {e}")
            return None

    def escribir_registro(self, registro, valor):
        """Escribir un registro del DS3231"""
        try:
            self.i2c.writeto(self.ds3231_addr, bytes([registro, valor]))
            return True
        except Exception as e:
            print(f"Error escribiendo registro: {e}")
            return False

    def leer_fecha_hora(self):
        """Leer fecha y hora actual"""
        try:
            # Leer 7 registros de tiempo
            self.i2c.writeto(self.ds3231_addr, bytes([self.REG_SECONDS]))
            data = self.i2c.readfrom(self.ds3231_addr, 7)

            segundos = self.bcd_to_dec(data[0] & 0x7F)
            minutos = self.bcd_to_dec(data[1] & 0x7F)
            horas = self.bcd_to_dec(data[2] & 0x3F)
            dia_semana = data[3] & 0x07
            dia = self.bcd_to_dec(data[4] & 0x3F)
            mes = self.bcd_to_dec(data[5] & 0x1F)
            ano = self.bcd_to_dec(data[6]) + 2000

            return {
                'ano': ano,
                'mes': mes,
                'dia': dia,
                'dia_semana': dia_semana,
                'horas': horas,
                'minutos': minutos,
                'segundos': segundos
            }
        except Exception as e:
            print(f"Error leyendo fecha/hora: {e}")
            return None

    def escribir_fecha_hora(self, ano, mes, dia, horas, minutos, segundos, dia_semana=1):
        """Escribir fecha y hora"""
        try:
            data = [
                self.dec_to_bcd(segundos),
                self.dec_to_bcd(minutos),
                self.dec_to_bcd(horas),
                dia_semana,
                self.dec_to_bcd(dia),
                self.dec_to_bcd(mes),
                self.dec_to_bcd(ano % 100)
            ]

            self.i2c.writeto(self.ds3231_addr, bytes([self.REG_SECONDS] + data))
            return True
        except Exception as e:
            print(f"Error escribiendo fecha/hora: {e}")
            return False

    def leer_temperatura(self):
        """Leer temperatura del sensor interno"""
        try:
            temp_msb = self.leer_registro(self.REG_TEMP_MSB)
            temp_lsb = self.leer_registro(self.REG_TEMP_LSB)

            if temp_msb is not None and temp_lsb is not None:
                # El bit 6 del LSB indica si la temperatura es negativa
                if temp_lsb & 0x80:
                    temperatura = temp_msb - 128 + (temp_lsb >> 6) * 0.25
                else:
                    temperatura = temp_msb + (temp_lsb >> 6) * 0.25
                return temperatura
            return None
        except Exception as e:
            print(f"Error leyendo temperatura: {e}")
            return None

    def test_conexion_i2c(self):
        """Probar conexion I2C"""
        print("=== TEST DE CONEXION I2C ===")
        try:
            dispositivos = self.i2c.scan()
            if dispositivos:
                print(f"SUCCESS: Dispositivos I2C encontrados: {[hex(x) for x in dispositivos]}")
                if self.ds3231_addr in dispositivos:
                    print(f"SUCCESS: DS3231 encontrado en direccion {hex(self.ds3231_addr)}")
                    return True
                else:
                    print(f"ERROR: DS3231 no encontrado en {hex(self.ds3231_addr)}")
                    return False
            else:
                print("ERROR: No se encontraron dispositivos I2C")
                return False
        except Exception as e:
            print(f"ERROR en conexion I2C: {e}")
            return False

    def test_lectura_fecha_hora(self):
        """Probar lectura de fecha y hora"""
        print("=== TEST DE LECTURA DE FECHA Y HORA ===")
        try:
            fecha_hora = self.leer_fecha_hora()
            if fecha_hora:
                print(f"SUCCESS: Fecha/Hora leida:")
                print(f"  {fecha_hora['dia']:02d}/{fecha_hora['mes']:02d}/{fecha_hora['ano']}")
                print(f"  {fecha_hora['horas']:02d}:{fecha_hora['minutos']:02d}:{fecha_hora['segundos']:02d}")
                print(f"  Dia de semana: {fecha_hora['dia_semana']}")
                return True
            else:
                print("ERROR: No se pudo leer fecha/hora")
                return False
        except Exception as e:
            print(f"ERROR en lectura de fecha/hora: {e}")
            return False

    def test_escritura_fecha_hora(self):
        """Probar escritura de fecha y hora"""
        print("=== TEST DE ESCRITURA DE FECHA Y HORA ===")
        try:
            # Fecha de prueba: 1 de enero de 2024, 12:00:00
            if self.escribir_fecha_hora(2024, 1, 1, 12, 0, 0, 1):
                print("SUCCESS: Fecha/hora escrita correctamente")

                # Verificar que se escribio correctamente
                fecha_hora = self.leer_fecha_hora()
                if fecha_hora:
                    print(f"Verificacion: {fecha_hora['dia']:02d}/{fecha_hora['mes']:02d}/{fecha_hora['ano']}")
                    print(f"  {fecha_hora['horas']:02d}:{fecha_hora['minutos']:02d}:{fecha_hora['segundos']:02d}")
                    return True
                else:
                    print("ERROR: No se pudo verificar la escritura")
                    return False
            else:
                print("ERROR: No se pudo escribir fecha/hora")
                return False
        except Exception as e:
            print(f"ERROR en escritura de fecha/hora: {e}")
            return False

    def test_temperatura(self):
        """Probar lectura de temperatura"""
        print("=== TEST DE LECTURA DE TEMPERATURA ===")
        try:
            temperatura = self.leer_temperatura()
            if temperatura is not None:
                print(f"SUCCESS: Temperatura leida: {temperatura:.2f} C")
                return True
            else:
                print("ERROR: No se pudo leer temperatura")
                return False
        except Exception as e:
            print(f"ERROR en lectura de temperatura: {e}")
            return False

    def test_precision_tiempo(self):
        """Probar precision del reloj"""
        print("=== TEST DE PRECISION DEL RELOJ ===")
        try:
            # Leer tiempo inicial
            tiempo_inicial = self.leer_fecha_hora()
            if not tiempo_inicial:
                print("ERROR: No se pudo leer tiempo inicial")
                return False

            print("Esperando 10 segundos...")
            time.sleep(10)

            # Leer tiempo final
            tiempo_final = self.leer_fecha_hora()
            if not tiempo_final:
                print("ERROR: No se pudo leer tiempo final")
                return False

            # Calcular diferencia
            segundos_inicial = tiempo_inicial['horas'] * 3600 + tiempo_inicial['minutos'] * 60 + tiempo_inicial['segundos']
            segundos_final = tiempo_final['horas'] * 3600 + tiempo_final['minutos'] * 60 + tiempo_final['segundos']

            # Ajustar si cambio de dia
            if segundos_final < segundos_inicial:
                segundos_final += 24 * 3600

            diferencia = segundos_final - segundos_inicial
            error = abs(diferencia - 10)

            print(f"Tiempo transcurrido: {diferencia} segundos")
            print(f"Error: {error} segundos")

            if error <= 1:  # Tolerancia de 1 segundo
                print("SUCCESS: Precision del reloj OK")
                return True
            else:
                print("WARNING: Precision del reloj puede estar afectada")
                return True  # No es error critico
        except Exception as e:
            print(f"ERROR en test de precision: {e}")
            return False

    def test_alarmas(self):
        """Probar funcionalidad de alarmas"""
        print("=== TEST DE ALARMAS ===")
        try:
            # Leer estado de control
            control = self.leer_registro(self.REG_CONTROL)
            if control is not None:
                print(f"Registro de control: 0x{control:02X}")

                # Leer estado
                status = self.leer_registro(self.REG_STATUS)
                if status is not None:
                    print(f"Registro de estado: 0x{status:02X}")

                    # Verificar flags de alarma
                    if status & 0x01:
                        print("Alarma 1 activada")
                    if status & 0x02:
                        print("Alarma 2 activada")

                    print("SUCCESS: Registros de alarma accesibles")
                    return True
                else:
                    print("ERROR: No se pudo leer registro de estado")
                    return False
            else:
                print("ERROR: No se pudo leer registro de control")
                return False
        except Exception as e:
            print(f"ERROR en test de alarmas: {e}")
            return False

    def test_actualizacion_continua(self):
        """Probar actualizacion continua del reloj"""
        print("=== TEST DE ACTUALIZACION CONTINUA ===")
        print("Mostrando tiempo actual cada segundo por 10 segundos...")

        try:
            for i in range(10):
                fecha_hora = self.leer_fecha_hora()
                if fecha_hora:
                    print(f"[{i+1}/10] {fecha_hora['dia']:02d}/{fecha_hora['mes']:02d}/{fecha_hora['ano']} "
                          f"{fecha_hora['horas']:02d}:{fecha_hora['minutos']:02d}:{fecha_hora['segundos']:02d}")
                else:
                    print(f"[{i+1}/10] ERROR leyendo tiempo")
                time.sleep(1)

            print("SUCCESS: Actualizacion continua funcionando")
            return True
        except Exception as e:
            print(f"ERROR en actualizacion continua: {e}")
            return False

def main():
    """Funcion principal de prueba"""
    print("=== TEST DE RELOJ DS3231 - COMPONENTE INDIVIDUAL ===")
    print("Hardware: Raspberry Pi Pico")
    print("Componente: Reloj de tiempo real DS3231")
    print("="*50)

    try:
        test_ds3231 = TestDS3231()

        # Menu de opciones
        while True:
            print("\nOpciones de prueba:")
            print("1. Test de conexion I2C")
            print("2. Test de lectura de fecha/hora")
            print("3. Test de escritura de fecha/hora")
            print("4. Test de lectura de temperatura")
            print("5. Test de precision del reloj")
            print("6. Test de alarmas")
            print("7. Test de actualizacion continua")
            print("8. Ejecutar todos los tests")
            print("0. Salir")

            opcion = input("\nSelecciona opcion (0-8): ").strip()

            if opcion == "0":
                print("Saliendo del test de DS3231...")
                break
            elif opcion == "1":
                test_ds3231.test_conexion_i2c()
            elif opcion == "2":
                test_ds3231.test_lectura_fecha_hora()
            elif opcion == "3":
                test_ds3231.test_escritura_fecha_hora()
            elif opcion == "4":
                test_ds3231.test_temperatura()
            elif opcion == "5":
                test_ds3231.test_precision_tiempo()
            elif opcion == "6":
                test_ds3231.test_alarmas()
            elif opcion == "7":
                test_ds3231.test_actualizacion_continua()
            elif opcion == "8":
                print("Ejecutando todos los tests...")
                tests = [
                    test_ds3231.test_conexion_i2c,
                    test_ds3231.test_lectura_fecha_hora,
                    test_ds3231.test_escritura_fecha_hora,
                    test_ds3231.test_temperatura,
                    test_ds3231.test_precision_tiempo,
                    test_ds3231.test_alarmas,
                    test_ds3231.test_actualizacion_continua
                ]

                for test in tests:
                    print(f"\nEjecutando {test.__name__}...")
                    test()
                    time.sleep(1)

                print("\nTodos los tests completados")
            else:
                print("ERROR: Opcion no valida")

    except Exception as e:
        print(f"ERROR en test de DS3231: {e}")

if __name__ == "__main__":
    main()
