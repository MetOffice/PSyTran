# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

all: install

.PHONY: demos docs test

setup:
	@echo "Setting up directory structure..."
	@mkdir -p demos/outputs
	@echo "Done."

install:
	@echo "Updating pip..."
	@python3 -m pip install --upgrade pip
	@echo "Done."
	@echo "Installing psytran..."
	@python3 -m pip install .
	@echo "Done."

install_dev:
	@echo "Updating pip..."
	@python3 -m pip install --upgrade pip
	@echo "Done."
	@echo "Installing psytran with dev dependencies..."
	@python3 -m pip install -e .[dev]
	@echo "Done."
	@echo "Setting up pre-commit..."
	@pre-commit install
	@echo "Done."

docs: demos
	@echo "Building PSyTran docs..."
	@cd docs && make html
	@echo "Done."

format:
	@echo "Applying formatting..."
	@black *.py
	@black demos/*.py
	@black docs/source/*.py
	@black psytran/*.py
	@black test/*.py
	@echo "Done."

codestyle:
	@echo "Checking codestyle..."
	@python3 -m pycodestyle psytran/
	@python3 -m pycodestyle test/
	@echo "PASS"

lint:
	@echo "Checking lint..."
	@python3 -m pylint psytran
	@echo "PASS"

test:
	@echo "testing psytran..."
	@python3 -m pytest -v --durations=20 test
	@echo "PASS"

coverage:
	@echo "Generating coverage report..."
	@python3 -m pytest -v --cov-reset --cov=psytran --cov-report=html test
	@echo "Done."

demos: setup
	@echo "Running demos..."
	@cd demos && make run
	@echo "Done."
