#!/usr/bin/env python3
"""
Gestor de Cache - Redis + SQLite
"""

import redis
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import threading

class CacheManager:
    def __init__(self, config):
        self.config = config
        self.redis_client = None
        self.sqlite_conn = None
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()

    def inicializar(self):
        """Inicializar cache Redis y SQLite"""
        try:
            # Conectar a Redis
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                password=self.config.redis_password if self.config.redis_password else None,
                db=self.config.redis_db,
                decode_responses=True
            )

            # Verificar conexión Redis
            self.redis_client.ping()
            self.logger.info("SUCCESS: Redis conectado")

            # Inicializar SQLite
            self.sqlite_conn = sqlite3.connect(
                self.config.sqlite_file,
                check_same_thread=False
            )
            self.sqlite_conn.row_factory = sqlite3.Row

            # Crear tablas si no existen
            self.crear_tablas()
            self.logger.info("SUCCESS: SQLite inicializado")

        except Exception as e:
            self.logger.error(f"ERROR: Error inicializando cache: {e}")
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
                    estacion_id INTEGER,
                    usuario_id INTEGER,
                    orden_fabricacion_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Agregar columnas si no existen (para bases de datos existentes)
            try:
                cursor.execute('ALTER TABLE lecturas_produccion ADD COLUMN estacion_id INTEGER')
            except:
                pass  # Columna ya existe

            try:
                cursor.execute('ALTER TABLE lecturas_produccion ADD COLUMN usuario_id INTEGER')
            except:
                pass  # Columna ya existe

            try:
                cursor.execute('ALTER TABLE lecturas_produccion ADD COLUMN orden_fabricacion_id INTEGER')
            except:
                pass  # Columna ya existe

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
            self.logger.info("SUCCESS: Tablas de SQLite creadas")

        except Exception as e:
            self.logger.error(f"ERROR: Error creando tablas: {e}")
            raise

    def guardar_lectura(self, lectura: Dict[str, Any]):
        """Guardar lectura de producción"""
        try:
            with self.lock:
                # Agregar timestamp si no existe
                if 'timestamp' not in lectura:
                    lectura['timestamp'] = datetime.now()

                # Guardar en SQLite (persistencia)
                cursor = self.sqlite_conn.cursor()
                cursor.execute('''
                    INSERT INTO lecturas_produccion
                    (orden_fabricacion, upc, cantidad, timestamp, fuente, sincronizada, estacion_id, usuario_id, orden_fabricacion_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    lectura['orden_fabricacion'],
                    lectura['upc'],
                    lectura['cantidad'],
                    lectura['timestamp'],
                    lectura['fuente'],
                    lectura.get('sincronizada', False),
                    lectura.get('estacion_id'),
                    lectura.get('usuario_id'),
                    lectura.get('orden_fabricacion_id')
                ))
                self.sqlite_conn.commit()

                # Guardar en Redis (acceso rápido)
                lectura_id = cursor.lastrowid
                redis_key = f"lectura:{lectura_id}"
                self.redis_client.hset(redis_key, mapping={
                    'id': lectura_id,
                    'orden_fabricacion': lectura['orden_fabricacion'],
                    'upc': lectura['upc'],
                    'cantidad': lectura['cantidad'],
                    'timestamp': lectura['timestamp'].isoformat(),
                    'fuente': lectura['fuente'],
                    'sincronizada': str(lectura.get('sincronizada', False)),
                    'estacion_id': str(lectura.get('estacion_id', '')),
                    'usuario_id': str(lectura.get('usuario_id', '')),
                    'orden_fabricacion_id': str(lectura.get('orden_fabricacion_id', ''))
                })

                # Agregar a lista de lecturas pendientes
                self.redis_client.lpush('lecturas_pendientes', lectura_id)

                self.logger.debug(f"INFO: Lectura guardada: {lectura_id}")

        except Exception as e:
            self.logger.error(f"ERROR: Error guardando lectura: {e}")

    def obtener_lecturas_pendientes(self, limite: int = None) -> List[Dict[str, Any]]:
        """Obtener lecturas pendientes de sincronización"""
        try:
            with self.lock:
                cursor = self.sqlite_conn.cursor()
                query = '''
                    SELECT * FROM lecturas_produccion
                    WHERE sincronizada = FALSE
                    ORDER BY timestamp ASC
                '''

                if limite:
                    query += f' LIMIT {limite}'

                cursor.execute(query)

                lecturas = []
                for row in cursor.fetchall():
                    lecturas.append({
                        'id': row['id'],
                        'orden_fabricacion': row['orden_fabricacion'],
                        'upc': row['upc'],
                        'cantidad': row['cantidad'],
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'fuente': row['fuente'],
                        'estacion_id': row['estacion_id'] if 'estacion_id' in row.keys() else None,
                        'usuario_id': row['usuario_id'] if 'usuario_id' in row.keys() else None,
                        'orden_fabricacion_id': row['orden_fabricacion_id'] if 'orden_fabricacion_id' in row.keys() else None
                    })

                return lecturas

        except Exception as e:
            self.logger.error(f"ERROR: Error obteniendo lecturas pendientes: {e}")
            return []

    def obtener_lecturas_por_orden(self, orden_fabricacion: str, estacion_id: int) -> List[Dict[str, Any]]:
        """Obtener lecturas de una orden específica"""
        try:
            with self.lock:
                cursor = self.sqlite_conn.cursor()
                cursor.execute('''
                    SELECT * FROM lecturas_produccion
                    WHERE orden_fabricacion = ? AND estacion_id = ?
                    ORDER BY timestamp ASC
                ''', (orden_fabricacion, estacion_id))

                lecturas = []
                for row in cursor.fetchall():
                    lecturas.append({
                        'id': row['id'],
                        'orden_fabricacion': row['orden_fabricacion'],
                        'upc': row['upc'],
                        'cantidad': row['cantidad'],
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'fuente': row['fuente'],
                        'estacion_id': row['estacion_id'] if 'estacion_id' in row.keys() else None,
                        'usuario_id': row['usuario_id'] if 'usuario_id' in row.keys() else None,
                        'orden_fabricacion_id': row['orden_fabricacion_id'] if 'orden_fabricacion_id' in row.keys() else None
                    })

                return lecturas

        except Exception as e:
            self.logger.error(f"ERROR: Error obteniendo lecturas por orden: {e}")
            return []

    def contar_lecturas_pendientes(self) -> int:
        """Contar lecturas pendientes de sincronización"""
        try:
            with self.lock:
                cursor = self.sqlite_conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM lecturas_produccion WHERE sincronizada = FALSE')
                return cursor.fetchone()[0]

        except Exception as e:
            self.logger.error(f"ERROR: Error contando lecturas pendientes: {e}")
            return 0

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

                # Limpiar de Redis
                for lectura in lecturas:
                    redis_key = f"lectura:{lectura['id']}"
                    self.redis_client.delete(redis_key)
                    self.redis_client.lrem('lecturas_pendientes', 0, lectura['id'])

                self.logger.info(f"SUCCESS: {len(lecturas)} lecturas marcadas como sincronizadas")

        except Exception as e:
            self.logger.error(f"ERROR: Error marcando lecturas como sincronizadas: {e}")

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

                # Guardar en Redis
                redis_key = f"estacion:{estacion_id}"
                self.redis_client.hset(redis_key, mapping={
                    'estado': estado.get('estado', 'INACTIVO'),
                    'orden_actual': estado.get('orden_actual', ''),
                    'contador': estado.get('contador', 0),
                    'meta': estado.get('meta', 0),
                    'ultima_actividad': estado.get('ultima_actividad', ''),
                    'tiempo_inactivo': estado.get('tiempo_inactivo', 0)
                })

        except Exception as e:
            self.logger.error(f"ERROR: Error guardando estado estacion: {e}")

    def obtener_estado_estacion(self, estacion_id: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de una estación"""
        try:
            # Intentar obtener de Redis primero
            redis_key = f"estacion:{estacion_id}"
            estado_redis = self.redis_client.hgetall(redis_key)

            if estado_redis:
                return {
                    'estado': estado_redis.get('estado', 'INACTIVO'),
                    'orden_actual': estado_redis.get('orden_actual', ''),
                    'contador': int(estado_redis.get('contador', 0)),
                    'meta': int(estado_redis.get('meta', 0)),
                    'ultima_actividad': estado_redis.get('ultima_actividad', ''),
                    'tiempo_inactivo': int(estado_redis.get('tiempo_inactivo', 0))
                }

            # Si no está en Redis, obtener de SQLite
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
            self.logger.error(f"ERROR: Error obteniendo estado estacion: {e}")
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
                    self.logger.info(f"INFO: {eliminadas} lecturas antiguas eliminadas")

        except Exception as e:
            self.logger.error(f"ERROR: Error limpiando lecturas antiguas: {e}")

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
            self.logger.error(f"ERROR: Error obteniendo estadisticas: {e}")
            return {}

    def cerrar(self):
        """Cerrar conexiones"""
        try:
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.redis_client:
                self.redis_client.close()
            self.logger.info("SUCCESS: Cache cerrado")
        except Exception as e:
            self.logger.error(f"ERROR: Error cerrando cache: {e}")
