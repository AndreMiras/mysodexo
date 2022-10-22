VIRTUAL_ENV ?= venv
REQUIREMENTS:=requirements.txt
PIP=$(VIRTUAL_ENV)/bin/pip
PYTHON=$(VIRTUAL_ENV)/bin/python
ISORT=$(VIRTUAL_ENV)/bin/isort
FLAKE8=$(VIRTUAL_ENV)/bin/flake8
BLACK=$(VIRTUAL_ENV)/bin/black
PYTEST=$(VIRTUAL_ENV)/bin/pytest
TOX=$(VIRTUAL_ENV)/bin/tox
TWINE=$(VIRTUAL_ENV)/bin/twine
PYTHON_MAJOR_VERSION=3
PYTHON_MINOR_VERSION=7
PYTHON_VERSION=$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)
PYTHON_MAJOR_MINOR=$(PYTHON_MAJOR_VERSION)$(PYTHON_MINOR_VERSION)
PYTHON_WITH_VERSION=python$(PYTHON_VERSION)
SOURCES=mysodexo/ tests/ setup.py setup_meta.py
SPHINXBUILD=$(shell realpath venv/bin/sphinx-build)
DOCS_DIR=docs


$(VIRTUAL_ENV):
	$(PYTHON_WITH_VERSION) -m venv $(VIRTUAL_ENV)
	$(PIP) install -r $(REQUIREMENTS)

virtualenv: $(VIRTUAL_ENV)

test: $(VIRTUAL_ENV)
	$(TOX)

pytest: $(VIRTUAL_ENV)
	$(PYTEST) --cov mysodexo/ --cov-report term --cov-report html tests/

lint/isort: $(VIRTUAL_ENV)
	$(ISORT) --check-only --diff $(SOURCES)

lint/flake8: $(VIRTUAL_ENV)
	$(FLAKE8) $(SOURCES)

lint/black: $(VIRTUAL_ENV)
	$(BLACK) --check $(SOURCES)

format/isort: $(VIRTUAL_ENV)
	$(ISORT) $(SOURCES)

format/black: $(VIRTUAL_ENV)
	$(BLACK) --verbose $(SOURCES)

lint: lint/isort lint/flake8 lint/black

format: format/isort format/black

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

clean/all: clean
	rm -rf $(VIRTUAL_ENV)

docs/clean:
	rm -rf $(DOCS_DIR)/build/

docs/build: virtualenv
	cd $(DOCS_DIR) && make html SPHINXBUILD=$(SPHINXBUILD)

docs: docs/build

release/clean:
	rm -rf dist/ build/

release/build: release/clean virtualenv
	$(PYTHON) setup.py sdist bdist_wheel
	$(TWINE) check dist/*

release/upload:
	$(TWINE) upload dist/*
