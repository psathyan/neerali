#!/bin/bash
set -xeuo pipefail

ROLE_DIR="roles/${ROLE_NAME}"
_config="${MOLECULE_CONFIG:-../../.molecule.config.yaml}"

pushd ${ROLE_DIR}
molecule -c ${_config} test
popd
