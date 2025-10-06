#!/usr/bin/env python3
"""
Monitor - Version simplificada y robusta del master
"""

import serial
import time
import json
from datetime import datetime

class MonitorRS485:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.dispositivos = {}
        self.ultimo_valor = {}
        self.ultimo_tiempo = {}
        self.debug_mode = False

    def conectar(self):
        """Conectar al puerto serial"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            print(f"Conectado a {self.port} @ {self.baudrate} bps")
            return True
        except Exception as e:
            print(f"Error de conexion: {e}")
            return False

    def procesar_mensaje(self, mensaje):
        """Procesar mensaje recibido"""
        try:
            partes = mensaje.strip().split(':')
            if len(partes) != 3:
                return False

            device_id, tag, valor = partes
            valor = int(valor)
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Inicializar dispositivo si no existe
            if device_id not in self.dispositivos:
                self.dispositivos[device_id] = {
                    'contador': 0,
                    'total': 0,
                    'meta': 0,
                    'activo': False,
                    'progreso': 0.0,
                    'log_contador': 0,
                    'ultima_lectura': timestamp,
                    'estado': 'DETENIDO',
                    'ultimo_heartbeat': timestamp,
                    'timestamp_heartbeat': 0,
                    'tiempo_inactivo': 0
                }

            # Actualizar segun el tag (guardar siempre, mostrar solo CONT)
            if tag == 'CONT':
                # Omitir lecturas de CONT = 0
                if valor == 0:
                    return True

                self.dispositivos[device_id]['contador'] = valor
                self.dispositivos[device_id]['ultima_lectura'] = timestamp

                # Solo mostrar CONT si el valor cambio Y han pasado al menos 500ms
                ahora = time.time()
                debe_mostrar = False

                if self.debug_mode:
                    print(f"[{timestamp}] {device_id}: CONT = {valor}")
                    debe_mostrar = True
                elif device_id not in self.ultimo_valor:
                    debe_mostrar = True
                elif self.ultimo_valor[device_id] != valor:
                    if device_id not in self.ultimo_tiempo or ahora - self.ultimo_tiempo[device_id] > 0.5:
                        debe_mostrar = True

                if debe_mostrar:
                    if not self.debug_mode:
                        print(f"[{timestamp}] {device_id}: CONT = {valor}")
                    self.ultimo_valor[device_id] = valor
                    self.ultimo_tiempo[device_id] = ahora

            elif tag == 'TOTAL':
                self.dispositivos[device_id]['total'] = valor
                # Solo mostrar en debug mode
                if self.debug_mode:
                    print(f"[{timestamp}] {device_id}: TOTAL = {valor}")

            elif tag == 'RESET':
                self.dispositivos[device_id]['contador'] = 0
                self.dispositivos[device_id]['activo'] = False
                self.dispositivos[device_id]['estado'] = 'DETENIDO'
                print(f"[{timestamp}] {device_id}: RESET")
                if device_id in self.ultimo_valor:
                    del self.ultimo_valor[device_id]

            elif tag == 'META':
                self.dispositivos[device_id]['meta'] = valor
                # Solo mostrar en debug mode
                if self.debug_mode:
                    print(f"[{timestamp}] {device_id}: META = {valor}")

            elif tag == 'ESTADO':
                self.dispositivos[device_id]['estado'] = 'ACTIVO' if valor == 1 else 'DETENIDO'
                self.dispositivos[device_id]['activo'] = valor == 1
                # Solo mostrar en debug mode
                if self.debug_mode:
                    print(f"[{timestamp}] {device_id}: ESTADO = {'ACTIVO' if valor == 1 else 'DETENIDO'}")

            elif tag == 'LOG':
                self.dispositivos[device_id]['log_contador'] = valor
                # Solo mostrar en debug mode
                if self.debug_mode:
                    print(f"[{timestamp}] {device_id}: LOG = {valor}")

            elif tag == 'HEARTBEAT':
                self.dispositivos[device_id]['ultimo_heartbeat'] = timestamp
                self.dispositivos[device_id]['timestamp_heartbeat'] = valor
                # Solo mostrar en debug mode
                if self.debug_mode:
                    print(f"[{timestamp}] {device_id}: HEARTBEAT = {valor}")

            elif tag == 'INACTIVO':
                self.dispositivos[device_id]['tiempo_inactivo'] = valor
                # Solo mostrar en debug mode
                if self.debug_mode:
                    print(f"[{timestamp}] {device_id}: INACTIVO = {valor}s")

            # Calcular progreso siempre
            if self.dispositivos[device_id]['meta'] > 0:
                self.dispositivos[device_id]['progreso'] = (self.dispositivos[device_id]['contador'] / self.dispositivos[device_id]['meta']) * 100
            else:
                self.dispositivos[device_id]['progreso'] = 0.0

            return True

        except Exception as e:
            print(f"Error procesando mensaje: {e}")
            return False

    def mostrar_estado(self):
        """Mostrar estado completo de todos los dispositivos"""
        print("\n" + "="*70)
        print("ESTADO COMPLETO DE ESTACIONES")
        print("="*70)

        if not self.dispositivos:
            print("No hay estaciones conectadas")
            return

        for device_id, data in self.dispositivos.items():
            estado_icono = "[ACTIVO]" if data['activo'] else "[DETENIDO]"
            estado_texto = data['estado']

            print(f"\nESTACION: {device_id}")
            print(f"   Estado: {estado_icono} {estado_texto}")
            print(f"   Contador: {data['contador']}")
            print(f"   Total: {data['total']}")
            print(f"   Meta: {data['meta']}")
            print(f"   Progreso: {data['progreso']:.1f}%")
            print(f"   Log Contador: {data['log_contador']}")
            print(f"   Ultima lectura: {data['ultima_lectura']}")

            # Informacion de heartbeat
            if 'ultimo_heartbeat' in data:
                print(f"   Ultimo heartbeat: {data['ultimo_heartbeat']}")
            if 'tiempo_inactivo' in data:
                print(f"   Tiempo inactivo: {data['tiempo_inactivo']}s")

            print("-" * 50)

    def escuchar(self):
        """Escuchar mensajes RS485"""
        if not self.ser or not self.ser.is_open:
            print("No hay conexion serial")
            return

        print("Escuchando mensajes RS485...")
        print("Solo se muestra CONT en tiempo real (cada 500ms)")
        print("Se omiten lecturas de CONT = 0")
        print("Todos los datos se guardan silenciosamente por estacion")
        print("Comandos disponibles:")
        print("   'd' + Enter: Activar/desactivar modo debug (ver todo)")
        print("   's' + Enter: Mostrar estado completo de todas las estaciones")
        print("   'q' + Enter: Salir")
        print("   Ctrl+C: Salir de emergencia")

        try:
            while True:
                # Verificar entrada del usuario
                import select
                import sys
                if select.select([sys.stdin], [], [], 0)[0]:
                    entrada = sys.stdin.readline().strip().lower()
                    if entrada == 'd':
                        self.debug_mode = not self.debug_mode
                        print(f"Modo debug: {'ACTIVADO' if self.debug_mode else 'DESACTIVADO'}")
                    elif entrada == 's':
                        self.mostrar_estado()
                    elif entrada == 'q' or entrada == 'quit' or entrada == 'exit':
                        print("\nSaliendo...")
                        break

                if self.ser.in_waiting > 0:
                    mensaje = self.ser.readline().decode('utf-8', errors='ignore')
                    if mensaje.strip():
                        self.procesar_mensaje(mensaje)

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nDeteniendo por Ctrl+C...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("Desconectado")

def main():
    """Funcion principal"""
    print("MONITOR - Sistema de Conteo Industrial")
    print("="*50)

    # Configuracion
    puerto = input("Puerto serial (default: /dev/ttyUSB0): ").strip() or "/dev/ttyUSB0"
    baudrate = input("Baudrate (default: 9600): ").strip() or "9600"

    try:
        baudrate = int(baudrate)
    except:
        baudrate = 9600

    # Crear instancia del monitor
    monitor = MonitorRS485(port=puerto, baudrate=baudrate)

    # Conectar y escuchar
    if monitor.conectar():
        monitor.escuchar()
    else:
        print("No se pudo conectar al puerto serial")

if __name__ == "__main__":
    main()
