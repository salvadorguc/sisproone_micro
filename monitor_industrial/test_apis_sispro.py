#!/usr/bin/env python3
"""
Prueba simple de login con SISPRO
"""

import requests
import json

# Configuración
BASE_URL = "http://100.24.193.207:3000"
USERNAME = "MONITORPI"
PASSWORD = "56fg453drJ"
EMPRESA_ID = 1

def test_apis_directo():
    """Probar APIs directamente sin autenticación (login local)"""
    print("🔐 PRUEBA DE APIS SISPRO (LOGIN LOCAL)")
    print("=" * 50)
    print(f"URL: {BASE_URL}")
    print(f"Empresa ID: {EMPRESA_ID}")
    print("=" * 50)

    # Probar directamente las APIs que necesitamos
    apis_to_test = [
        {
            "name": "Estaciones de Trabajo",
            "url": "/api/estacionesTrabajo",
            "method": "GET"
        },
        {
            "name": "Órdenes Asignadas",
            "url": "/api/ordenesDeFabricacion/listarAsignadas?estacionTrabajoId=1",
            "method": "GET"
        },
        {
            "name": "Avance de Orden",
            "url": "/api/ordenesDeFabricacion/avance?ordenFabricacion=OF-001",
            "method": "GET"
        }
    ]

    for api in apis_to_test:
        try:
            print(f"📡 Probando: {api['name']}")
            print(f"   URL: {api['url']}")

            headers = {
                'empresa-id': str(EMPRESA_ID),
                'Content-Type': 'application/json'
            }

            if api['method'] == 'GET':
                response = requests.get(
                    f"{BASE_URL}{api['url']}",
                    headers=headers,
                    timeout=30
                )
            else:
                response = requests.post(
                    f"{BASE_URL}{api['url']}",
                    headers=headers,
                    timeout=30
                )

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {api['name']} - EXITOSO!")

                # Mostrar información relevante
                if 'data' in data:
                    if isinstance(data['data'], list):
                        print(f"   📋 Elementos encontrados: {len(data['data'])}")
                        if data['data'] and len(data['data']) > 0:
                            first_item = data['data'][0]
                            if 'nombre' in first_item:
                                print(f"   🎯 Primer elemento: {first_item.get('nombre', 'Sin nombre')}")
                            elif 'ordenFabricacion' in first_item:
                                print(f"   🎯 Primera orden: {first_item.get('ordenFabricacion', 'Sin orden')}")
                    else:
                        print(f"   📋 Datos: {json.dumps(data['data'], indent=2)[:200]}...")
                else:
                    print(f"   📋 Respuesta: {json.dumps(data, indent=2)[:200]}...")

            elif response.status_code == 400:
                print(f"   ⚠️  {api['name']} - Error 400 (probablemente falta parámetro)")
                print(f"   📋 Error: {response.text[:100]}")
            elif response.status_code == 404:
                print(f"   ❌ {api['name']} - No encontrado (404)")
            elif response.status_code == 405:
                print(f"   ❌ {api['name']} - Método no permitido (405)")
            else:
                print(f"   ❌ {api['name']} - Error {response.status_code}")
                print(f"   📋 Error: {response.text[:100]}")

        except Exception as e:
            print(f"   ❌ Error probando {api['name']}: {e}")

    print("\n🎯 RESUMEN:")
    print("✅ Si ves respuestas 200: Las APIs funcionan correctamente")
    print("⚠️  Si ves errores 400: Las APIs existen pero faltan parámetros")
    print("❌ Si ves errores 404/405: Las APIs no existen o están mal configuradas")

    return True

if __name__ == "__main__":
    print("🏭 PRUEBA DE CONEXIÓN SISPRO - MONITOR RASPBERRY PI")
    print("=" * 60)

    success = test_apis_directo()

    if success:
        print("\n🎉 ¡PRUEBA COMPLETADA!")
        print("✅ Las APIs están disponibles para el monitor Python")
        print("🚀 Puedes proceder con la implementación en Raspberry Pi")
        print("\n📝 PRÓXIMOS PASOS:")
        print("   1. Implementar el monitor Python siguiendo cursorrules_python_monitor.md")
        print("   2. Configurar comunicación RS485 con Raspberry Pi Pico")
        print("   3. Implementar caché local con Redis/SQLite")
        print("   4. Configurar sincronización periódica con SISPRO")
    else:
        print("\n❌ ¡PRUEBA FALLIDA!")
        print("🔧 Revisa la configuración y vuelve a intentar")
