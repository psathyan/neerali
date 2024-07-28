# Settings
SHELL				:= /bin/bash
VIRTUAL_ENV			?= venv
MOLECULE_CONFIG		?= .molecule.config.yaml
ROLE_NAME			?=

# Targets

dev-setup:
	bash scripts/dev-setup.sh

.PHONY: create-update-role
create-update-role:
	$(if $(strip $(ROLE_NAME)),,$(error Please call make create-update-role ROLE_NAME=${ROLE_NAME}))
	ansible-galaxy role init --role-skeleton _skeleton_role_ --init-path ./roles ${ROLE_NAME}
