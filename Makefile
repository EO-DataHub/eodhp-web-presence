VERSION ?= latest
IMAGENAME = eodhp-web-presence
DOCKERREPO ?= public.ecr.aws/eodh
uv-run ?= uv run --no-sync

.PHONY: dockerbuild
dockerbuild:
	DOCKER_BUILDKIT=1 docker build -t ${IMAGENAME}:${VERSION} .

.PHONY: dockerpush
dockerpush: dockerbuild
	docker tag ${IMAGENAME}:${VERSION} ${DOCKERREPO}/${IMAGENAME}:${VERSION}
	docker push ${DOCKERREPO}/${IMAGENAME}:${VERSION}

.PHONY: test
test:
	(set -a; . ./.env; DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ${uv-run} ptw ./eodhp_web_presence)

.PHONY: testonce
testonce:
	(set -a; . ./.env; DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ${uv-run} pytest ./eodhp_web_presence)

.PHONY: run
run:
	bash -c '(set -a; . ./.env; \
	 trap "kill 0" INT QUIT HUP TERM; \
	 DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ${uv-run} python ./eodhp_web_presence/manage.py runserver & \
	 npm run dev-watch & \
	 ${uv-run} ptw ./eodhp_web_presence & \
	 wait -f \
	)'

.PHONY: runserver
runserver:
	(set -a; . ./.env; DEBUG=True PAGE_CACHE_LENGTH=0 STATIC_FILE_CACHE_LENGTH=0 ${uv-run} python ./eodhp_web_presence/manage.py runserver)

.git/hooks/pre-commit:
	${uv-run} pre-commit install
	curl -o .pre-commit-config.yaml https://raw.githubusercontent.com/EO-DataHub/github-actions/main/.pre-commit-config-python.yaml

.make-node_modules-installed: package-lock.json
	npm install --from-lock-file
	touch .make-node_modules-installed

.PHONY: setup
setup: update .make-node_modules-installed .git/hooks/pre-commit

.PHONY: pre-commit
pre-commit:
	${uv-run} pre-commit

.PHONY: pre-commit-all
pre-commit-all:
	${uv-run} pre-commit run --all-files

.PHONY: check
check:
	${uv-run} ruff check
	${uv-run} ruff format --check --diff
	${uv-run} pyright
	${uv-run} validate-pyproject pyproject.toml

.PHONY: format
format:
	${uv-run} ruff check --fix
	${uv-run} ruff format

.PHONY: install
install:
	uv sync --frozen

.PHONY: update
update:
	uv sync
