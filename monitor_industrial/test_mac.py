#!/usr/bin/env python3
"""
Monitor Industrial SISPRO - Versión de Prueba para Mac
Simula hardware y permite probar toda la funcionalidad
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import os
import sys

# Importar módulos locales
from config_mac import Config
from barcode_validator import BarcodeValidator
from cache_manager_mac import CacheManager
from estado_manager import EstadoManager
from interfaz_industrial import InterfazIndustrial

class SimuladorRS485:
    """Simulador de comunicación RS485 para pruebas en Mac"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.contador = 0
        self.meta = 0
        self.activo = False
        self.device_id = "TEST001"

    def conectar(self) -> bool:
        """Simular conexión RS485"""
        self.running = True
        self.logger.info("✅ Simulador RS485 conectado (MODO PRUEBA)")
        return True

    def desconectar(self):
        """Simular desconexión RS485"""
        self.running = False
        self.logger.info("✅ Simulador RS485 desconectado")

    def leer_mensaje(self) -> Optional[str]:
        """Simular lectura de mensajes del Pico"""
        if not self.running or not self.activo:
            return None

        # Simular envío de mensajes cada 2-5 segundos
        if random.random() < 0.3:  # 30% de probabilidad
            self.contador += random.randint(1, 3)

            # Enviar diferentes tipos de mensajes
            mensajes = [
                f"{self.device_id}:CONT:{self.contador}",
                f"{self.device_id}:TOTAL:{self.contador}",
                f"{self.device_id}:ESTADO:1",
                f"{self.device_id}:HEARTBEAT:{int(time.time())}",
                f"{self.device_id}:INACTIVO:0"
            ]

            return random.choice(mensajes)

        return None

    def enviar_comando(self, comando: str) -> bool:
        """Simular envío de comandos al Pico"""
        self.logger.info(f"📤 Comando simulado: {comando}")

        # Procesar comandos simulados
        if "ACTIVAR" in comando:
            self.activo = True
            self.contador = 0
        elif "DESACTIVAR" in comando:
            self.activo = False
        elif "META" in comando:
            try:
                self.meta = int(comando.split(":")[-1])
            except:
                pass
        elif "RESET" in comando:
            self.contador = 0

        return True

    def activar_estacion(self, device_id: str, producto_id: str) -> bool:
        """Activar estación simulada"""
        comando = f"{device_id}:ACTIVAR:{producto_id}"
        return self.enviar_comando(comando)

    def desactivar_estacion(self, device_id: str) -> bool:
        """Desactivar estación simulada"""
        comando = f"{device_id}:DESACTIVAR:0"
        return self.enviar_comando(comando)

    def establecer_meta(self, device_id: str, cantidad: int) -> bool:
        """Establecer meta simulada"""
        comando = f"{device_id}:META:{cantidad}"
        return self.enviar_comando(comando)

