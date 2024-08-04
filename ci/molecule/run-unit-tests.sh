#!/bin/bash
source ~/venv/bin/activate
set -euo pipefail

# The purpouse of this script is to execute molecule or ansible-tests.
# Usage:
#       bash run-unit-tests.sh <molecule|ansible-test> <module>
#
# Where
#       $1      The type of test to be executed.
#       $2      The ROLE_NAME of ansible-test type [sanity|integration]

_type=${1:-"molecule"}
_mod=${2:-""}

export LC_ALL=C.UTF-8

export NEERALI_DIR="${HOME}/neerali"
export NEERALI_ROLES_PATH="${NEERALI_DIR}/roles:~/.ansible/roles:/usr/share/ansible/roles:/etc/ansible/roles"
export NEERALI_COLLECTIONS_PATH="~/.ansible/collections"
export NEERALI_ACTION_PLUGINS="${NEERALI_DIR}/plugins/action:/usr/share/ansible/plugins/action"
export NEERALI_FILTER_PLUGINS="${NEERALI_DIR}/plugins/filter:/usr/share/ansible/roles:/etc/ansible/roles"

export ANSIBLE_LOCAL_TMP=/tmp
export ANSIBLE_LOG_PATH=/tmp/ansible-execution.log
export MOLECULE_REPORT=/tmp/report.html

pushd neerali
python -m pip install -r requirements.txt
ansible-galaxy collection install .

if [ "${_type}" == "ansible-test" ]; then
    echo "Executing ansible-test"
    pushd ~/.ansible/collections/ansible_collections/neerali/general
    ansible-test ${_mod}
    popd
elif [ "${_type}" == "molecule" ]; then
    pushd roles/${2}
    echo "Executing molecule"
    molecule -c ${NEERALI_DIR}/.config/molecule/config.yml test
    popd
else
    echo "Unknown test execution"
    exit 1
fi

popd
echo "Testing done"
