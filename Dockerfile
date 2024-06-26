FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive
 
RUN apt-get update --yes --quiet
RUN apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    curl \
    postgresql-client \
    lsb-release \
 && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - &&\
    apt-get install -y nodejs
RUN install -d /usr/share/postgresql-common/pgdg
RUN curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

RUN apt update
RUN apt -y install postgresql

RUN node -v
RUN npm -v

RUN python -m pip install --upgrade pip
RUN python -m pip install gunicorn==20.0.4

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY package*.json .
RUN npm install

ENV PATH /app/node_modules/.bin:$PATH

COPY . .

ARG NODE_ENV
ENV NODE_ENV $NODE_ENV
ARG DEBUG
ENV DEBUG $DEBUG

RUN npm run build
WORKDIR /app/eodhp_web_presence

COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
CMD ["--timeout=30", "--worker-class=gevent", "--workers=4"]
