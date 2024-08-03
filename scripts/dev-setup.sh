#!/bin/bash
# This scripts installs the require prerequisites need to develop or execute
# neerali.
set -euo pipefail

PY_CMD=$(which python3)
VIRTUAL_ENV=${VIRTUAL_ENV:-"venv"}

echo "Get or create python virtual environment."
if [ ! -d "${VIRTUAL_ENV}" ]; then
    ${PY_CMD} -m venv ${VIRTUAL_ENV}
    ${VIRTUAL_ENV}/bin/python -m pip install setuptools pip --upgrade
fi

echo "Installing neerali's python prerequisites..."
${VIRTUAL_ENV}/bin/python -m pip install -r requirements.txt --upgrade

echo "Install neerali's ansible requirements..."
${VIRTUAL_ENV}/bin/ansible-galaxy collection install ${NEERALI_DIR}
