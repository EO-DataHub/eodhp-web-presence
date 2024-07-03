.PHONY: dockerbuild dockerpush test testonce ruff black lint isort pre-commit-check requirements-update requirements setup
VERSION ?= latest
IMAGENAME = eodhp-web-presence
DOCKERREPO ?= public.ecr.aws/n1b3o1k2/ukeodhp

dockerbuild:
	DOCKER_BUILDKIT=1 docker build -t ${IMAGENAME}:${VERSION} .

dockerpush: dockerbuild testdocker
	docker tag ${IMAGENAME}:${VERSION} ${}DOCKERREPO}/${IMAGENAME}:${VERSION}
	docker push ${DOCKERREPO}/${IMAGENAME}:${VERSION}

test:
	(set -a; . ./.env; DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ./venv/bin/ptw ./eodhp_web_presence)

testonce:
	(set -a; . ./.env; DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ./venv/bin/pytest ./eodhp_web_presence)

ruff:
	./venv/bin/ruff check .

black:
	./venv/bin/black .

isort:
	./venv/bin/isort . --check --diff

validate-pyproject:
	validate-pyproject pyproject.toml

lint: ruff black isort validate-pyproject

run:
	(set -a; . ./.env; DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ./venv/bin/python ./eodhp_web_presence/manage.py runserver)

requirements.txt: pyproject.toml
	pip-compile

requirements-dev.txt: pyproject.toml
	pip-compile --extra dev -o requirements-dev.txt

requirements: requirements.txt requirements-dev.txt

requirements-update:
	pip-compile -U
	pip-compile --extra dev -o requirements-dev.txt -U

venv:
	virtualenv -p python3.11 venv

.make-venv-installed: venv requirements.txt requirements-dev.txt
	./venv/bin/pip install -r requirements.txt -r requirements-dev.txt
	touch .make-venv-installed

.git/hooks/pre-commit:
	./venv/bin/pre-commit install

setup: venv requirements .make-venv-installed .git/hooks/pre-commit

