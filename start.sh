#!/bin/bash
# Salir si hay algún error
set -e

# Mostrar versión de Python (útil para debugging)
python --version

# Instalar dependencias (aunque Railway lo hace, por seguridad)
pip install -r requirements.txt

# Ejecutar el bot
python bot.py