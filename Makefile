VIRTUAL_ENV ?= venv
PIP=$(VIRTUAL_ENV)/bin/pip
TOX=`which tox`
PYTHON=$(VIRTUAL_ENV)/bin/python
ISORT=$(VIRTUAL_ENV)/bin/isort
FLAKE8=$(VIRTUAL_ENV)/bin/flake8
BLACK=$(VIRTUAL_ENV)/bin/black
PYTEST=$(VIRTUAL_ENV)/bin/pytest
MYPY=$(VIRTUAL_ENV)/bin/mypy
# only report coverage for one Python version in tox testing
COVERALLS=.tox/py$(PYTHON_MAJOR_MINOR)/bin/coveralls
TWINE=`which twine`
SOURCES=mysodexo/ tests/ setup.py setup_meta.py
# using full path so it can be used outside the root dir
SPHINXBUILD=$(shell realpath venv/bin/sphinx-build)
DOCS_DIR=docs
PYTHON_MAJOR_VERSION=3
PYTHON_MINOR_VERSION=7
SYSTEM_DEPENDENCIES= \
	libpython3.6-dev \
	libpython$(PYTHON_VERSION)-dev \
	python3.6 \
	python3.6-dev \
	python$(PYTHON_VERSION) \
	python$(PYTHON_VERSION)-dev \
	tox \
	virtualenv
PYTHON_VERSION=$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)
PYTHON_MAJOR_MINOR=$(PYTHON_MAJOR_VERSION)$(PYTHON_MINOR_VERSION)
PYTHON_WITH_VERSION=python$(PYTHON_VERSION)


all: virtualenv

system_dependencies:
	sudo apt install --yes --no-install-recommends $(SYSTEM_DEPENDENCIES)

$(VIRTUAL_ENV):
	virtualenv -p $(PYTHON_WITH_VERSION) $(VIRTUAL_ENV)
	$(PIP) install -r requirements.txt

virtualenv: $(VIRTUAL_ENV)

run: virtualenv
	PYTHONPATH=. $(PYTHON) mysodexo/api.py

test:
	$(TOX)
	@if [ -n "$$CI" ] && [ -f $(COVERALLS) ]; then $(COVERALLS); fi \

doctest: virtualenv
	$(PYTHON) -m doctest mysodexo/*.py

pytest: virtualenv
	$(PYTEST) --cov mysodexo/ --cov-report html tests/

lint/isort-check: virtualenv
	$(ISORT) --check-only --recursive --diff $(SOURCES)

lint/isort-fix: virtualenv
	$(ISORT) --recursive $(SOURCES)

lint/black-fix: virtualenv
	$(BLACK) --verbose $(SOURCES)

lint/flake8: virtualenv
	$(FLAKE8) $(SOURCES)

lint/black-check: virtualenv
	$(BLACK) --check $(SOURCES)

lint/mypy: virtualenv
	$(MYPY) $(SOURCES)

lint: lint/isort-check lint/flake8 lint/black-check lint/mypy

docs/clean:
	rm -rf $(DOCS_DIR)/build/

docs/build: virtualenv
	cd $(DOCS_DIR) && make html SPHINXBUILD=$(SPHINXBUILD)

docs: docs/build

release/clean:
	rm -rf dist/ build/

release/build: release/clean virtualenv
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) setup_meta.py sdist bdist_wheel
	$(TWINE) check dist/*

release/upload:
	$(TWINE) upload dist/*

clean: release/clean docs/clean
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

clean/all: clean
	rm -rf $(VIRTUAL_ENV) .tox/
