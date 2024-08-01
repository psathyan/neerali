#!/bin/bash
set -euo pipefail

project_dir="$(dirname $(readlink -f ${BASH_SOURCE[0]}))/../"
source ${project_dir}/scripts/common.sh

ROLE_DIR="roles/${ROLE_NAME}"
_config="${MOLECULE_CONFIG:-../../.molecule.config.yaml}"

pushd ${ROLE_DIR}
molecule -c ${_config} test
popd
