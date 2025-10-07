#!/usr/bin/env python3
"""
Gestor de Estados - Control de estados del sistema
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum

class EstadoSistema(Enum):
    INACTIVO = "INACTIVO"
    CONSULTANDO = "CONSULTANDO"
    ESPERANDO_UPC = "ESPERANDO_UPC"
    PRODUCIENDO = "PRODUCIENDO"
    PAUSADO = "PAUSADO"
    ERROR = "ERROR"
    SINCRONIZANDO = "SINCRONIZANDO"

class EstadoPico(Enum):
    DESCONECTADO = "DESCONECTADO"
    CONECTADO = "CONECTADO"
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    ERROR = "ERROR"

class EstadoManager:
    def __init__(self):
        self.estado_actual = EstadoSistema.INACTIVO
        self.estado_pico = {}
        self.estacion_actual = None
        self.orden_actual = None
        self.ultima_actividad = None
        self.errores_consecutivos = 0
        self.logger = logging.getLogger(__name__)

    def cambiar_estado(self, nuevo_estado: EstadoSistema):
        """Cambiar estado del sistema"""
        try:
            estado_anterior = self.estado_actual
            self.estado_actual = nuevo_estado
            self.ultima_actividad = datetime.now()

            self.logger.info(f"INFO: Estado cambiado: {estado_anterior.value} -> {nuevo_estado.value}")

            # Ejecutar acciones según el estado
            self._ejecutar_acciones_estado(nuevo_estado)

        except Exception as e:
            self.logger.error(f"ERROR: Error cambiando estado: {e}")

    def _ejecutar_acciones_estado(self, estado: EstadoSistema):
        """Ejecutar acciones según el estado"""
        try:
            if estado == EstadoSistema.INACTIVO:
                self._acciones_inactivo()
            elif estado == EstadoSistema.CONSULTANDO:
                self._acciones_consultando()
            elif estado == EstadoSistema.ESPERANDO_UPC:
                self._acciones_esperando_upc()
            elif estado == EstadoSistema.PRODUCIENDO:
                self._acciones_produciendo()
            elif estado == EstadoSistema.PAUSADO:
                self._acciones_pausado()
            elif estado == EstadoSistema.ERROR:
                self._acciones_error()
            elif estado == EstadoSistema.SINCRONIZANDO:
                self._acciones_sincronizando()

        except Exception as e:
            self.logger.error(f"ERROR: Error ejecutando acciones de estado: {e}")

    def _acciones_inactivo(self):
        """Acciones para estado INACTIVO"""
        self.errores_consecutivos = 0
        self.estacion_actual = None
        self.orden_actual = None

    def _acciones_consultando(self):
        """Acciones para estado CONSULTANDO"""
        pass

    def _acciones_esperando_upc(self):
        """Acciones para estado ESPERANDO_UPC"""
        pass

    def _acciones_produciendo(self):
        """Acciones para estado PRODUCIENDO"""
        pass

    def _acciones_pausado(self):
        """Acciones para estado PAUSADO"""
        pass

    def _acciones_error(self):
        """Acciones para estado ERROR"""
        self.errores_consecutivos += 1

    def _acciones_sincronizando(self):
        """Acciones para estado SINCRONIZANDO"""
        pass

    def actualizar_estado_pico(self, device_id: str, estado: str):
        """Actualizar estado del Pico"""
        try:
            self.estado_pico[device_id] = {
                'estado': estado,
                'ultima_actividad': datetime.now(),
                'tiempo_inactivo': 0
            }

            self.logger.debug(f"📡 Estado Pico {device_id}: {estado}")

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando estado Pico: {e}")

    def actualizar_tiempo_inactivo(self, device_id: str, tiempo: int):
        """Actualizar tiempo de inactividad del Pico"""
        try:
            if device_id in self.estado_pico:
                self.estado_pico[device_id]['tiempo_inactivo'] = tiempo
                self.estado_pico[device_id]['ultima_actividad'] = datetime.now()

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando tiempo inactivo: {e}")

    def obtener_estado_pico(self, device_id: str = None) -> Dict[str, Any]:
        """Obtener estado del Pico"""
        try:
            if device_id:
                return self.estado_pico.get(device_id, {
                    'estado': 'DESCONECTADO',
                    'ultima_actividad': None,
                    'tiempo_inactivo': 0
                })
            else:
                return self.estado_pico

        except Exception as e:
            self.logger.error(f"ERROR: Error obteniendo estado Pico: {e}")
            return {}

    def verificar_estado_pico(self, device_id: str) -> bool:
        """Verificar si el Pico está activo"""
        try:
            if device_id not in self.estado_pico:
                return False

            estado = self.estado_pico[device_id]
            ultima_actividad = estado.get('ultima_actividad')

            if not ultima_actividad:
                return False

            # Considerar inactivo si no hay actividad en los últimos 60 segundos
            tiempo_limite = datetime.now() - timedelta(seconds=60)
            return ultima_actividad > tiempo_limite

        except Exception as e:
            self.logger.error(f"ERROR: Error verificando estado Pico: {e}")
            return False

    def registrar_error(self, error: str):
        """Registrar error del sistema"""
        try:
            self.errores_consecutivos += 1
            self.logger.error(f"ERROR: Error #{self.errores_consecutivos}: {error}")

            # Si hay muchos errores consecutivos, cambiar a estado ERROR
            if self.errores_consecutivos >= 5:
                self.cambiar_estado(EstadoSistema.ERROR)

        except Exception as e:
            self.logger.error(f"ERROR: Error registrando error: {e}")

    def limpiar_errores(self):
        """Limpiar contador de errores"""
        self.errores_consecutivos = 0

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del estado"""
        try:
            return {
                'estado_actual': self.estado_actual.value,
                'estacion_actual': self.estacion_actual,
                'orden_actual': self.orden_actual,
                'ultima_actividad': self.ultima_actividad,
                'errores_consecutivos': self.errores_consecutivos,
                'estados_pico': self.estado_pico
            }

        except Exception as e:
            self.logger.error(f"ERROR: Error obteniendo estadísticas: {e}")
            return {}

    def es_estado_valido(self, estado: str) -> bool:
        """Verificar si un estado es válido"""
        try:
            return estado.upper() in [e.value for e in EstadoSistema]
        except:
            return False

    def obtener_estado_por_nombre(self, nombre: str) -> Optional[EstadoSistema]:
        """Obtener estado por nombre"""
        try:
            for estado in EstadoSistema:
                if estado.value.upper() == nombre.upper():
                    return estado
            return None
        except:
            return None

    def puede_cambiar_a(self, nuevo_estado: EstadoSistema) -> bool:
        """Verificar si se puede cambiar a un estado"""
        try:
            # Definir transiciones válidas
            transiciones_validas = {
                EstadoSistema.INACTIVO: [EstadoSistema.CONSULTANDO, EstadoSistema.ERROR],
                EstadoSistema.CONSULTANDO: [EstadoSistema.ESPERANDO_UPC, EstadoSistema.INACTIVO, EstadoSistema.ERROR],
                EstadoSistema.ESPERANDO_UPC: [EstadoSistema.PRODUCIENDO, EstadoSistema.INACTIVO, EstadoSistema.ERROR],
                EstadoSistema.PRODUCIENDO: [EstadoSistema.PAUSADO, EstadoSistema.INACTIVO, EstadoSistema.SINCRONIZANDO, EstadoSistema.ERROR],
                EstadoSistema.PAUSADO: [EstadoSistema.PRODUCIENDO, EstadoSistema.INACTIVO, EstadoSistema.ERROR],
                EstadoSistema.ERROR: [EstadoSistema.INACTIVO, EstadoSistema.CONSULTANDO],
                EstadoSistema.SINCRONIZANDO: [EstadoSistema.PRODUCIENDO, EstadoSistema.INACTIVO, EstadoSistema.ERROR]
            }

            return nuevo_estado in transiciones_validas.get(self.estado_actual, [])

        except Exception as e:
            self.logger.error(f"ERROR: Error verificando transición de estado: {e}")
            return False
