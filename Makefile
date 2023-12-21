# A self-documenting Makefile
# You can set these variables from the command line, and also
# from the environment for the first two.

SOURCEDIR = ./ocx_generator
CONDA_ENV = generator
DATA_SOURCE: C:\PythonDev\ocxtools\readme

# PROJECT setup using conda and powershell
.PHONY: conda-create
conda-create:  ## Create a new conda environment with the python version and basic development tools as specified in environment.yml
	@conda env create -f environment.yml

conda-upd:  ## Update the conda development environment when environment.yml has changed
	@conda env update -f environment.yml
.PHONY:conda-upd

conda-clean: ## Purge all conda tarballs, log files and caches
	conda clean -a -y
.PHONY: conda-clean

conda-activate: ## Activate the conda environment for the project
	@conda activate $(CONDA_ENV)

# Color output
BLUE='\033[0;34m'
NC='\033[0m' # No Color

check:
	@echo ${PYPI_USER}
	@echo {$PSWD}
.PHONY: check

# DOCUMENTATION ##############################################################
SPHINXBUILD = sphinx-build -E -b html docs dist/docs
COVDIR = "htmlcov"

doc-serve: ## Open the the html docs built by Sphinx
	@cmd /c start "_build/index.html"

ds: doc-serve
.PHINY: ds

doc: ## Build the html docs using Sphinx. For other Sphinx options, run make in the docs folder
	@sphinx-build docs _build
PHONY: doc

doc-links: ## Check the internal and external links after building the documentation
	@sphinx-build docs -W -b linkcheck -d _build/doctrees _build/html
PHONY: doc-links

build-exe:  ## Build a single Windows executable
	@pyinstaller --clean --onefile --name ocxtools  --add-data "readme\*:readme"  .\__main__.py

# POETRY ########################################################################
build:   ## Build the package dist with poetry
	@poetry update
	@poetry build
.PHONY: build

poetry-fix:  ## Force pip poetry re-installation
	@pip install poetry --upgrade
.PHONY: poetry-fix

export:   ## Export the dependencies to docs/requirements.txt
	@poetry export --with=docs -o ./docs/requirements.txt
.PHONY: publish

#  Run CLI
run:  ## Run the CLI
	python __main__.py
.PHONY: run
# pre-commit ######################################################################
pre-commit:	## Run any pre-commit hooks
	@pre-commit run --all-files

sourcery:  ## Run sourcery with --fix
# TESTS #######################################################################
	@sourcery review --fix --no-summary ./ocxtools
FAILURES := .pytest_cache/pytest/v/cache/lastfailed


test:  ## Run unit and integration tests
	@pytest --durations=5  --cov-report html --cov ocxtools .
.PHONY: test

test-upd:  ## Run unit and integration tests
	@pytest --force-regen --durations=5  --cov-report html --cov ocxtools .


test-cov:  ## View the test coverage report
	cmd /c start $(CURDIR)/htmlcov/index.html
.PHONY: test-cov

# REST API #######################################################################
swagger:  ## Swagger api documentation
# HELP ########################################################################
	cmd /c start http://localhost:8080/swagger-ui.html


# REST API #######################################################################
validate:  ## Docker GUI validation
# HELP ########################################################################
	cmd /c start http://localhost:8080/ocx/upload


.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

#-----------------------------------------------------------------------------------------------
