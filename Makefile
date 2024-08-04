# Settings
SHELL				:= /bin/bash
VIRTUAL_ENV			?= venv
MOLECULE_CONFIG		?= .config/molecule/config.yml
ROLE_NAME			?=
TEST_EXEC			?= molecule
TEST_SUITE			?=

define vars
${1}: export ROLE_NAME=${ROLE_NAME}
${1}: export MOLECULE_CONFIG=${MOLECULE_CONFIG}
${1}: export VIRTUAL_ENV=${VIRTUAL_ENV}
${1}: export TEST_EXEC=${TEST_EXEC}
${1}: export SHELL=${SHELL}
endef

# Targets

dev-setup:
	bash scripts/dev-setup.sh

.PHONY: create-update-role
create-update-role:
	$(if $(strip $(ROLE_NAME)),,$(error Please call make create-update-role ROLE_NAME=${ROLE_NAME}))
	ansible-galaxy role init --role-skeleton _skeleton_role_ --init-path ./roles ${ROLE_NAME}

.PHONY: unit-test
unit-test:
	$(if $(strip $(TEST_SUITE)),,$(error Please call make run-tests TEST_TYPE=molecule TEST_MOD=${TEST_SUITE}))
	bash scripts/run-tests.sh
