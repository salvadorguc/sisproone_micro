from machine import Pin
import time

def test_teclado():
    """Test simple del teclado 4x4"""
    print("=== TEST TECLADO 4x4 ===")
    print("Pines: Filas=14,7,8,9 | Columnas=1,2,3,11")
    print()

    # Pines - ordenados lógicamente
    filas = [Pin(14, Pin.OUT), Pin(7, Pin.OUT), Pin(8, Pin.OUT), Pin(9, Pin.OUT)]
    # Columnas reordenadas para que coincidan con 1,2,3,A
    # GP11, GP2, GP3, GP1 (según el comportamiento real)
    cols = [Pin(11, Pin.IN, Pin.PULL_UP), Pin(2, Pin.IN, Pin.PULL_UP),
            Pin(3, Pin.IN, Pin.PULL_UP), Pin(1, Pin.IN, Pin.PULL_UP)]

    # Teclado - orden lógico estándar
    teclado = [
        ['1', '2', '3', 'A'],  # Fila 1: 1,2,3,A
        ['4', '5', '6', 'B'],  # Fila 2: 4,5,6,B
        ['7', '8', '9', 'C'],  # Fila 3: 7,8,9,C
        ['*', '0', '#', 'D']   # Fila 4: *,0,#,D
    ]

    # Inicializar filas
    for f in filas:
        f.value(1)

    print("Presiona teclas... (Ctrl+C para salir)")

    try:
        while True:
            for i, fila in enumerate(filas):
                fila.value(0)  # Activar fila
                time.sleep_ms(10)

                # Leer columnas
                for j, col in enumerate(cols):
                    if col.value() == 0:  # Tecla presionada
                        print(f"Tecla: '{teclado[i][j]}' (Fila {i+1}, Col {j+1})")
                        time.sleep_ms(300)  # Debounce

                fila.value(1)  # Desactivar fila
                time.sleep_ms(10)

            time.sleep_ms(50)

    except KeyboardInterrupt:
        print("\nTest terminado")

    # Restaurar
    for f in filas:
        f.value(1)

if __name__ == "__main__":
    test_teclado()