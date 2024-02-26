# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
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
	@echo "Installing psyacc..."
	@python3 -m pip install -r requirements.txt
	@python3 -m pip install -e .
	@echo "Done."
	@echo "Setting up pre-commit..."
	@pre-commit install
	@echo "Done."

docs: demos
	@echo "Building PSyACC docs..."
	@cd docs && make html
	@echo "Done."

format:
	@echo "Applying formatting..."
	@black *.py
	@black demos/*.py
	@black docs/source/*.py
	@black psyacc/*.py
	@black test/*.py
	@echo "Done."

lint:
	@echo "Checking lint..."
	@flake8
	@echo "PASS"

test: lint
	@echo "testing psyacc..."
	@python3 -m pytest -v --durations=20 test
	@echo "PASS"

coverage:
	@echo "Generating coverage report..."
	@python3 -m coverage erase
	@python3 -m coverage run --source=psyacc -m pytest -v test
	@python3 -m coverage html
	@echo "Done."

demos: setup
	@echo "Running demos..."
	@cd demos && make run
	@echo "Done."
