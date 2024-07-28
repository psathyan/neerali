# Settings
SHELL				:= /bin/bash
VIRTUAL_ENV			?= venv
MOLECULE_CONFIG		?= .molecule.config.yaml
ROLE_NAME			?=

define vars
${1}: export ROLE_NAME=${ROLE_NAME}
${1}: export MOLECULE_CONFIG=${MOLECULE_CONFIG}
${1}: export VIRTUAL_ENV=${VIRTUAL_ENV}
endef

# Targets

dev-setup:
	bash scripts/dev-setup.sh

.PHONY: create-update-role
create-update-role:
	$(if $(strip $(ROLE_NAME)),,$(error Please call make create-update-role ROLE_NAME=${ROLE_NAME}))
	ansible-galaxy role init --role-skeleton _skeleton_role_ --init-path ./roles ${ROLE_NAME}

.PHONY: run-molecule
run-molecule:
	$(if $(strip $(ROLE_NAME)),,$(error Please call make create-update-role ROLE_NAME=${ROLE_NAME}))
	bash scripts/run-molecule.sh
