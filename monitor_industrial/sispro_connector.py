#!/usr/bin/env python3
"""
Conector SISPRO - Comunicación con APIs de Next.js
"""

import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

class SISPROConnector:
    def __init__(self, config):
        self.config = config
        self.base_url = config.sispro_base_url
        self.empresa_id = config.empresa_id
        self.usuario_id = config.usuario_id
        self.token = None
        self.session = None
        self.logger = logging.getLogger(__name__)

    def conectar(self) -> bool:
        """Conectar a SISPRO"""
        try:
            # Crear sesión HTTP
            self.session = aiohttp.ClientSession()

            # Autenticar
            return asyncio.run(self.autenticar())

        except Exception as e:
            self.logger.error(f"❌ Error conectando a SISPRO: {e}")
            return False

    async def autenticar(self) -> bool:
        """Autenticar con SISPRO"""
        try:
            # Por ahora, usar autenticación básica
            # En producción, implementar JWT
            self.token = "monitor_pi_token"
            self.logger.info("✅ Autenticado con SISPRO")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error autenticando: {e}")
            return False

    def desconectar(self):
        """Desconectar de SISPRO"""
        try:
            if self.session:
                asyncio.run(self.session.close())
            self.logger.info("✅ Desconectado de SISPRO")
        except Exception as e:
            self.logger.error(f"❌ Error desconectando: {e}")

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Realizar petición HTTP a SISPRO"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                'empresa-id': str(self.empresa_id),
                'Content-Type': 'application/json'
            }

            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

            kwargs['headers'] = headers

            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    self.logger.error(f"❌ Error HTTP {response.status}: {await response.text()}")
                    return None

        except Exception as e:
            self.logger.error(f"❌ Error en petición HTTP: {e}")
            return None

    def obtener_estaciones(self) -> List[Dict]:
        """Obtener estaciones de trabajo"""
        try:
            result = asyncio.run(self._make_request('GET', '/api/estacionesTrabajo'))
            if result and result.get('success'):
                return result.get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo estaciones: {e}")
            return []

    def obtener_ordenes_asignadas(self, estacion_id: int) -> List[Dict]:
        """Obtener órdenes asignadas a una estación"""
        try:
            params = {'estacionTrabajoId': estacion_id}
            result = asyncio.run(self._make_request(
                'GET',
                '/api/ordenesDeFabricacion/listarAsignadas',
                params=params
            ))
            if result and result.get('success'):
                return result.get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo órdenes: {e}")
            return []

    def registrar_lectura_upc(self, orden_fabricacion: str, upc: str, estacion_id: int, usuario_id: int) -> bool:
        """Registrar lectura UPC"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'upc': upc,
                'estacionId': estacion_id,
                'usuarioId': usuario_id
            }
            result = asyncio.run(self._make_request(
                'POST',
                '/api/lecturaUPC/registrar',
                json=data
            ))
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"❌ Error registrando lectura UPC: {e}")
            return False

    def consultar_avance_orden(self, orden_fabricacion: str) -> Optional[Dict]:
        """Consultar avance de una orden"""
        try:
            params = {'ordenFabricacion': orden_fabricacion}
            result = asyncio.run(self._make_request(
                'GET',
                '/api/ordenesDeFabricacion/avance',
                params=params
            ))
            if result and result.get('success'):
                return result.get('data')
            return None
        except Exception as e:
            self.logger.error(f"❌ Error consultando avance: {e}")
            return None

    def cambiar_prioridad_orden(self, orden_fabricacion: str, prioridad: str, estacion_id: int) -> bool:
        """Cambiar prioridad de una orden"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'prioridad': prioridad,
                'estacionId': estacion_id
            }
            result = asyncio.run(self._make_request(
                'POST',
                '/api/ordenesDeFabricacion/cambiarPrioridad',
                json=data
            ))
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"❌ Error cambiando prioridad: {e}")
            return False

    def cerrar_orden(self, orden_fabricacion: str, estacion_id: int) -> bool:
        """Cerrar una orden"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'estacionId': estacion_id
            }
            result = asyncio.run(self._make_request(
                'POST',
                '/api/ordenesDeFabricacion/cerrarOrden',
                json=data
            ))
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"❌ Error cerrando orden: {e}")
            return False

    def reabrir_orden(self, orden_fabricacion: str, estacion_id: int) -> bool:
        """Reabrir una orden"""
        try:
            data = {
                'ordenFabricacion': orden_fabricacion,
                'estacionId': estacion_id
            }
            result = asyncio.run(self._make_request(
                'POST',
                '/api/ordenesDeFabricacion/reabrirOrden',
                json=data
            ))
            return result and result.get('success', False)
        except Exception as e:
            self.logger.error(f"❌ Error reabriendo orden: {e}")
            return False

    def consultar_lecturas_upc(self, fecha_inicial: str, fecha_final: str, estacion_id: int) -> List[Dict]:
        """Consultar lecturas UPC"""
        try:
            params = {
                'fechaInicial': fecha_inicial,
                'fechaFinal': fecha_final,
                'estacionId': estacion_id
            }
            result = asyncio.run(self._make_request(
                'GET',
                '/api/lecturaUPC/consultar',
                params=params
            ))
            if result and result.get('success'):
                return result.get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"❌ Error consultando lecturas: {e}")
            return []

    def verificar_conexion(self) -> bool:
        """Verificar conexión con SISPRO"""
        try:
            result = asyncio.run(self._make_request('GET', '/api/estacionesTrabajo'))
            return result is not None
        except Exception as e:
            self.logger.error(f"❌ Error verificando conexión: {e}")
            return False
