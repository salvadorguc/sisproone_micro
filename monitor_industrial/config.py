#!/usr/bin/env python3
"""
Configuración del Monitor Industrial
"""

import json
import os
from typing import Dict, Any, Optional

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.config_default()

    def config_default(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            "sispro": {
                "base_url": "http://100.24.193.207:3000",
                "username": "HOOK",
                "password": "HOOK25",
                "empresa_id": 1,
                "usuario_id": 1
            },
            "rs485": {
                "port": "/dev/ttyUSB0",
                "baudrate": 9600,
                "timeout": 1
            },
            "cache": {
                "redis_host": "localhost",
                "redis_port": 6379,
                "redis_password": "Z67tyEr",
                "redis_db": 0,
                "sqlite_file": "monitor_cache.db"
            },
            "interfaz": {
                "fullscreen": True,
                "theme": "industrial",
                "update_interval": 1000
            },
            "sincronizacion": {
                "intervalo_minutos": 5,
                "max_reintentos": 3,
                "timeout_segundos": 30
            },
            "estacion": {
                "id": None,
                "nombre": None
            }
        }

    def cargar(self):
        """Cargar configuración desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_cargada = json.load(f)
                    self.config = self.merge_config(self.config, config_cargada)
            else:
                self.guardar()
        except Exception as e:
            print(f"WARNING: Error cargando configuracion: {e}")
            self.guardar()

    def guardar(self):
        """Guardar configuración a archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"ERROR: Error guardando configuracion: {e}")

    def merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """Fusionar configuración cargada con la por defecto"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Establecer valor de configuración"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.guardar()

    def guardar_estacion(self, estacion_id: int, estacion_nombre: str = None):
        """Guardar estación seleccionada"""
        self.set('estacion.id', estacion_id)
        if estacion_nombre:
            self.set('estacion.nombre', estacion_nombre)

    @property
    def sispro_base_url(self) -> str:
        return self.get('sispro.base_url')

    @property
    def sispro_username(self) -> str:
        return self.get('sispro.username')

    @property
    def sispro_password(self) -> str:
        return self.get('sispro.password')

    @property
    def empresa_id(self) -> int:
        return self.get('sispro.empresa_id')

    @property
    def usuario_id(self) -> int:
        return self.get('sispro.usuario_id')

    @property
    def rs485_port(self) -> str:
        return self.get('rs485.port')

    @property
    def rs485_baudrate(self) -> int:
        return self.get('rs485.baudrate')

    @property
    def rs485_timeout(self) -> int:
        return self.get('rs485.timeout')

    @property
    def redis_host(self) -> str:
        return self.get('cache.redis_host')

    @property
    def redis_port(self) -> int:
        return self.get('cache.redis_port')

    @property
    def redis_password(self) -> str:
        return self.get('cache.redis_password')

    @property
    def redis_db(self) -> int:
        return self.get('cache.redis_db')

    @property
    def sqlite_file(self) -> str:
        return self.get('cache.sqlite_file')

    @property
    def fullscreen(self) -> bool:
        return self.get('interfaz.fullscreen')

    @property
    def theme(self) -> str:
        return self.get('interfaz.theme')

    @property
    def update_interval(self) -> int:
        return self.get('interfaz.update_interval')

    @property
    def intervalo_sincronizacion(self) -> int:
        return self.get('sincronizacion.intervalo_minutos')

    @property
    def max_reintentos(self) -> int:
        return self.get('sincronizacion.max_reintentos')

    @property
    def timeout_sincronizacion(self) -> int:
        return self.get('sincronizacion.timeout_segundos')

    @property
    def estacion_id(self) -> Optional[int]:
        return self.get('estacion.id')

    @property
    def estacion_nombre(self) -> Optional[str]:
        return self.get('estacion.nombre')
