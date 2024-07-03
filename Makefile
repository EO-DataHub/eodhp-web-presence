.PHONY: dockerbuild dockerpush test testonce ruff pylint black lint
VERSION ?= latest
IMAGENAME = eodhp-web-presence
DOCKERREPO ?= public.ecr.aws/n1b3o1k2/ukeodhp

dockerbuild:
	DOCKER_BUILDKIT=1 docker build -t ${IMAGENAME}:${VERSION} .

dockerpush: dockerbuild testdocker
	docker tag ${IMAGENAME}:${VERSION} ${}DOCKERREPO}/${IMAGENAME}:${VERSION}
	docker push ${DOCKERREPO}/${IMAGENAME}:${VERSION}

test:
	./venv/bin/ptw CHANGEME-test-package-names

testonce:
	./venv/bin/pytest

pylint:
	./venv/bin/pylint CHANGEME-package-names

ruff:
	./venv/bin/ruff check .

black:
	./venv/bin/black .

isort:
	./venv/bin/isort . --check --diff

lint: ruff black isort

run:
	(set -a; . ./.env; DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ./venv/bin/python ./eodhp_web_presence/manage.py runserver)
