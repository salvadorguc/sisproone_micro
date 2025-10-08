#!/usr/bin/env python3
"""
Script de prueba para testear la API de receta
"""

import requests
import json
from datetime import datetime

def test_receta_api():
    """Probar la API de receta directamente"""

    # Configuración
    base_url = "http://100.24.193.207:3000"
    username = "HOOK"
    password = "HOOK25"
    empresa_id = 1

    print("=" * 60)
    print("TEST DE API DE RECETA")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Usuario: {username}")
    print(f"Empresa ID: {empresa_id}")
    print()

    # Paso 1: Autenticación
    print("1. AUTENTICANDO...")
    auth_url = f"{base_url}/api/auth/login_local"
    auth_data = {
        "username": username,
        "password": password
    }
    auth_headers = {
        'Content-Type': 'application/json',
        'empresa-id': str(empresa_id)
    }

    try:
        print(f"   URL: {auth_url}")
        print(f"   Headers: {auth_headers}")
        print(f"   Data: {auth_data}")

        auth_response = requests.post(auth_url, json=auth_data, headers=auth_headers, timeout=30)
        print(f"   Status Code: {auth_response.status_code}")
        print(f"   Response: {auth_response.text}")

        if auth_response.status_code != 200:
            print("   ❌ ERROR: Falló la autenticación")
            return False

        auth_result = auth_response.json()
        if not auth_result.get('success'):
            print("   ❌ ERROR: Respuesta de autenticación no exitosa")
            return False

        token = auth_result.get('token')
        if not token:
            print("   ❌ ERROR: No se obtuvo token")
            return False

        print(f"   ✅ SUCCESS: Token obtenido: {token[:20]}...")

    except Exception as e:
        print(f"   ❌ ERROR: Excepción en autenticación: {e}")
        return False

    print()

    # Paso 2: Probar API de receta
    print("2. PROBANDO API DE RECETA...")

    # Lista de órdenes para probar
    ordenes_prueba = ["523856", "523771", "523757", "523804"]

    for orden in ordenes_prueba:
        print(f"\n   Probando orden: {orden}")

        receta_url = f"{base_url}/api/ordenesDeFabricacion/estatus"
        receta_params = {'orden': orden}
        receta_headers = {
            'empresa-id': str(empresa_id),
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            print(f"   URL: {receta_url}")
            print(f"   Params: {receta_params}")
            print(f"   Headers: {receta_headers}")

            receta_response = requests.get(receta_url, params=receta_params, headers=receta_headers, timeout=30)
            print(f"   Status Code: {receta_response.status_code}")
            print(f"   Response: {receta_response.text}")

            if receta_response.status_code == 200:
                receta_result = receta_response.json()
                if receta_result.get('success'):
                    data = receta_result.get('data', {})
                    print(f"   ✅ SUCCESS: Receta obtenida")
                    print(f"   Orden: {data.get('ordenFabricacion')}")
                    print(f"   Producto: {data.get('articuloPT')} - {data.get('descripcionPT')}")
                    print(f"   Partidas: {len(data.get('partidas', []))} materiales")

                    # Mostrar algunas partidas
                    for i, partida in enumerate(data.get('partidas', [])[:3]):
                        print(f"     {i+1}. {partida.get('articuloMP')} - {partida.get('descripcionMP')} (Cant: {partida.get('cantidad')})")

                    if len(data.get('partidas', [])) > 3:
                        print(f"     ... y {len(data.get('partidas', [])) - 3} más")

                    return True  # Si una orden funciona, el API está bien
                else:
                    print(f"   ❌ ERROR: Respuesta no exitosa: {receta_result}")
            else:
                print(f"   ❌ ERROR: Status code {receta_response.status_code}")

        except Exception as e:
            print(f"   ❌ ERROR: Excepción: {e}")

    print("\n   ❌ ERROR: Ninguna orden funcionó")
    return False

def test_direct_curl():
    """Probar con curl directo"""
    print("\n" + "=" * 60)
    print("TEST CON CURL DIRECTO")
    print("=" * 60)

    # Comando curl para probar
    curl_command = """
curl --location 'http://100.24.193.207:3000/api/ordenesDeFabricacion/estatus?orden=523856' \\
--header 'empresa-id: 1' \\
--header 'Content-Type: application/json' \\
--header 'Authorization: Bearer [TOKEN_AQUI]'
"""

    print("Comando curl para probar manualmente:")
    print(curl_command)
    print("\nNota: Reemplaza [TOKEN_AQUI] con el token obtenido en el paso 1")

if __name__ == "__main__":
    print(f"Iniciando test a las {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test principal
    success = test_receta_api()

    if success:
        print("\n" + "=" * 60)
        print("✅ RESULTADO: API de receta funciona correctamente")
        print("El problema puede estar en la integración con la aplicación")
    else:
        print("\n" + "=" * 60)
        print("❌ RESULTADO: API de receta tiene problemas")
        print("Revisa la conectividad y configuración del servidor")

    # Test con curl
    test_direct_curl()

    print("\n" + "=" * 60)
    print("Test completado")
