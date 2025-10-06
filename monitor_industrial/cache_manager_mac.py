#!/usr/bin/env python3
"""
Gestor de Cache para Mac - Solo SQLite (sin Redis)
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import threading

class CacheManager:
    def __init__(self, config):
        self.config = config
        self.sqlite_conn = None
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()

    def inicializar(self):
        """Inicializar cache SQLite"""
        try:
            # Inicializar SQLite
            self.sqlite_conn = sqlite3.connect(
                self.config.sqlite_file,
                check_same_thread=False
            )
            self.sqlite_conn.row_factory = sqlite3.Row

            # Crear tablas si no existen
            self.crear_tablas()
            self.logger.info("✅ SQLite inicializado (MODO MAC)")

        except Exception as e:
            self.logger.error(f"❌ Error inicializando cache: {e}")
            raise

    def crear_tablas(self):
        """Crear tablas de SQLite si no existen"""
        try:
            cursor = self.sqlite_conn.cursor()

            # Tabla de lecturas de producción
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lecturas_produccion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    orden_fabricacion TEXT NOT NULL,
                    upc TEXT NOT NULL,
                    cantidad INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    fuente TEXT NOT NULL,
                    sincronizada BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de estado de estaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estado_estaciones (
                    estacion_id TEXT PRIMARY KEY,
                    estado TEXT NOT NULL,
                    orden_actual TEXT,
                    contador INTEGER DEFAULT 0,
                    meta INTEGER DEFAULT 0,
                    ultima_actividad DATETIME,
                    tiempo_inactivo INTEGER DEFAULT 0,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de configuración
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Índices para optimizar consultas
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_lecturas_orden
                ON lecturas_produccion(orden_fabricacion)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_lecturas_sincronizada
                ON lecturas_produccion(sincronizada)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_lecturas_timestamp
                ON lecturas_produccion(timestamp)
            ''')

            self.sqlite_conn.commit()
            self.logger.info("✅ Tablas de SQLite creadas")

        except Exception as e:
            self.logger.error(f"❌ Error creando tablas: {e}")
            raise

    def guardar_lectura(self, lectura: Dict[str, Any]):
        """Guardar lectura de producción"""
        try:
            with self.lock:
                # Guardar en SQLite
                cursor = self.sqlite_conn.cursor()
                cursor.execute('''
                    INSERT INTO lecturas_produccion
                    (orden_fabricacion, upc, cantidad, timestamp, fuente)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    lectura['orden_fabricacion'],
                    lectura['upc'],
                    lectura['cantidad'],
                    lectura['timestamp'],
                    lectura['fuente']
                ))
                self.sqlite_conn.commit()

                self.logger.debug(f"📊 Lectura guardada: {cursor.lastrowid}")

        except Exception as e:
            self.logger.error(f"❌ Error guardando lectura: {e}")

    def obtener_lecturas_pendientes(self) -> List[Dict[str, Any]]:
        """Obtener lecturas pendientes de sincronización"""
        try:
            with self.lock:
                cursor = self.sqlite_conn.cursor()
                cursor.execute('''
                    SELECT * FROM lecturas_produccion
                    WHERE sincronizada = FALSE
                    ORDER BY timestamp ASC
                ''')

                lecturas = []
                for row in cursor.fetchall():
                    lecturas.append({
                        'id': row['id'],
                        'orden_fabricacion': row['orden_fabricacion'],
                        'upc': row['upc'],
                        'cantidad': row['cantidad'],
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'fuente': row['fuente']
                    })

                return lecturas

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo lecturas pendientes: {e}")
            return []

    def marcar_como_sincronizadas(self, lecturas: List[Dict[str, Any]]):
        """Marcar lecturas como sincronizadas"""
        try:
            with self.lock:
                if not lecturas:
                    return

                ids = [lectura['id'] for lectura in lecturas]
                placeholders = ','.join(['?' for _ in ids])

                cursor = self.sqlite_conn.cursor()
                cursor.execute(f'''
                    UPDATE lecturas_produccion
                    SET sincronizada = TRUE
                    WHERE id IN ({placeholders})
                ''', ids)
                self.sqlite_conn.commit()

                self.logger.info(f"✅ {len(lecturas)} lecturas marcadas como sincronizadas")

        except Exception as e:
            self.logger.error(f"❌ Error marcando lecturas como sincronizadas: {e}")

    def guardar_estado_estacion(self, estacion_id: str, estado: Dict[str, Any]):
        """Guardar estado de una estación"""
        try:
            with self.lock:
                cursor = self.sqlite_conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO estado_estaciones
                    (estacion_id, estado, orden_actual, contador, meta, ultima_actividad, tiempo_inactivo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    estacion_id,
                    estado.get('estado', 'INACTIVO'),
                    estado.get('orden_actual'),
                    estado.get('contador', 0),
                    estado.get('meta', 0),
                    estado.get('ultima_actividad'),
                    estado.get('tiempo_inactivo', 0)
                ))
                self.sqlite_conn.commit()

        except Exception as e:
            self.logger.error(f"❌ Error guardando estado estación: {e}")

    def obtener_estado_estacion(self, estacion_id: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de una estación"""
        try:
            with self.lock:
                cursor = self.sqlite_conn.cursor()
                cursor.execute('''
                    SELECT * FROM estado_estaciones
                    WHERE estacion_id = ?
                ''', (estacion_id,))

                row = cursor.fetchone()
                if row:
                    return {
                        'estado': row['estado'],
                        'orden_actual': row['orden_actual'],
                        'contador': row['contador'],
                        'meta': row['meta'],
                        'ultima_actividad': row['ultima_actividad'],
                        'tiempo_inactivo': row['tiempo_inactivo']
                    }

            return None

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo estado estación: {e}")
            return None

    def limpiar_lecturas_antiguas(self, dias: int = 7):
        """Limpiar lecturas antiguas ya sincronizadas"""
        try:
            with self.lock:
                fecha_limite = datetime.now() - timedelta(days=dias)

                cursor = self.sqlite_conn.cursor()
                cursor.execute('''
                    DELETE FROM lecturas_produccion
                    WHERE sincronizada = TRUE
                    AND timestamp < ?
                ''', (fecha_limite,))

                eliminadas = cursor.rowcount
                self.sqlite_conn.commit()

                if eliminadas > 0:
                    self.logger.info(f"🧹 {eliminadas} lecturas antiguas eliminadas")

        except Exception as e:
            self.logger.error(f"❌ Error limpiando lecturas antiguas: {e}")

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        try:
            with self.lock:
                cursor = self.sqlite_conn.cursor()

                # Total de lecturas
                cursor.execute('SELECT COUNT(*) FROM lecturas_produccion')
                total_lecturas = cursor.fetchone()[0]

                # Lecturas pendientes
                cursor.execute('SELECT COUNT(*) FROM lecturas_produccion WHERE sincronizada = FALSE')
                lecturas_pendientes = cursor.fetchone()[0]

                # Lecturas por fuente
                cursor.execute('''
                    SELECT fuente, COUNT(*)
                    FROM lecturas_produccion
                    GROUP BY fuente
                ''')
                lecturas_por_fuente = dict(cursor.fetchall())

                return {
                    'total_lecturas': total_lecturas,
                    'lecturas_pendientes': lecturas_pendientes,
                    'lecturas_sincronizadas': total_lecturas - lecturas_pendientes,
                    'lecturas_por_fuente': lecturas_por_fuente
                }

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

    def cerrar(self):
        """Cerrar conexiones"""
        try:
            if self.sqlite_conn:
                self.sqlite_conn.close()
            self.logger.info("✅ Cache cerrado")
        except Exception as e:
            self.logger.error(f"❌ Error cerrando cache: {e}")
