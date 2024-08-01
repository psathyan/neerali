# Common variables for scripts
export NEERALI_DIR="$(dirname $(readlink -f ${BASH_SOURCE[0]}))/../"
export ANSIBLE_LOCAL_TMP=/tmp
export ANSIBLE_REMOTE_TMP=/tmp

export NEERALI_ROLES_PATH="${NEERALI_DIR}/roles:~/.ansible/roles:/usr/share/ansible/roles:/etc/ansible/roles"
export NEERALI_COLLECTIONS_PATH="~/.ansible/collections"
export NEERALI_ACTION_PLUGINS="${NEERALI_DIR}/plugins/action:/usr/share/ansible/plugins/action"
export NEERALI_FILTER_PLUGINS="${NEERALI_DIR}/plugins/filter:/usr/share/ansible/roles:/etc/ansible/roles"