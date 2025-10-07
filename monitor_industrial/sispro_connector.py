#!/usr/bin/env python3
"""
Conector SISPRO - Comunicacion con APIs de Next.js
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

class SISPROConnector:
    def __init__(self, config):
        self.config = config
        self.base_url = config.sispro_base_url
        self.username = config.sispro_username
        self.password = config.sispro_password
        self.empresa_id = config.empresa_id
        self.usuario_id = config.usuario_id
        self.token = None
        self.session = None
        self.logger = logging.getLogger(__name__)

    def conectar(self) -> bool:
        """Conectar a SISPRO"""
        try:
            # Crear sesion HTTP
            self.session = requests.Session()

            # Autenticar
            return self.autenticar()

        except Exception as e:
            self.logger.error(f"ERROR: Error conectando a SISPRO: {e}")
            return False

    def autenticar(self) -> bool:
        """Autenticar con SISPRO usando JWT"""
        try:
            url = f"{self.base_url}/api/auth/login_local"

            payload = {
                "username": self.username,
                "password": self.password
            }

            headers = {
                'Content-Type': 'application/json',
                'empresa-id': str(self.empresa_id)
            }

            response = self.session.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token')
                    self.logger.info(f"SUCCESS: Autenticado con SISPRO - Token obtenido")
                    return True
                else:
                    self.logger.error(f"ERROR: Autenticacion fallida: {data.get('message', 'Sin mensaje')}")
                    return False
            else:
                self.logger.error(f"ERROR: HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"ERROR: Error autenticando: {e}")
            return False

    def desconectar(self):
        """Desconectar de SISPRO"""
        try:
            if self.session:
                self.session.close()
            self.logger.info("SUCCESS: Desconectado de SISPRO")
        except Exception as e:
            self.logger.error(f"ERROR: Error desconectando: {e}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Realizar peticion HTTP a SISPRO"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                'empresa-id': str(self.empresa_id),
                'Content-Type': 'application/json'
            }

            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

            kwargs['headers'] = headers
            kwargs['timeout'] = 30

            response = self.session.request(method, url, **kwargs)

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"ERROR: Error HTTP {response.status_code}: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"ERROR: Error en peticion HTTP: {e}")
            return None

    def obtener_estaciones(self) -> List[Dict]:
        """Obtener estaciones de trabajo"""
        try:
            result = self._make_request('GET', '/api/estacionesTrabajo')
            if result and result.get('success'):
                return result.get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Error obteniendo estaciones: {e}")
            return []

    def obtener_ordenes_asignadas(self, estacion_id: int) -> List[Dict]:
        """Obtener ordenes asignadas a una estacion"""
        try:
            params = {'estacionTrabajoId': estacion_id}
            result = self._make_request(
                'GET',
                '/api/ordenesDeFabricacion/listarAsignadas',
                params=params
            )
            if result and result.get('success'):
                return result.get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Error obteniendo ordenes: {e}")
            return []

    def registrar_lectura_upc(self, orden_fabricacion: str, upc: str, estacion_id: int, usuario_id: int, cantidad: int = 1) -> bool:
        """Registrar lectura UPC con cantidad"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'upc': upc,
                'estacionId': estacion_id,
                'usuarioId': usuario_id,
                'cantidad': cantidad
            }
            result = self._make_request(
                'POST',
                '/api/lecturaUPC/registrar',
                json=data
            )
            if result:
                self.logger.info(f"INFO: Lectura registrada - OF: {orden_fabricacion}, Cantidad: {cantidad}")
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"ERROR: Error registrando lectura UPC: {e}")
            return False

    def registrar_lectura_produccion(self, orden_fabricacion: str, estacion_id: int, usuario_id: int, cantidad: int) -> bool:
        """Registrar lectura de produccion RS485 (actualiza ordenEstacion)"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'estacionId': estacion_id,
                'usuarioId': usuario_id,
                'cantidad': cantidad,
                'fuente': 'RS485',
                'timestamp': datetime.now().isoformat()
            }
            result = self._make_request(
                'POST',
                '/api/ordenesDeFabricacion/registrarLecturaRS485',
                json=data
            )
            if result:
                self.logger.info(f"INFO: Produccion registrada - OF: {orden_fabricacion}, Cantidad: {cantidad}")
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"ERROR: Error registrando produccion: {e}")
            return False

    def consultar_avance_orden(self, orden_fabricacion: str) -> Optional[Dict]:
        """Consultar avance de una orden"""
        try:
            params = {'ordenFabricacion': orden_fabricacion}
            result = self._make_request(
                'GET',
                '/api/ordenesDeFabricacion/avance',
                params=params
            )
            if result and result.get('success'):
                return result.get('data')
            return None
        except Exception as e:
            self.logger.error(f"ERROR: Error consultando avance: {e}")
            return None

    def cambiar_prioridad_orden(self, orden_fabricacion: str, prioridad: str, estacion_id: int) -> bool:
        """Cambiar prioridad de una orden"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'prioridad': prioridad,
                'estacionId': estacion_id
            }
            result = self._make_request(
                'POST',
                '/api/ordenesDeFabricacion/cambiarPrioridad',
                json=data
            )
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"ERROR: Error cambiando prioridad: {e}")
            return False

    def cerrar_orden(self, orden_fabricacion: str, estacion_id: int) -> bool:
        """Cerrar una orden"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'estacionId': estacion_id
            }
            result = self._make_request(
                'POST',
                '/api/ordenesDeFabricacion/cerrarOrden',
                json=data
            )
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"ERROR: Error cerrando orden: {e}")
            return False

    def reabrir_orden(self, orden_fabricacion: str, estacion_id: int) -> bool:
        """Reabrir una orden"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'estacionId': estacion_id
            }
            result = self._make_request(
                'POST',
                '/api/ordenesDeFabricacion/reabrirOrden',
                json=data
            )
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"ERROR: Error reabriendo orden: {e}")
            return False

    def consultar_lecturas_upc(self, fecha_inicial: str, fecha_final: str, estacion_id: int) -> List[Dict]:
        """Consultar lecturas UPC"""
        try:
            params = {
                'fechaInicial': fecha_inicial,
                'fechaFinal': fecha_final,
                'estacionId': estacion_id
            }
            result = self._make_request(
                'GET',
                '/api/lecturaUPC/consultar',
                params=params
            )
            if result and result.get('success'):
                return result.get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Error consultando lecturas: {e}")
            return []

    def verificar_conexion(self) -> bool:
        """Verificar conexion con SISPRO"""
        try:
            result = self._make_request('GET', '/api/estacionesTrabajo')
            return result is not None
        except Exception as e:
            self.logger.error(f"ERROR: Error verificando conexion: {e}")
            return False
