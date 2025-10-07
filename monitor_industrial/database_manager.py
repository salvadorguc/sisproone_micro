"""
Database Manager - Conexion directa a MySQL
Maneja la carga de lecturas en lotes y actualizacion de ordenEstacion
"""

import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import hashlib
import json

class DatabaseManager:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.cursor = None

    def conectar(self) -> bool:
        """Conectar a la base de datos MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                user=self.config['database']['username'],
                password=self.config['database']['password'],
                database=self.config['database']['database'],
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                self.logger.info("SUCCESS: Conectado a MySQL")
                return True
            else:
                self.logger.error("ERROR: No se pudo conectar a MySQL")
                return False

        except Error as e:
            self.logger.error(f"ERROR: Error conectando a MySQL: {e}")
            return False

    def desconectar(self):
        """Desconectar de la base de datos"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
            self.logger.info("SUCCESS: Desconectado de MySQL")
        except Error as e:
            self.logger.error(f"ERROR: Error desconectando de MySQL: {e}")

    def generar_indice_unico(self, orden_fabricacion: str, upc: str, timestamp: datetime, estacion_id: int) -> str:
        """Generar indice unico para evitar duplicados"""
        # Combinar datos para crear hash unico
        data_string = f"{orden_fabricacion}_{upc}_{timestamp.isoformat()}_{estacion_id}"
        return hashlib.md5(data_string.encode()).hexdigest()[:16]

    def cargar_lecturas_lote(self, lecturas: List[Dict]) -> Tuple[bool, int]:
        """
        Cargar lecturas en lote a la tabla lecturaUPC
        Retorna: (exito, cantidad_cargada)
        """
        if not lecturas:
            return True, 0

        try:
            if not self.connection or not self.connection.is_connected():
                if not self.conectar():
                    return False, 0

            # Preparar datos para insercion
            datos_insercion = []
            for lectura in lecturas:
                indice = self.generar_indice_unico(
                    lectura['orden_fabricacion'],
                    lectura['upc'],
                    lectura['timestamp'],
                    lectura['estacion_id']
                )

                datos_insercion.append((
                    lectura['upc'],
                    lectura['timestamp'].date(),
                    lectura['timestamp'].time(),
                    lectura['usuario_id'],
                    lectura['orden_fabricacion_id'],
                    lectura['hora_lectura'],
                    lectura['estacion_id'],
                    lectura['orden_fabricacion'],
                    indice
                ))

            # Query de insercion con manejo de duplicados
            query = """
            INSERT IGNORE INTO lecturaUPC
            (upc, fechaLectura, horaLectura, usuarioId, ordenFabricacionId,
             fechaLectura, estacionId, ordenFabricacion, indice)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Ejecutar insercion en lote
            self.cursor.executemany(query, datos_insercion)
            filas_afectadas = self.cursor.rowcount

            # Confirmar transaccion
            self.connection.commit()

            self.logger.info(f"SUCCESS: {filas_afectadas} lecturas cargadas en lote")
            return True, filas_afectadas

        except Error as e:
            if self.connection:
                self.connection.rollback()
            self.logger.error(f"ERROR: Error cargando lecturas en lote: {e}")
            return False, 0

    def actualizar_orden_estacion(self, orden_fabricacion: str, estacion_id: int) -> bool:
        """
        Actualizar cantidadPendiente y avance en ordenEstacion
        basado en las lecturas cargadas
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.conectar():
                    return False

            # Obtener datos actuales de la orden
            query_orden = """
            SELECT cantidadFabricar, cantidadPendiente, avance
            FROM ordenEstacion
            WHERE ordenFabricacion = %s AND estacionId = %s
            """

            self.cursor.execute(query_orden, (orden_fabricacion, estacion_id))
            orden_actual = self.cursor.fetchone()

            if not orden_actual:
                self.logger.warning(f"WARNING: Orden {orden_fabricacion} no encontrada en estacion {estacion_id}")
                return False

            # Contar lecturas cargadas para esta orden
            query_lecturas = """
            SELECT COUNT(*) as total_lecturas, SUM(1) as cantidad_leida
            FROM lecturaUPC
            WHERE ordenFabricacion = %s AND estacionId = %s
            """

            self.cursor.execute(query_lecturas, (orden_fabricacion, estacion_id))
            lecturas_data = self.cursor.fetchone()

            cantidad_leida = lecturas_data['cantidad_leida'] or 0
            cantidad_fabricar = orden_actual['cantidadFabricar']
            cantidad_pendiente_actual = orden_actual['cantidadPendiente']

            # Calcular nueva cantidad pendiente (no puede ser negativa)
            nueva_cantidad_pendiente = max(0, cantidad_pendiente_actual - cantidad_leida)

            # Calcular nuevo avance (1 = 100%, maximo 4 decimales)
            nuevo_avance = min(1.0, round(cantidad_leida / cantidad_fabricar, 4))

            # Actualizar ordenEstacion
            query_update = """
            UPDATE ordenEstacion
            SET cantidadPendiente = %s,
                avance = %s,
                updatedAt = NOW()
            WHERE ordenFabricacion = %s AND estacionId = %s
            """

            self.cursor.execute(query_update, (
                nueva_cantidad_pendiente,
                nuevo_avance,
                orden_fabricacion,
                estacion_id
            ))

            # Confirmar transaccion
            self.connection.commit()

            self.logger.info(f"SUCCESS: Orden {orden_fabricacion} actualizada - "
                           f"Pendiente: {nueva_cantidad_pendiente}, Avance: {nuevo_avance}")

            return True

        except Error as e:
            if self.connection:
                self.connection.rollback()
            self.logger.error(f"ERROR: Error actualizando ordenEstacion: {e}")
            return False

    def obtener_receta_orden(self, orden_fabricacion: str) -> Optional[Dict]:
        """Obtener receta de la orden de fabricacion"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.conectar():
                    return None

            # Query para obtener datos de la orden y sus partidas
            query = """
            SELECT
                of.ordenFabricacion,
                of.estatus,
                of.fechaInicio,
                of.fechaFin,
                of.cliente,
                of.razonSocial,
                of.articuloPT,
                of.descripcionPT,
                of.cantidadPlanificada,
                of.caja,
                GROUP_CONCAT(
                    CONCAT(op.articuloMP, '|', op.descripcionMP, '|', op.cantidad)
                    SEPARATOR '||'
                ) as partidas
            FROM ordenesDeFabricacion of
            LEFT JOIN ordenesDeFabricacionPartidas op ON of.id = op.ordenFabricacionId
            WHERE of.ordenFabricacion = %s
            GROUP BY of.id
            """

            self.cursor.execute(query, (orden_fabricacion,))
            resultado = self.cursor.fetchone()

            if not resultado:
                return None

            # Procesar partidas
            partidas = []
            if resultado['partidas']:
                for partida_str in resultado['partidas'].split('||'):
                    if partida_str:
                        articulo, descripcion, cantidad = partida_str.split('|')
                        partidas.append({
                            'articuloMP': articulo,
                            'descripcionMP': descripcion,
                            'cantidad': int(cantidad)
                        })

            receta = {
                'ordenFabricacion': resultado['ordenFabricacion'],
                'estatus': resultado['estatus'],
                'fechaInicio': resultado['fechaInicio'],
                'fechaFin': resultado['fechaFin'],
                'cliente': resultado['cliente'],
                'razonSocial': resultado['razonSocial'],
                'articuloPT': resultado['articuloPT'],
                'descripcionPT': resultado['descripcionPT'],
                'cantidadPlanificada': resultado['cantidadPlanificada'],
                'caja': resultado['caja'],
                'partidas': partidas
            }

            return receta

        except Error as e:
            self.logger.error(f"ERROR: Error obteniendo receta: {e}")
            return None

    def verificar_lecturas_pendientes(self, orden_fabricacion: str, estacion_id: int) -> int:
        """Verificar cuantas lecturas estan pendientes de cargar"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.conectar():
                    return 0

            query = """
            SELECT COUNT(*) as pendientes
            FROM lecturaUPC
            WHERE ordenFabricacion = %s AND estacionId = %s
            """

            self.cursor.execute(query, (orden_fabricacion, estacion_id))
            resultado = self.cursor.fetchone()

            return resultado['pendientes'] if resultado else 0

        except Error as e:
            self.logger.error(f"ERROR: Error verificando lecturas pendientes: {e}")
            return 0
