#!/usr/bin/env python3
"""
Script simple para probar solo la autenticación
"""

import requests
import json

def test_auth():
    """Probar solo la autenticación"""

    print("=" * 50)
    print("TEST DE AUTENTICACIÓN SIMPLE")
    print("=" * 50)

    # Configuración
    base_url = "http://100.24.193.207:3000"
    username = "HOOK"
    password = "HOOK25"
    empresa_id = 1

    print(f"Base URL: {base_url}")
    print(f"Usuario: {username}")
    print(f"Empresa ID: {empresa_id}")
    print()

    # URL de autenticación
    auth_url = f"{base_url}/api/auth/login_local"

    # Datos de autenticación
    auth_data = {
        "username": username,
        "password": password
    }

    # Headers
    auth_headers = {
        'Content-Type': 'application/json',
        'empresa-id': str(empresa_id)
    }

    print("Enviando petición de autenticación...")
    print(f"URL: {auth_url}")
    print(f"Headers: {auth_headers}")
    print(f"Data: {auth_data}")
    print()

    try:
        # Hacer petición
        response = requests.post(auth_url, json=auth_data, headers=auth_headers, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            try:
                result = response.json()
                print(f"JSON Response: {json.dumps(result, indent=2)}")

                if result.get('success'):
                    token = result.get('token')
                    print(f"\n✅ SUCCESS: Autenticación exitosa")
                    print(f"Token: {token[:50]}..." if token else "No token")
                    return token
                else:
                    print(f"\n❌ ERROR: Autenticación falló")
                    print(f"Message: {result.get('message', 'No message')}")
                    return None

            except json.JSONDecodeError as e:
                print(f"\n❌ ERROR: No se pudo parsear JSON: {e}")
                return None
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Timeout - El servidor no responde")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ERROR: Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: Excepción: {e}")
        return None

if __name__ == "__main__":
    token = test_auth()

    if token:
        print("\n" + "=" * 50)
        print("✅ AUTENTICACIÓN EXITOSA")
        print("Ahora puedes probar el script completo")
    else:
        print("\n" + "=" * 50)
        print("❌ AUTENTICACIÓN FALLÓ")
        print("Revisa la conectividad y configuración")
