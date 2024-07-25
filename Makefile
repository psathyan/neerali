# Settings
SHELL				:= /bin/bash
VIRTUAL_ENV			?= venv

# Targets

.PHONY: dev-setup
dev-setup:
	bash scripts/dev-setup.sh
