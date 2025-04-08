"""Configuración de pytest para los tests de la aplicación."""

import sys
import os

# Agregar "backend" al sys.path para que pytest encuentre los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
