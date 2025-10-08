#!/usr/bin/env python3
"""
Script de prueba usando el mismo SisproConnector que la aplicación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sispro_connector import SISPROConnector
from config import Config
from datetime import datetime

def test_sispro_connector():
    """Probar SisproConnector directamente"""

    print("=" * 60)
    print("TEST CON SISPRO CONNECTOR")
    print("=" * 60)

    try:
        # Cargar configuración
        print("1. CARGANDO CONFIGURACIÓN...")
        config = Config()
        print(f"   Base URL: {config.get('sispro.base_url')}")
        print(f"   Usuario: {config.get('sispro.username')}")
        print(f"   Empresa ID: {config.get('sispro.empresa_id')}")

        # Crear connector
        print("\n2. CREANDO SISPRO CONNECTOR...")
        sispro = SISPROConnector(config)

        # Conectar
        print("\n3. CONECTANDO...")
        if not sispro.conectar():
            print("   ❌ ERROR: No se pudo conectar")
            return False

        print("   ✅ SUCCESS: Conectado correctamente")

        # Probar órdenes
        print("\n4. PROBANDO ÓRDENES...")
        ordenes_prueba = ["523856", "523771", "523757", "523804"]

        for orden in ordenes_prueba:
            print(f"\n   Probando orden: {orden}")

            try:
                resultado = sispro.consultar_estatus_orden(orden)

                if resultado and resultado.get('success'):
                    data = resultado.get('data', {})
                    print(f"   ✅ SUCCESS: Receta obtenida")
                    print(f"   Orden: {data.get('ordenFabricacion')}")
                    print(f"   Producto: {data.get('articuloPT')} - {data.get('descripcionPT')}")
                    print(f"   Partidas: {len(data.get('partidas', []))} materiales")

                    # Mostrar algunas partidas
                    for i, partida in enumerate(data.get('partidas', [])[:3]):
                        print(f"     {i+1}. {partida.get('articuloMP')} - {partida.get('descripcionMP')} (Cant: {partida.get('cantidad')})")

                    if len(data.get('partidas', [])) > 3:
                        print(f"     ... y {len(data.get('partidas', [])) - 3} más")

                    return True
                else:
                    print(f"   ❌ ERROR: No se pudo obtener receta")
                    print(f"   Resultado: {resultado}")

            except Exception as e:
                print(f"   ❌ ERROR: Excepción: {e}")

        # Desconectar
        print("\n5. DESCONECTANDO...")
        sispro.desconectar()
        print("   ✅ SUCCESS: Desconectado")

        return False

    except Exception as e:
        print(f"❌ ERROR: Excepción general: {e}")
        return False

def test_config_values():
    """Verificar valores de configuración"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 60)

    try:
        config = Config()

        print("Valores de configuración SISPRO:")
        print(f"  base_url: {config.get('sispro.base_url')}")
        print(f"  username: {config.get('sispro.username')}")
        print(f"  password: {config.get('sispro.password')}")
        print(f"  empresa_id: {config.get('sispro.empresa_id')}")
        print(f"  usuario_id: {config.get('sispro.usuario_id')}")

        print("\nValores de configuración Database:")
        print(f"  host: {config.get('database.host')}")
        print(f"  port: {config.get('database.port')}")
        print(f"  username: {config.get('database.username')}")
        print(f"  database: {config.get('database.database')}")

    except Exception as e:
        print(f"❌ ERROR: No se pudo cargar configuración: {e}")

if __name__ == "__main__":
    print(f"Iniciando test a las {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Verificar configuración
    test_config_values()

    # Test principal
    success = test_sispro_connector()

    if success:
        print("\n" + "=" * 60)
        print("✅ RESULTADO: SisproConnector funciona correctamente")
        print("El problema puede estar en la integración con la interfaz")
    else:
        print("\n" + "=" * 60)
        print("❌ RESULTADO: SisproConnector tiene problemas")
        print("Revisa la configuración y conectividad")

    print("\n" + "=" * 60)
    print("Test completado")
