#!/usr/bin/env python3
"""
Validador de Códigos de Barras UPC
"""

import re
import logging
from typing import Optional, Dict, Any

class BarcodeValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validar_formato_upc(self, upc: str) -> bool:
        """Validar formato básico de UPC"""
        try:
            # Limpiar código
            upc_limpio = re.sub(r'[^0-9]', '', upc)

            # Verificar longitud (UPC-12 o UPC-13)
            if len(upc_limpio) not in [12, 13]:
                return False

            # Verificar que sean solo números
            if not upc_limpio.isdigit():
                return False

            return True

        except Exception as e:
            self.logger.error(f"ERROR: Error validando formato UPC: {e}")
            return False

    def validar_upc_contra_orden(self, upc: str, orden: Dict[str, Any]) -> bool:
        """Validar UPC contra la orden de fabricación"""
        try:
            if not self.validar_formato_upc(upc):
                return False

            # Obtener UPC esperado de la orden
            upc_esperado = orden.get('ptUPC', '')
            if not upc_esperado:
                self.logger.warning("WARNING: Orden sin UPC especificado")
                return False

            # Comparar UPCs
            upc_limpio = re.sub(r'[^0-9]', '', upc)
            upc_esperado_limpio = re.sub(r'[^0-9]', '', upc_esperado)

            if upc_limpio == upc_esperado_limpio:
                self.logger.info(f"SUCCESS: UPC valido: {upc} coincide con orden {orden.get('ordenFabricacion')}")
                return True
            else:
                self.logger.warning(f"WARNING: UPC invalido: {upc} no coincide con {upc_esperado}")
                return False

        except Exception as e:
            self.logger.error(f"ERROR: Error validando UPC contra orden: {e}")
            return False

    def extraer_informacion_upc(self, upc: str) -> Dict[str, Any]:
        """Extraer información del código UPC"""
        try:
            upc_limpio = re.sub(r'[^0-9]', '', upc)

            info = {
                'upc_original': upc,
                'upc_limpio': upc_limpio,
                'longitud': len(upc_limpio),
                'tipo': 'UPC-12' if len(upc_limpio) == 12 else 'UPC-13' if len(upc_limpio) == 13 else 'DESCONOCIDO'
            }

            # Para UPC-12, extraer información básica
            if len(upc_limpio) == 12:
                info['codigo_empresa'] = upc_limpio[:6]
                info['codigo_producto'] = upc_limpio[6:11]
                info['digito_verificacion'] = upc_limpio[11]

            return info

        except Exception as e:
            self.logger.error(f"ERROR: Error extrayendo informacion UPC: {e}")
            return {}

    def calcular_digito_verificacion(self, upc: str) -> Optional[str]:
        """Calcular dígito de verificación para UPC-12"""
        try:
            upc_limpio = re.sub(r'[^0-9]', '', upc)

            if len(upc_limpio) != 11:
                return None

            # Algoritmo de dígito de verificación UPC
            suma_impares = sum(int(upc_limpio[i]) for i in range(0, 11, 2))
            suma_pares = sum(int(upc_limpio[i]) for i in range(1, 11, 2))

            total = suma_impares * 3 + suma_pares
            digito_verificacion = (10 - (total % 10)) % 10

            return str(digito_verificacion)

        except Exception as e:
            self.logger.error(f"ERROR: Error calculando digito de verificacion: {e}")
            return None

    def validar_digito_verificacion(self, upc: str) -> bool:
        """Validar dígito de verificación de UPC"""
        try:
            upc_limpio = re.sub(r'[^0-9]', '', upc)

            if len(upc_limpio) != 12:
                return False

            # Calcular dígito de verificación esperado
            digito_esperado = self.calcular_digito_verificacion(upc_limpio[:11])

            if digito_esperado and upc_limpio[11] == digito_esperado:
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"ERROR: Error validando digito de verificacion: {e}")
            return False

    def normalizar_upc(self, upc: str) -> str:
        """Normalizar código UPC"""
        try:
            # Limpiar y normalizar
            upc_limpio = re.sub(r'[^0-9]', '', upc)

            # Agregar ceros al inicio si es necesario para UPC-12
            if len(upc_limpio) < 12:
                upc_limpio = upc_limpio.zfill(12)
            elif len(upc_limpio) > 12:
                upc_limpio = upc_limpio[-12:]

            return upc_limpio

        except Exception as e:
            self.logger.error(f"ERROR: Error normalizando UPC: {e}")
            return upc
