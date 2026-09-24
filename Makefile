SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c
.DEFAULT_GOAL := help

VENV := .env
PYTHON := python3
PYINFRA := $(VENV)/bin/pyinfra
PYTEST := $(VENV)/bin/pytest

# Target host for pyinfra. Defaults to the local machine (no SSH needed);
# override for a remote host, e.g. `make dry-deploy HOST=inventory.py`
# or `make dry-deploy HOST=some-hostname`.
HOST ?= @local

# Strips the known-harmless gevent/atfork traceback noise (gevent doesn't
# yet support Python 3.14's threading internals) from stderr, without
# hiding real errors. See CLAUDE.md.
NOISE_PATTERN := Exception ignored in atfork callback|Traceback \(most recent call last\):|threading\.py"|_after_fork|_os_thread_handle|AttributeError:|assert len\(active\)|AssertionError:
QUIET := 2>&1 | grep -vE '$(NOISE_PATTERN)'

.PHONY: help
help:
	@echo "Targets:"
	@echo "  venv         Create .env and install requirements-dev.txt"
	@echo "  test         Run the unit tests"
	@echo "  dry-deploy   Preview deploy.py changes (no changes applied)"
	@echo "  deploy       Apply deploy.py"
	@echo "  dry-esp32    Preview esp32_arduino_setup.py changes (no changes applied)"
	@echo "  esp32        Apply esp32_arduino_setup.py"
	@echo "  clean        Remove the venv"
	@echo ""
	@echo "Override the target host with HOST=... (default: @local)"

$(VENV)/bin/activate: requirements-dev.txt requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements-dev.txt
	touch $(VENV)/bin/activate

.PHONY: venv
venv: $(VENV)/bin/activate

.PHONY: test
test: venv
	$(PYTEST)

.PHONY: dry-deploy
dry-deploy: venv
	$(PYINFRA) $(HOST) deploy.py --dry $(QUIET)

.PHONY: deploy
deploy: venv
	$(PYINFRA) $(HOST) deploy.py $(QUIET)

.PHONY: dry-esp32
dry-esp32: venv
	$(PYINFRA) $(HOST) esp32_arduino_setup.py --dry $(QUIET)

.PHONY: esp32
esp32: venv
	$(PYINFRA) $(HOST) esp32_arduino_setup.py $(QUIET)

.PHONY: clean
clean:
	rm -rf $(VENV)
