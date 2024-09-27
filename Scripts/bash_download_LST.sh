#!/bin/bash
readonly envFile="/var/py/volunclima/scripts/prediccion/venv/bin/activate"
source ${envFile}
cd /var/py/volunclima/scripts/goes-16/Scripts/
python3.9 download_LST.py
