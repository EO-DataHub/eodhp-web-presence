# syntax=docker/dockerfile:1@sha256:4a43a54dd1fedceb30ba47e76cfcf2b47304f4161c0caeac2db1c61804ea3c91
FROM node:24-slim@sha256:d8e448a56fc63242f70026718378bd4b00f8c82e78d20eefb199224a4d8e33d8 AS js_builder

# Only set in GitHub Actions.
ARG GIT_REF_NAME="no-ref-name"
ENV GIT_REF_NAME=$GIT_REF_NAME
ARG GIT_SHA="no-sha"
ENV GIT_SHA=$GIT_SHA

WORKDIR /app

COPY package*.json .
RUN npm install

COPY assets ./assets
COPY webpack.config.js .eslintrc.js .stylelintrc ./

RUN npm run build

# Build stage
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim@sha256:e2fd64bdac73bd01b5013d324d9fe2e82055dfd661bc55f8006c2796da9b1d04 AS py_builder

ENV UV_NO_DEV=1

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update --yes --quiet \
    && apt-get install --yes --quiet --no-install-recommends \
    build-essential

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy project files and sync the project
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Final stage
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim@sha256:e2fd64bdac73bd01b5013d324d9fe2e82055dfd661bc55f8006c2796da9b1d04

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update --yes --quiet \
    && apt-get install --yes --quiet --no-install-recommends \
    postgresql-client

WORKDIR /app

# Copy the entire app with venv from the builder
COPY --from=py_builder /app /app

COPY --from=js_builder /app/eodhp_web_presence/staticfiles ./eodhp_web_presence/staticfiles
RUN uv run --no-sync python eodhp_web_presence/manage.py collectstatic --noinput

# Create a convenience script to run manage.py commands from docker CLI, e.g.
# `docker run --entrypoint manage <container_name> migrate`
RUN printf '#!/bin/bash\n\nuv run --no-sync python /app/eodhp_web_presence/manage.py "$@"\n' \
    > /usr/local/bin/manage && chmod +x /usr/local/bin/manage

EXPOSE 8000
ENTRYPOINT ["uv", "run", "--no-sync", "gunicorn", "eodhp_web_presence.wsgi:application", \
    "--chdir=/app/eodhp_web_presence", "--bind=0.0.0.0:8000"]
CMD ["--timeout=30", "--worker-class=gevent", "--workers=4"]