class SimuladorSISPRO:
    """Simulador de SISPRO para pruebas en Mac"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.estaciones = [
            {
                "id": 1,
                "nombre": "Estación 001",
                "descripcion": "Estación de Prueba",
                "estado": "ASIGNADA",
                "coordinadorSupervisor": "Juan Pérez",
                "cuadrante": "Cuadrante A"
            },
            {
                "id": 2,
                "nombre": "Estación 002",
                "descripcion": "Estación de Prueba 2",
                "estado": "ASIGNADA",
                "coordinadorSupervisor": "María García",
                "cuadrante": "Cuadrante B"
            }
        ]

        self.ordenes = {
            1: [
                {
                    "id": 1,
                    "ordenFabricacion": "OF-001",
                    "pt": "PT-001",
                    "cantidadFabricar": 1000,
                    "cantidadPendiente": 1000,
                    "avance": 0.0,
                    "ptDescripcion": "Producto de Prueba A",
                    "ptPresentacion": "Caja x 10",
                    "ptUPC": "123456789012",
                    "estacionNombre": "Estación 001",
                    "estacionCoordinador": "Juan Pérez",
                    "estacionCuadrante": "Cuadrante A",
                    "prioridad": "NORMAL",
                    "isClosed": False
                },
                {
                    "id": 2,
                    "ordenFabricacion": "OF-002",
                    "pt": "PT-002",
                    "cantidadFabricar": 500,
                    "cantidadPendiente": 500,
                    "avance": 0.0,
                    "ptDescripcion": "Producto de Prueba B",
                    "ptPresentacion": "Caja x 5",
                    "ptUPC": "987654321098",
                    "estacionNombre": "Estación 001",
                    "estacionCoordinador": "Juan Pérez",
                    "estacionCuadrante": "Cuadrante A",
                    "prioridad": "ALTA",
                    "isClosed": False
                }
            ],
            2: [
                {
                    "id": 3,
                    "ordenFabricacion": "OF-003",
                    "pt": "PT-003",
                    "cantidadFabricar": 750,
                    "cantidadPendiente": 750,
                    "avance": 0.0,
                    "ptDescripcion": "Producto de Prueba C",
                    "ptPresentacion": "Caja x 15",
                    "ptUPC": "112233445566",
                    "estacionNombre": "Estación 002",
                    "estacionCoordinador": "María García",
                    "estacionCuadrante": "Cuadrante B",
                    "prioridad": "NORMAL",
                    "isClosed": False
                }
            ]
        }

        self.lecturas_registradas = []

    def conectar(self) -> bool:
        """Simular conexión a SISPRO"""
        self.logger.info("✅ Simulador SISPRO conectado (MODO PRUEBA)")
        return True

    def desconectar(self):
        """Simular desconexión de SISPRO"""
        self.logger.info("✅ Simulador SISPRO desconectado")

    def obtener_estaciones(self) -> List[Dict]:
        """Obtener estaciones simuladas"""
        return self.estaciones

    def obtener_ordenes_asignadas(self, estacion_id: int) -> List[Dict]:
        """Obtener órdenes asignadas simuladas"""
        return self.ordenes.get(estacion_id, [])

    def registrar_lectura_upc(self, orden_fabricacion: str, upc: str, estacion_id: int, usuario_id: int) -> bool:
        """Registrar lectura UPC simulada"""
        lectura = {
            "orden_fabricacion": orden_fabricacion,
            "upc": upc,
            "estacion_id": estacion_id,
            "usuario_id": usuario_id,
            "timestamp": datetime.now(),
            "cantidad": 1
        }
        self.lecturas_registradas.append(lectura)
        self.logger.info(f"📊 Lectura registrada: {lectura}")
        return True

    def consultar_avance_orden(self, orden_fabricacion: str) -> Optional[Dict]:
        """Consultar avance de orden simulado"""
        # Simular avance basado en lecturas registradas
        lecturas_orden = [l for l in self.lecturas_registradas if l["orden_fabricacion"] == orden_fabricacion]
        cantidad_leida = len(lecturas_orden)

        # Buscar orden para obtener meta
        for estacion_ordenes in self.ordenes.values():
            for orden in estacion_ordenes:
                if orden["ordenFabricacion"] == orden_fabricacion:
                    meta = orden["cantidadFabricar"]
                    avance = cantidad_leida / meta if meta > 0 else 0
                    return {
                        "cantidadPendiente": meta - cantidad_leida,
                        "avance": avance
                    }

        return None

    def cerrar_orden(self, orden_fabricacion: str, estacion_id: int) -> bool:
        """Cerrar orden simulada"""
        self.logger.info(f"✅ Orden cerrada: {orden_fabricacion}")
        return True

class MonitorIndustrialMac:
    """Monitor Industrial para Mac - Versión de Prueba"""

    def __init__(self):
        self.config = Config()
        self.sispro = SimuladorSISPRO(self.config)
        self.rs485 = SimuladorRS485(self.config)
        self.barcode = BarcodeValidator()
        self.cache = CacheManager(self.config)
        self.estado = EstadoManager()
        self.interfaz = None

        # Estado del sistema
        self.estacion_actual = None
        self.orden_actual = None
        self.upc_validado = None
        self.lecturas_acumuladas = 0
        self.ultima_sincronizacion = None

        # Threads
        self.thread_rs485 = None
        self.thread_sincronizacion = None
        self.thread_estado = None
        self.running = False

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
                logging.FileHandler(f'{log_dir}/monitor_mac_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def inicializar(self):
        """Inicializar todos los componentes del sistema"""
        try:
            self.logger.info("🚀 Iniciando Monitor Industrial SISPRO (MODO PRUEBA MAC)")

            # 1. Cargar configuración
            self.config.cargar()
            self.logger.info("✅ Configuración cargada")

            # 2. Inicializar cache (solo SQLite para Mac)
            self.cache.inicializar()
            self.logger.info("✅ Cache SQLite inicializado")

            # 3. Conectar a SISPRO (simulado)
            if not self.sispro.conectar():
                self.logger.error("❌ Error conectando a SISPRO")
                return False
            self.logger.info("✅ Conectado a SISPRO (simulado)")

            # 4. Conectar RS485 (simulado)
            if not self.rs485.conectar():
                self.logger.error("❌ Error conectando RS485")
                return False
            self.logger.info("✅ RS485 conectado (simulado)")

            # 5. Crear interfaz industrial (se creará en ejecutar())
            self.logger.info("✅ Interfaz industrial preparada")

            return True

        except Exception as e:
            self.logger.error(f"❌ Error en inicialización: {e}")
            return False

    def ejecutar(self):
        """Ejecutar el monitor industrial"""
        try:
            if not self.inicializar():
                return False

            self.running = True

            # Crear interfaz industrial
            self.interfaz = InterfazIndustrialMac(self)
            self.logger.info("✅ Interfaz industrial creada")

            # Mostrar interfaz (esto inicializa tkinter)
            self.interfaz.mostrar()

            # Iniciar threads después de que tkinter esté listo
            self.iniciar_threads()

            # Bucle principal
            self.interfaz.root.mainloop()

        except KeyboardInterrupt:
            self.logger.info("🛑 Deteniendo monitor por interrupción del usuario")
        except Exception as e:
            self.logger.error(f"❌ Error en ejecución: {e}")
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

        self.logger.info("✅ Threads iniciados")

    def procesar_rs485(self):
        """Procesar mensajes RS485 del Pico"""
        while self.running:
            try:
                if self.estado.estado_actual.value == "PRODUCIENDO" and self.upc_validado:
                    mensaje = self.rs485.leer_mensaje()
                    if mensaje:
                        self.procesar_mensaje_pico(mensaje)
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"❌ Error procesando RS485: {e}")
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
                self.lecturas_acumuladas = valor

                # Guardar en cache
                self.cache.guardar_lectura({
                    'orden_fabricacion': self.orden_actual['ordenFabricacion'],
                    'upc': self.upc_validado,
                    'cantidad': valor,
                    'timestamp': datetime.now(),
                    'fuente': 'RS485'
                })

                # Actualizar interfaz
                if self.interfaz:
                    self.interfaz.actualizar_contador(valor)

                self.logger.info(f"📊 Conteo actualizado: {valor}")

            elif tag == 'HEARTBEAT':
                # Actualizar estado del Pico
                self.estado.actualizar_estado_pico(device_id, 'ACTIVO')

            elif tag == 'INACTIVO':
                # Actualizar tiempo de inactividad
                self.estado.actualizar_tiempo_inactivo(device_id, valor)

        except Exception as e:
            self.logger.error(f"❌ Error procesando mensaje Pico: {e}")

    def sincronizar_periodicamente(self):
        """Sincronizar datos con SISPRO periódicamente"""
        while self.running:
            try:
                if self.estado.estado_actual.value == "PRODUCIENDO" and self.orden_actual:
                    self.sincronizar_lecturas()
                time.sleep(30)  # Cada 30 segundos para pruebas
            except Exception as e:
                self.logger.error(f"❌ Error en sincronización: {e}")
                time.sleep(10)

    def sincronizar_lecturas(self):
        """Sincronizar lecturas acumuladas con SISPRO"""
        try:
            lecturas_pendientes = self.cache.obtener_lecturas_pendientes()
            if not lecturas_pendientes:
                return

            # Agregar lecturas acumuladas
            cantidad_total = sum(lectura['cantidad'] for lectura in lecturas_pendientes)

            # Enviar a SISPRO
            success = self.sispro.registrar_lectura_upc(
                orden_fabricacion=self.orden_actual['ordenFabricacion'],
                upc=self.upc_validado,
                estacion_id=self.estacion_actual['id'],
                usuario_id=self.config.usuario_id
            )

            if success:
                # Marcar como sincronizadas
                self.cache.marcar_como_sincronizadas(lecturas_pendientes)
                self.ultima_sincronizacion = datetime.now()

                # Actualizar avance
                self.actualizar_avance_orden()

                self.logger.info(f"✅ Sincronizadas {len(lecturas_pendientes)} lecturas")
            else:
                self.logger.warning("⚠️ Error sincronizando lecturas")

        except Exception as e:
            self.logger.error(f"❌ Error sincronizando: {e}")

    def actualizar_avance_orden(self):
        """Actualizar avance de la orden en SISPRO"""
        try:
            avance = self.sispro.consultar_avance_orden(self.orden_actual['ordenFabricacion'])
            if avance and self.interfaz:
                self.interfaz.actualizar_avance(avance)
        except Exception as e:
            self.logger.error(f"❌ Error actualizando avance: {e}")

    def monitorear_estado_pico(self):
        """Monitorear estado del Pico"""
        while self.running:
            try:
                # Verificar estado del Pico
                estado_pico = self.estado.obtener_estado_pico()
                if self.interfaz:
                    self.interfaz.actualizar_estado_pico(estado_pico)
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"❌ Error monitoreando Pico: {e}")
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
                self.logger.info(f"✅ Estación seleccionada: {estacion['nombre']}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"❌ Error seleccionando estación: {e}")
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
            orden = self.interfaz.mostrar_seleccion_orden(ordenes)
            if orden:
                self.orden_actual = orden
                self.estado.cambiar_estado(EstadoManager.EstadoSistema.ESPERANDO_UPC)
                self.logger.info(f"✅ Orden seleccionada: {orden['ordenFabricacion']}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"❌ Error seleccionando orden: {e}")
            return False

    def validar_upc(self, upc: str):
        """Validar código UPC"""
        try:
            if not self.orden_actual:
                return False

            # Validar UPC contra la orden
            if upc == self.orden_actual['ptUPC']:
                self.upc_validado = upc
                self.estado.cambiar_estado(EstadoManager.EstadoSistema.PRODUCIENDO)

                # Activar comunicación con Pico
                self.activar_pico()

                self.logger.info(f"✅ UPC validado: {upc}")
                return True
            else:
                self.logger.warning(f"⚠️ UPC inválido: {upc}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error validando UPC: {e}")
            return False

    def activar_pico(self):
        """Activar comunicación con el Pico"""
        try:
            # Enviar comando de activación al Pico
            comando = f"{self.estacion_actual['id']}:ACTIVAR:{self.orden_actual['pt']}"
            self.rs485.enviar_comando(comando)

            # Establecer meta
            meta_comando = f"{self.estacion_actual['id']}:META:{self.orden_actual['cantidadFabricar']}"
            self.rs485.enviar_comando(meta_comando)

            self.logger.info("✅ Pico activado (simulado)")

        except Exception as e:
            self.logger.error(f"❌ Error activando Pico: {e}")

    def finalizar_orden(self):
        """Finalizar orden de fabricación"""
        try:
            if self.orden_actual:
                # Sincronizar lecturas finales
                self.sincronizar_lecturas()

                # Cerrar orden en SISPRO
                self.sispro.cerrar_orden(
                    self.orden_actual['ordenFabricacion'],
                    self.estacion_actual['id']
                )

                # Desactivar Pico
                self.desactivar_pico()

                # Limpiar estado
                self.orden_actual = None
                self.upc_validado = None
                self.lecturas_acumuladas = 0
                self.estado.cambiar_estado(EstadoManager.EstadoSistema.INACTIVO)

                self.logger.info("✅ Orden finalizada")

        except Exception as e:
            self.logger.error(f"❌ Error finalizando orden: {e}")

    def desactivar_pico(self):
        """Desactivar comunicación con el Pico"""
        try:
            comando = f"{self.estacion_actual['id']}:DESACTIVAR:0"
            self.rs485.enviar_comando(comando)
            self.logger.info("✅ Pico desactivado (simulado)")
        except Exception as e:
            self.logger.error(f"❌ Error desactivando Pico: {e}")

    def detener(self):
        """Detener el monitor industrial"""
        try:
            self.running = False

            # Finalizar orden si está activa
            if self.estado.estado_actual.value == "PRODUCIENDO":
                self.finalizar_orden()

            # Desactivar Pico
            self.desactivar_pico()

            # Cerrar conexiones
            self.rs485.desconectar()
            self.sispro.desconectar()
            self.cache.cerrar()

            self.logger.info("🛑 Monitor detenido")

        except Exception as e:
            self.logger.error(f"❌ Error deteniendo monitor: {e}")

class InterfazIndustrialMac(InterfazIndustrial):
    """Interfaz Industrial adaptada para Mac"""

    def __init__(self, monitor):
        super().__init__(monitor)
        # Configurar para Mac (no fullscreen por defecto)
        self.configurar_para_mac()

    def configurar_para_mac(self):
        """Configurar interfaz para Mac"""
        # Ajustar colores para mejor contraste en Mac
        self.colores['fondo'] = '#2b2b2b'
        self.colores['panel'] = '#3c3c3c'

    def configurar_ventana(self):
        """Configurar ventana principal para Mac"""
        try:
            self.root.title("Monitor Industrial SISPRO - MODO PRUEBA MAC")
            self.root.configure(bg=self.colores['fondo'])

            # No fullscreen por defecto en Mac para pruebas
            self.root.geometry("1200x800")
            self.root.attributes('-topmost', False)

            # Configurar teclas de salida
            self.root.bind('<Escape>', self.salir)
            self.root.bind('<Command-q>', self.salir)
            self.root.bind('<F11>', self.toggle_fullscreen)

            # Centrar ventana
            self.root.update_idletasks()
            width = 1200
            height = 800
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")

        except Exception as e:
            self.logger.error(f"❌ Error configurando ventana: {e}")

def main():
    """Función principal para Mac"""
    try:
        print("🍓 Monitor Industrial SISPRO - MODO PRUEBA MAC")
        print("=" * 50)
        print("Esta es una versión de prueba que simula:")
        print("- Comunicación RS485 con Pico")
        print("- APIs de SISPRO")
        print("- Lecturas de producción")
        print("=" * 50)
        print()

        monitor = MonitorIndustrialMac()
        monitor.ejecutar()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
