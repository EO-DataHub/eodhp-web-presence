FROM node:22-slim AS js_builder

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

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive
ENV SETUPTOOLS_USE_DISTUTILS=stdlib

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update --yes --quiet \
    && apt-get install --yes --quiet --no-install-recommends \
    postgresql-client

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt
COPY eodhp_web_presence .
COPY --from=js_builder /app/eodhp_web_presence/staticfiles ./staticfiles
RUN python manage.py collectstatic --noinput


# Create a convenience script to run manage.py commands from docker CLI, e.g.
# `docker run --entrypoint manage <container_name> migrate`
RUN printf '#!/bin/bash\n\npython /app/manage.py "$@"\n' \
    > /usr/local/bin/manage && chmod +x /usr/local/bin/manage

EXPOSE 8000
ENTRYPOINT ["gunicorn", "eodhp_web_presence.wsgi:application", \
    "--bind=0.0.0.0:8000"]
CMD ["--timeout=30", "--worker-class=gevent", "--workers=4"]