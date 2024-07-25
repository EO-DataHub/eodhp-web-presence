# syntax=docker/dockerfile:1
FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive
ENV SETUPTOOLS_USE_DISTUTILS=stdlib

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update --yes --quiet \
    && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    curl \
    postgresql-client \
    lsb-release \
    git
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - &&\
    apt-get install -y nodejs
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    install -d /usr/share/postgresql-common/pgdg \
    && curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
    && apt-get update \
    && apt-get -y install postgresql

RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --upgrade pip

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip python -m pip install -r requirements.txt
COPY package*.json .
RUN npm install

ENV PATH /app/node_modules/.bin:$PATH

COPY run_migrations.sh webpack.config.js .eslintrc.json .stylelintrc .
COPY eodhp_web_presence eodhp_web_presence/

RUN git clone https://github.com/EO-DataHub/github-actions.git
RUN git init ..
RUN (cd ./github-actions && pre-commit install-hooks)

ARG NODE_ENV
ENV NODE_ENV $NODE_ENV
ARG DEBUG
ENV DEBUG $DEBUG

# Only set in GitHub Actions.
ARG GIT_REF_NAME="no-ref-name"
ENV GIT_REF_NAME $GIT_REF_NAME
ARG GIT_SHA="no-sha"
ENV GIT_SHA $GIT_SHA

RUN npm install --save-dev webpack
RUN npm run build
# collectstatic is done here so that production builds can have permission to modify their root
# filesystem (or at least the code itself) removed. In development collectstatic is run during
# startup and/or isn't necessary.
RUN sh -c '[ "$NODE_ENV" = "development" ] || python /app/eodhp_web_presence/manage.py collectstatic --noinput'
WORKDIR /app/eodhp_web_presence

COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
CMD ["--timeout=30", "--worker-class=gevent", "--workers=4"]
