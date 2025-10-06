#!/usr/bin/env python3
"""
Script de ejecución para Mac - Monitor Industrial SISPRO
"""

import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar el monitor
from test_mac import main

if __name__ == "__main__":
    main()
