#!/usr/bin/env python3
"""
Configuración para Mac - Versión simplificada
"""

import json
import os
from typing import Dict, Any

class Config:
    def __init__(self, config_file="config_mac.json"):
        self.config_file = config_file

        # Configuración por defecto para Mac
        self.sispro_base_url = "http://localhost:3000"
        self.sispro_username = "monitor_pi"
        self.sispro_password = "password_segura"
        self.empresa_id = 1
        self.usuario_id = 1

        # RS485 simulado
        self.rs485_port = "/dev/ttyUSB0"  # No se usa en Mac
        self.rs485_baudrate = 9600
        self.rs485_timeout = 1

        # Cache simplificado (solo SQLite)
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.redis_db = 0
        self.sqlite_file = "monitor_cache_mac.db"

        # Interfaz
        self.fullscreen = False  # No fullscreen en Mac para pruebas
        self.theme = "industrial"
        self.update_interval = 1000

        # Sincronización
        self.intervalo_minutos = 1  # Más rápido para pruebas
        self.max_reintentos = 3
        self.timeout_segundos = 30

        # Logging
        self.log_level = "INFO"
        self.log_file = "logs/monitor_mac.log"

    def cargar(self):
        """Cargar configuración desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)

                # Cargar configuración SISPRO
                sispro_config = config_data.get("sispro", {})
                self.sispro_base_url = sispro_config.get("base_url", self.sispro_base_url)
                self.sispro_username = sispro_config.get("username", self.sispro_username)
                self.sispro_password = sispro_config.get("password", self.sispro_password)
                self.empresa_id = sispro_config.get("empresa_id", self.empresa_id)
                self.usuario_id = sispro_config.get("usuario_id", self.usuario_id)

                # Cargar configuración RS485
                rs485_config = config_data.get("rs485", {})
                self.rs485_port = rs485_config.get("port", self.rs485_port)
                self.rs485_baudrate = rs485_config.get("baudrate", self.rs485_baudrate)
                self.rs485_timeout = rs485_config.get("timeout", self.rs485_timeout)

                # Cargar configuración de cache
                cache_config = config_data.get("cache", {})
                self.redis_host = cache_config.get("redis_host", self.redis_host)
                self.redis_port = cache_config.get("redis_port", self.redis_port)
                self.redis_db = cache_config.get("redis_db", self.redis_db)
                self.sqlite_file = cache_config.get("sqlite_file", self.sqlite_file)

                # Cargar configuración de interfaz
                interfaz_config = config_data.get("interfaz", {})
                self.fullscreen = interfaz_config.get("fullscreen", self.fullscreen)
                self.theme = interfaz_config.get("theme", self.theme)
                self.update_interval = interfaz_config.get("update_interval", self.update_interval)

                # Cargar configuración de sincronización
                sincronizacion_config = config_data.get("sincronizacion", {})
                self.intervalo_minutos = sincronizacion_config.get("intervalo_minutos", self.intervalo_minutos)
                self.max_reintentos = sincronizacion_config.get("max_reintentos", self.max_reintentos)
                self.timeout_segundos = sincronizacion_config.get("timeout_segundos", self.timeout_segundos)

                print(f"✅ Configuración cargada desde {self.config_file}")
            else:
                print(f"⚠️ Archivo de configuración {self.config_file} no encontrado. Usando valores por defecto.")
                self.guardar()  # Crear archivo con valores por defecto

        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            print("Usando valores por defecto.")

    def guardar(self):
        """Guardar configuración en archivo"""
        try:
            config_data = {
                "sispro": {
                    "base_url": self.sispro_base_url,
                    "username": self.sispro_username,
                    "password": self.sispro_password,
                    "empresa_id": self.empresa_id,
                    "usuario_id": self.usuario_id
                },
                "rs485": {
                    "port": self.rs485_port,
                    "baudrate": self.rs485_baudrate,
                    "timeout": self.rs485_timeout
                },
                "cache": {
                    "redis_host": self.redis_host,
                    "redis_port": self.redis_port,
                    "redis_db": self.redis_db,
                    "sqlite_file": self.sqlite_file
                },
                "interfaz": {
                    "fullscreen": self.fullscreen,
                    "theme": self.theme,
                    "update_interval": self.update_interval
                },
                "sincronizacion": {
                    "intervalo_minutos": self.intervalo_minutos,
                    "max_reintentos": self.max_reintentos,
                    "timeout_segundos": self.timeout_segundos
                }
            }

            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)

            print(f"✅ Configuración guardada en {self.config_file}")

        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")

    def guardar_estacion(self, estacion_id: int):
        """Guardar ID de estación seleccionada"""
        try:
            config_data = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)

            config_data["estacion_actual"] = estacion_id

            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)

        except Exception as e:
            print(f"❌ Error guardando estación: {e}")

    def obtener_estacion_guardada(self) -> int:
        """Obtener ID de estación guardada"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                return config_data.get("estacion_actual", 0)
            return 0
        except Exception as e:
            print(f"❌ Error obteniendo estación guardada: {e}")
            return 0
