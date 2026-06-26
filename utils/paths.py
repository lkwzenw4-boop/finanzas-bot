"""
Utilidades para resolver rutas de archivos.
Maneja la diferencia entre ejecucion normal y ejecucion empaquetada (PyInstaller).
"""
import os
import sys


def get_base_path():
    """
    Retorna la ruta base del proyecto.
    - En desarrollo: el directorio del proyecto
    - En ejecutable (PyInstaller): sys._MEIPASS (directorio temporal de extraccion)
    """
    if getattr(sys, 'frozen', False):
        # Ejecutable empaquetado con PyInstaller
        return sys._MEIPASS
    else:
        # Ejecucion normal desde codigo fuente
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_user_data_path():
    """
    Retorna la ruta donde se guardan datos del usuario (BD, configuracion).
    - En desarrollo: junto al main.py
    - En ejecutable: junto al .exe
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
