#!/usr/bin/env python3
"""
Monitor RS485 - Comunicación con Raspberry Pi Pico
"""

import serial
import time
import threading
import logging
from typing import Optional, Callable
from queue import Queue

class MonitorRS485:
    def __init__(self, config):
        self.config = config
        self.port = config.rs485_port
        self.baudrate = config.rs485_baudrate
        self.timeout = config.rs485_timeout
        self.ser = None
        self.running = False
        self.message_queue = Queue()
        self.callbacks = []
        self.logger = logging.getLogger(__name__)

    def conectar(self) -> bool:
        """Conectar al puerto RS485"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )

            self.running = True
            self.logger.info(f"SUCCESS: Conectado a RS485: {self.port} @ {self.baudrate} bps")
            return True

        except Exception as e:
            self.logger.error(f"ERROR: Error conectando RS485: {e}")
            return False

    def desconectar(self):
        """Desconectar RS485"""
        try:
            self.running = False
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.logger.info("SUCCESS: RS485 desconectado")
        except Exception as e:
            self.logger.error(f"ERROR: Error desconectando RS485: {e}")

    def leer_mensaje(self) -> Optional[str]:
        """Leer mensaje del Pico"""
        try:
            if not self.ser or not self.ser.is_open:
                return None

            if self.ser.in_waiting > 0:
                mensaje = self.ser.readline().decode('utf-8', errors='ignore')
                if mensaje.strip():
                    self.logger.debug(f"INFO: Mensaje recibido: {mensaje.strip()}")
                    return mensaje.strip()
            return None

        except Exception as e:
            self.logger.error(f"ERROR: Error leyendo mensaje: {e}")
            return None

    def enviar_comando(self, comando: str) -> bool:
        """Enviar comando al Pico"""
        try:
            if not self.ser or not self.ser.is_open:
                return False

            mensaje = f"{comando}\n"
            data = mensaje.encode('utf-8')
            self.ser.write(data)
            self.ser.flush()

            self.logger.info(f"INFO: Comando enviado: {comando}")
            return True

        except Exception as e:
            self.logger.error(f"ERROR: Error enviando comando: {e}")
            return False

    def activar_estacion(self, device_id: str, producto_id: str) -> bool:
        """Activar estación en el Pico"""
        comando = f"{device_id}:ACTIVAR:{producto_id}"
        return self.enviar_comando(comando)

    def desactivar_estacion(self, device_id: str) -> bool:
        """Desactivar estación en el Pico"""
        comando = f"{device_id}:DESACTIVAR:0"
        return self.enviar_comando(comando)

    def establecer_meta(self, device_id: str, cantidad: int) -> bool:
        """Establecer meta de producción en el Pico"""
        comando = f"{device_id}:META:{cantidad}"
        return self.enviar_comando(comando)

    def pausar_estacion(self, device_id: str) -> bool:
        """Pausar estación en el Pico"""
        comando = f"{device_id}:PAUSAR:0"
        return self.enviar_comando(comando)

    def reanudar_estacion(self, device_id: str) -> bool:
        """Reanudar estación en el Pico"""
        comando = f"{device_id}:REANUDAR:0"
        return self.enviar_comando(comando)

    def resetear_estacion(self, device_id: str) -> bool:
        """Resetear estación en el Pico"""
        comando = f"{device_id}:RESET:0"
        return self.enviar_comando(comando)

    def solicitar_estado(self, device_id: str) -> bool:
        """Solicitar estado de la estación al Pico"""
        comando = f"{device_id}:ESTADO:0"
        return self.enviar_comando(comando)

    def agregar_callback(self, callback: Callable[[str], None]):
        """Agregar callback para procesar mensajes"""
        self.callbacks.append(callback)

    def procesar_mensajes(self):
        """Procesar mensajes recibidos (para usar en thread)"""
        while self.running:
            try:
                mensaje = self.leer_mensaje()
                if mensaje:
                    # Agregar a cola
                    self.message_queue.put(mensaje)

                    # Ejecutar callbacks
                    for callback in self.callbacks:
                        try:
                            callback(mensaje)
                        except Exception as e:
                            self.logger.error(f"ERROR: Error en callback: {e}")

                time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"ERROR: Error procesando mensajes: {e}")
                time.sleep(1)

    def obtener_mensaje_de_cola(self) -> Optional[str]:
        """Obtener mensaje de la cola"""
        try:
            return self.message_queue.get_nowait()
        except:
            return None

    def limpiar_cola(self):
        """Limpiar cola de mensajes"""
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except:
                break

    def limpiar_buffer(self):
        """Limpiar buffer serial y cola de mensajes"""
        try:
            # Limpiar cola de mensajes
            self.limpiar_cola()

            # Limpiar buffer de entrada del puerto serial
            if self.ser and self.ser.is_open:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.logger.info("SUCCESS: Buffer RS485 limpiado")
                return True
            return False
        except Exception as e:
            self.logger.error(f"ERROR: Error limpiando buffer RS485: {e}")
            return False
