.PHONY: dockerbuild dockerpush test testonce ruff black lint isort pre-commit-check requirements-update requirements setup
VERSION ?= latest
IMAGENAME = eodhp-web-presence
DOCKERREPO ?= public.ecr.aws/n1b3o1k2

dockerbuild:
	DOCKER_BUILDKIT=1 docker build -t ${IMAGENAME}:${VERSION} .

dockerpush: dockerbuild testdocker
	docker tag ${IMAGENAME}:${VERSION} ${DOCKERREPO}/${IMAGENAME}:${VERSION}
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
	./venv/bin/isort . --profile black

validate-pyproject:
	validate-pyproject pyproject.toml

lint: ruff black isort validate-pyproject

run:
	bash -c '(set -a; . ./.env; \
	 trap "kill 0" INT QUIT HUP TERM; \
	 DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ./venv/bin/python ./eodhp_web_presence/manage.py runserver & \
	 npm run dev-watch & \
	 ./venv/bin/ptw ./eodhp_web_presence & \
	 wait -f \
	)'

runserver:
	(set -a; . ./.env; DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ./venv/bin/python ./eodhp_web_presence/manage.py runserver)

requirements.txt: venv pyproject.toml
	./venv/bin/pip-compile

requirements-dev.txt: venv pyproject.toml
	./venv/bin/pip-compile --extra dev -o requirements-dev.txt

requirements: requirements.txt requirements-dev.txt

requirements-update: venv
	./venv/bin/pip-compile -U
	./venv/bin/pip-compile --extra dev -o requirements-dev.txt -U

venv:
	virtualenv -p python3.11 venv
	./venv/bin/python -m ensurepip -U 
	./venv/bin/pip3 install pip-tools

.make-venv-installed: venv requirements.txt requirements-dev.txt
	./venv/bin/pip3 install -r requirements.txt -r requirements-dev.txt
	touch .make-venv-installed

.make-node_modules-installed: package-lock.json
	npm install --from-lock-file
	touch .make-node_modules-installed

.git/hooks/pre-commit:
	./venv/bin/pre-commit install
	curl -o .pre-commit-config.yaml https://raw.githubusercontent.com/EO-DataHub/github-actions/main/.pre-commit-config-python.yaml

setup: venv requirements .make-venv-installed .make-node_modules-installed .git/hooks/pre-commit

