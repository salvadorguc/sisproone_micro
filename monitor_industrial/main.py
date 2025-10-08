#!/usr/bin/env python3
"""
Monitor Industrial SISPRO - Estación de Trabajo
Raspberry Pi - Interfaz Industrial Fullscreen
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import logging
from datetime import datetime, timedelta
import asyncio
import aiohttp
import serial
import redis
import sqlite3
from typing import Optional, Dict, List, Any
import os
import sys

# Importar módulos locales
from config import Config
from sispro_connector import SISPROConnector
from monitor_rs485 import MonitorRS485
from barcode_validator import BarcodeValidator
from cache_manager import CacheManager
from database_manager import DatabaseManager
from estado_manager import EstadoManager
from interfaz_industrial import InterfazIndustrial

class MonitorIndustrial:
    def __init__(self):
        """Inicializar el monitor industrial"""
        self.config = Config()
        self.sispro = SISPROConnector(self.config)
        self.rs485 = MonitorRS485(self.config)
        self.barcode = BarcodeValidator()
        self.cache = CacheManager(self.config)
        self.database = DatabaseManager(self.config.config)
        self.estado = EstadoManager()
        self.interfaz = None

        # Estado del sistema
        self.estacion_actual = None
        self.orden_actual = None
        self.upc_validado = None
        self.contador_actual = 0
        self.lecturas_acumuladas = 0
        self.ultima_cantidad_sincronizada = 0
        self.ultima_sincronizacion = None
        self.receta_actual = None

        # Threads
        self.thread_rs485 = None
        self.thread_sincronizacion = None
        self.thread_estado = None
        self.running = False
        self._detenido = False

        # Configurar logging
        self.setup_logging()

    def setup_logging(self):
        """Configurar sistema de logging"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/monitor_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def inicializar(self):
        """Inicializar todos los componentes del sistema"""
        try:
            self.logger.info("INFO: Iniciando Monitor Industrial SISPRO")

            # 1. Cargar configuracion
            self.config.cargar()
            self.logger.info("SUCCESS: Configuracion cargada")

            # 2. Inicializar cache
            self.cache.inicializar()
            self.logger.info("SUCCESS: Cache inicializado")

            # 3. Conectar a SISPRO
            if not self.sispro.conectar():
                self.logger.error("ERROR: Error conectando a SISPRO")
                return False
            self.logger.info("SUCCESS: Conectado a SISPRO")

            # 4. Conectar a base de datos MySQL
            if not self.database.conectar():
                self.logger.error("ERROR: Error conectando a MySQL")
                return False
            self.logger.info("SUCCESS: Conectado a MySQL")

            # 4. Conectar RS485
            if not self.rs485.conectar():
                self.logger.error("ERROR: Error conectando RS485")
                return False
            self.logger.info("SUCCESS: RS485 conectado")

            # 5. Crear interfaz industrial
            self.interfaz = InterfazIndustrial(self)
            self.logger.info("SUCCESS: Interfaz industrial creada")

            return True

        except Exception as e:
            self.logger.error(f"ERROR: Error en inicializacion: {e}")
            return False

    def ejecutar(self):
        """Ejecutar el monitor industrial"""
        try:
            if not self.inicializar():
                return False

            self.running = True

            # Iniciar threads
            self.iniciar_threads()

            # Mostrar interfaz
            self.interfaz.mostrar()

        except KeyboardInterrupt:
            self.logger.info("INFO: Deteniendo monitor por interrupcion del usuario")
        except Exception as e:
            self.logger.error(f"ERROR: Error en ejecucion: {e}")
        finally:
            self.detener()

    def iniciar_threads(self):
        """Iniciar todos los threads del sistema"""
        # Thread de comunicación RS485
        self.thread_rs485 = threading.Thread(target=self.procesar_rs485, daemon=True)
        self.thread_rs485.start()

        # Thread de sincronización
        self.thread_sincronizacion = threading.Thread(target=self.sincronizar_periodicamente, daemon=True)
        self.thread_sincronizacion.start()

        # Thread de estado del Pico
        self.thread_estado = threading.Thread(target=self.monitorear_estado_pico, daemon=True)
        self.thread_estado.start()

        self.logger.info("SUCCESS: Threads iniciados")

    def procesar_rs485(self):
        """Procesar mensajes RS485 del Pico"""
        while self.running:
            try:
                from estado_manager import EstadoSistema
                if self.estado.estado_actual == EstadoSistema.PRODUCIENDO and self.upc_validado:
                    mensaje = self.rs485.leer_mensaje()
                    if mensaje:
                        self.procesar_mensaje_pico(mensaje)
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"ERROR: Error procesando RS485: {e}")
                time.sleep(1)

    def procesar_mensaje_pico(self, mensaje: str):
        """Procesar mensaje recibido del Pico"""
        try:
            partes = mensaje.strip().split(':')
            if len(partes) != 3:
                return

            device_id, tag, valor = partes
            valor = int(valor)

            if tag == 'CONT':
                # Actualizar contador local
                incremento = valor - self.lecturas_acumuladas
                self.lecturas_acumuladas = valor
                self.contador_actual = valor

                # Guardar lectura individual en cache (para velocidad de produccion)
                if incremento > 0:
                    self.cache.guardar_lectura({
                        'orden_fabricacion': self.orden_actual['ordenFabricacion'],
                        'upc': self.upc_validado,
                        'cantidad': incremento,
                        'timestamp': datetime.now(),
                        'fuente': 'RS485',
                        'sincronizada': False,
                        'estacion_id': self.estacion_actual['id'],
                        'usuario_id': self.config.get('sispro.usuario_id', 228),
                        'orden_fabricacion_id': self.orden_actual.get('id')
                    })

                # Actualizar interfaz
                if self.interfaz:
                    self.interfaz.actualizar_contador(valor)
                    # Actualizar última lectura del Pico
                    self.interfaz.actualizar_ultima_lectura(datetime.now())

                # Verificar si se alcanzó el 100% de la meta
                if self.orden_actual:
                    meta = self.orden_actual.get('cantidadFabricar', 0)
                    if meta > 0 and valor >= meta:
                        self.logger.info(f"SUCCESS: Meta alcanzada: {valor}/{meta}")
                        # Sincronizar inmediatamente
                        self.sincronizar_lecturas()
                        # Recargar ordenes para actualizar cantidades pendientes
                        if self.interfaz:
                            self.interfaz.cargar_ordenes()
                        # Finalizar orden automáticamente
                        self.finalizar_orden()

                self.logger.info(f"INFO: Conteo actualizado: {valor} (+{incremento})")

            elif tag == 'FIN':
                # Lectura completada
                self.logger.info(f"INFO: Lectura completada con {self.lecturas_acumuladas} unidades")

                # Sincronizar inmediatamente
                self.sincronizar_lecturas()

                # Recargar ordenes para actualizar cantidades pendientes
                if self.interfaz:
                    self.interfaz.cargar_ordenes()

                self.logger.info("SUCCESS: Lectura finalizada y sincronizada")

            elif tag == 'HEARTBEAT':
                # Actualizar estado del Pico
                self.estado.actualizar_estado_pico(device_id, 'ACTIVO')

            elif tag == 'INACTIVO':
                # Actualizar tiempo de inactividad
                self.estado.actualizar_tiempo_inactivo(device_id, valor)

        except Exception as e:
            self.logger.error(f"ERROR: Error procesando mensaje Pico: {e}")

    def sincronizar_periodicamente(self):
        """Sincronizar datos con SISPRO periodicamente"""
        while self.running:
            try:
                from estado_manager import EstadoSistema
                if self.estado.estado_actual == EstadoSistema.PRODUCIENDO and self.orden_actual:
                    self.sincronizar_lecturas()
                time.sleep(300)  # Cada 5 minutos
            except Exception as e:
                self.logger.error(f"ERROR: Error en sincronizacion: {e}")
                time.sleep(60)

    def sincronizar_lecturas(self):
        """Sincronizar lecturas acumuladas con MySQL"""
        try:
            # Verificar si hay datos para sincronizar
            if not self.orden_actual or not self.upc_validado:
                return

            # Obtener lecturas pendientes del cache
            lecturas_pendientes = self.cache.obtener_lecturas_pendientes(
                limite=self.config.get('lotes.tamaño_maximo', 100)
            )

            if not lecturas_pendientes:
                self.logger.info("INFO: No hay lecturas pendientes para sincronizar")
                return

            # Preparar datos para MySQL
            lecturas_mysql = []
            for lectura in lecturas_pendientes:
                lecturas_mysql.append({
                    'orden_fabricacion': lectura['orden_fabricacion'],
                    'upc': lectura['upc'],
                    'cantidad': lectura['cantidad'],
                    'timestamp': lectura['timestamp'],
                    'estacion_id': lectura['estacion_id'],
                    'usuario_id': lectura['usuario_id'],
                    'orden_fabricacion_id': lectura['orden_fabricacion_id']
                })

            # Cargar lecturas en lote a MySQL
            success, cantidad_cargada = self.database.cargar_lecturas_lote(lecturas_mysql)

            if success and cantidad_cargada > 0:
                # Actualizar ordenEstacion con las lecturas cargadas
                success_avance = self.database.actualizar_orden_estacion(
                    self.orden_actual['ordenFabricacion'],
                    self.estacion_actual['id']
                )

                if success_avance:
                    # Marcar lecturas como sincronizadas en cache
                    self.cache.marcar_como_sincronizadas(lecturas_pendientes)
                    self.ultima_cantidad_sincronizada = self.lecturas_acumuladas
                    self.ultima_sincronizacion = datetime.now()

                    # Actualizar avance en interfaz
                    avance = self.actualizar_avance_orden()

                    # Verificar si la orden esta completa
                    if avance and avance.get('cantidadPendiente', 0) == 0:
                        self.logger.info("INFO: Orden completada, finalizando automaticamente")
                        # Recargar ordenes para quitar la completa de la lista
                        if self.interfaz:
                            self.interfaz.cargar_ordenes()

                    self.logger.info(f"SUCCESS: {cantidad_cargada} lecturas cargadas en MySQL")
                else:
                    self.logger.warning("WARNING: Error actualizando ordenEstacion")
            else:
                self.logger.warning("WARNING: No se pudieron cargar las lecturas en MySQL")

        except Exception as e:
            self.logger.error(f"ERROR: Error sincronizando: {e}")

    def actualizar_avance_orden(self):
        """Actualizar avance de la orden en SISPRO"""
        try:
            avance = self.sispro.consultar_avance_orden(self.orden_actual['ordenFabricacion'])
            if avance:
                if self.interfaz:
                    self.interfaz.actualizar_avance(avance)
                return avance
            return None
        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando avance: {e}")
            return None

    def monitorear_estado_pico(self):
        """Monitorear estado del Pico"""
        while self.running:
            try:
                # Verificar estado del Pico
                estado_pico = self.estado.obtener_estado_pico()
                if (self.interfaz and
                    hasattr(self.interfaz, 'actualizar_estado_pico') and
                    hasattr(self.interfaz, 'estado_pico_var') and
                    self.interfaz.estado_pico_var is not None):
                    self.interfaz.actualizar_estado_pico(estado_pico)
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"ERROR: Error monitoreando Pico: {e}")
                time.sleep(10)

    def seleccionar_estacion(self):
        """Seleccionar estación de trabajo"""
        try:
            estaciones = self.sispro.obtener_estaciones()
            if not estaciones:
                messagebox.showerror("Error", "No se pudieron obtener las estaciones")
                return False

            # Mostrar diálogo de selección
            estacion = self.interfaz.mostrar_seleccion_estacion(estaciones)
            if estacion:
                self.estacion_actual = estacion
                self.config.guardar_estacion(estacion['id'])
                self.logger.info(f"SUCCESS: Estacion seleccionada: {estacion['nombre']}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"ERROR: Error seleccionando estacion: {e}")
            return False

    def seleccionar_orden(self):
        """Seleccionar orden de fabricación"""
        try:
            if not self.estacion_actual:
                return False

            ordenes = self.sispro.obtener_ordenes_asignadas(self.estacion_actual['id'])
            if not ordenes:
                messagebox.showwarning("Advertencia", "No hay órdenes asignadas a esta estación")
                return False

            # Mostrar diálogo de selección
            self.logger.info(f"INFO: Mostrando diálogo de selección con {len(ordenes)} órdenes")
            orden = self.interfaz.mostrar_seleccion_orden(ordenes)

            if orden:
                self.logger.info(f"INFO: Orden seleccionada del diálogo: {orden}")
                self.orden_actual = orden
                from estado_manager import EstadoSistema
                self.estado.cambiar_estado(EstadoSistema.ESPERANDO_UPC)

                # Cargar receta de la orden
                self.logger.info(f"INFO: Iniciando carga de receta para orden {orden['ordenFabricacion']}")
                self.cargar_receta_orden()

                self.logger.info(f"SUCCESS: Orden seleccionada: {orden['ordenFabricacion']}")
                return True
            else:
                self.logger.warning("WARNING: No se seleccionó ninguna orden")
                return False
            return False

        except Exception as e:
            self.logger.error(f"ERROR: Error seleccionando orden: {e}")
            return False

    def validar_upc(self, upc: str):
        """Validar código UPC"""
        try:
            if not self.orden_actual:
                return False

            # Validar UPC contra la orden
            if upc == self.orden_actual['ptUPC']:
                self.upc_validado = upc
                # Resetear contador para nueva orden
                self.contador_actual = 0
                self.lecturas_acumuladas = 0
                from estado_manager import EstadoSistema
                self.estado.cambiar_estado(EstadoSistema.PRODUCIENDO)

                # Activar comunicacion con Pico
                self.activar_pico()

                self.logger.info(f"SUCCESS: UPC validado: {upc}")
                return True
            else:
                self.logger.warning(f"WARNING: UPC invalido: {upc}")
                return False

        except Exception as e:
            self.logger.error(f"ERROR: Error validando UPC: {e}")
            return False

    def activar_pico(self):
        """Activar comunicacion con el Pico"""
        try:
            # Solicitar estado actual del Pico (HEARTBEAT tiene el contador)
            time.sleep(0.5)  # Esperar ultimo heartbeat

            # Revisar si hay lecturas previas del Pico
            contador_actual = self.lecturas_acumuladas

            # Si hay contador existente, alertar al operador
            if contador_actual > 0:
                from tkinter import messagebox
                respuesta = messagebox.askyesno(
                    "ALERTA - Contador Existente",
                    f"El dispositivo ya tiene {contador_actual} lecturas.\n\n"
                    f"¿Desea usar este conteo actual?\n\n"
                    f"SI = Continuar con {contador_actual}\n"
                    f"NO = Cancela y reinicia manualmente en el Pico\n\n"
                    f"(Para reiniciar: Presiona C en el teclado del Pico)",
                    icon='warning'
                )

                if respuesta:
                    # Usar contador actual
                    self.contador_actual = contador_actual
                    # Actualizar interfaz con el contador existente
                    if self.interfaz:
                        self.interfaz.actualizar_contador(contador_actual)
                    # Guardar lectura inicial
                    self.cache.guardar_lectura({
                        'orden_fabricacion': self.orden_actual['ordenFabricacion'],
                        'upc': self.upc_validado,
                        'cantidad': contador_actual,
                        'timestamp': datetime.now(),
                        'fuente': 'RS485_INICIAL'
                    })
                    self.logger.info(f"INFO: Usando contador existente: {contador_actual}")
                else:
                    # Cancelar y pedir que reinicie manualmente
                    messagebox.showinfo(
                        "Reinicio Manual Requerido",
                        "Por favor:\n\n"
                        "1. Ve al dispositivo Pico\n"
                        "2. Presiona tecla C (RESET)\n"
                        "3. Ingresa el PIN de supervisor\n"
                        "4. El contador se reiniciara a 0\n"
                        "5. Vuelve e intenta validar el UPC de nuevo"
                    )
                    from estado_manager import EstadoSistema
                    self.estado.cambiar_estado(EstadoSistema.ESPERANDO_UPC)
                    self.upc_validado = None
                    self.logger.info("INFO: Validacion cancelada - reinicio manual requerido")
                    return

            # Enviar comando de activacion al Pico
            comando = f"{self.estacion_actual['id']}:ACTIVAR:{self.orden_actual['pt']}"
            self.rs485.enviar_comando(comando)

            # Establecer meta
            meta_comando = f"{self.estacion_actual['id']}:META:{self.orden_actual['cantidadFabricar']}"
            self.rs485.enviar_comando(meta_comando)

            self.logger.info("SUCCESS: Pico activado")

        except Exception as e:
            self.logger.error(f"ERROR: Error activando Pico: {e}")

    def finalizar_orden(self):
        """Finalizar orden de fabricación"""
        try:
            if self.orden_actual:
                orden_numero = self.orden_actual['ordenFabricacion']
                
                # Sincronizar lecturas finales
                self.sincronizar_lecturas()

                # Cerrar orden en SISPRO
                self.sispro.cerrar_orden(
                    orden_numero,
                    self.estacion_actual['id']
                )

                # Desactivar Pico
                self.desactivar_pico()

                # Limpiar estado
                self.orden_actual = None
                self.upc_validado = None
                self.lecturas_acumuladas = 0
                self.ultima_cantidad_sincronizada = 0
                self.contador_actual = 0
                from estado_manager import EstadoSistema
                self.estado.cambiar_estado(EstadoSistema.INACTIVO)

                # Mostrar mensaje de finalización y limpiar interfaz
                if self.interfaz:
                    self.interfaz.mostrar_mensaje_exito(f"Orden {orden_numero} completada exitosamente")
                    self.interfaz.limpiar_interfaz_orden()
                    # Recargar órdenes para actualizar la lista
                    self.interfaz.cargar_ordenes()

                self.logger.info("SUCCESS: Orden finalizada")

        except Exception as e:
            self.logger.error(f"ERROR: Error finalizando orden: {e}")

    def desactivar_pico(self):
        """Desactivar comunicación con el Pico"""
        try:
            if self.estacion_actual:
                comando = f"{self.estacion_actual['id']}:DESACTIVAR:0"
                self.rs485.enviar_comando(comando)
                self.logger.info("SUCCESS: Pico desactivado")
        except Exception as e:
            self.logger.error(f"ERROR: Error desactivando Pico: {e}")

    def detener(self):
        """Detener el monitor industrial"""
        try:
            # Evitar doble llamada
            if hasattr(self, '_detenido') and self._detenido:
                return

            self._detenido = True
            self.running = False

            # Verificar si hay lecturas pendientes (antes de cerrar conexiones)
            try:
                lecturas_pendientes = self.cache.contar_lecturas_pendientes()

                if lecturas_pendientes > 0:
                    self.logger.warning(f"WARNING: Hay {lecturas_pendientes} lecturas pendientes de sincronizar")

                    # Intentar sincronizar una última vez
                    self.logger.info("INFO: Intentando sincronizar lecturas pendientes...")
                    self.sincronizar_lecturas()

                    # Verificar nuevamente
                    lecturas_restantes = self.cache.contar_lecturas_pendientes()

                    if lecturas_restantes > 0:
                        self.logger.error(f"ERROR: No se pudieron sincronizar {lecturas_restantes} lecturas")
                        self.logger.error("ERROR: Las lecturas se mantendrán en cache para la próxima ejecución")
                    else:
                        self.logger.info("SUCCESS: Todas las lecturas sincronizadas correctamente")
            except Exception as e:
                self.logger.warning(f"WARNING: No se pudo verificar lecturas pendientes: {e}")

            # Finalizar orden si esta activa
            from estado_manager import EstadoSistema
            if self.estado.estado_actual == EstadoSistema.PRODUCIENDO:
                self.finalizar_orden()

            # Desactivar Pico
            self.desactivar_pico()

            # Cerrar conexiones
            self.rs485.desconectar()
            self.sispro.desconectar()
            self.database.desconectar()
            self.cache.cerrar()

            self.logger.info("INFO: Monitor detenido")

        except Exception as e:
            self.logger.error(f"ERROR: Error deteniendo monitor: {e}")

    def cargar_receta_orden(self):
        """Cargar receta de la orden actual"""
        try:
            if not self.orden_actual:
                self.logger.warning("WARNING: No hay orden actual para cargar receta")
                return

            self.logger.info(f"INFO: Cargando receta para orden {self.orden_actual['ordenFabricacion']}")

            # Obtener receta desde SISPRO API
            receta_data = self.sispro.consultar_estatus_orden(self.orden_actual['ordenFabricacion'])

            self.logger.info(f"INFO: Respuesta de API: {receta_data is not None}")
            if receta_data:
                self.logger.info(f"INFO: Success: {receta_data.get('success')}")
                self.logger.info(f"INFO: Data presente: {receta_data.get('data') is not None}")

            if receta_data and receta_data.get('success') and receta_data.get('data'):
                self.receta_actual = receta_data['data']
                self.logger.info(f"INFO: Receta obtenida con {len(self.receta_actual.get('partidas', []))} partidas")

                if self.interfaz:
                    self.logger.info("INFO: Llamando a interfaz.mostrar_receta")
                    self.interfaz.mostrar_receta(self.receta_actual)
                    self.logger.info(f"SUCCESS: Receta cargada para orden {self.orden_actual['ordenFabricacion']}")
                else:
                    self.logger.warning("WARNING: No hay interfaz disponible para mostrar receta")
            else:
                self.logger.warning(f"WARNING: No se pudo cargar receta para orden {self.orden_actual['ordenFabricacion']}")
                if receta_data:
                    self.logger.warning(f"WARNING: Respuesta API: {receta_data}")

        except Exception as e:
            self.logger.error(f"ERROR: Error cargando receta: {e}")
            import traceback
            self.logger.error(f"ERROR: Traceback: {traceback.format_exc()}")

def main():
    """Función principal"""
    try:
        monitor = MonitorIndustrial()
        monitor.ejecutar()
    except Exception as e:
        print(f"ERROR: Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
