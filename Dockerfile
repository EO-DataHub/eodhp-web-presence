FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/London
ENV DEBIAN_FRONTEND=noninteractive
 
RUN apt-get update --yes --quiet
RUN apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - &&\
    apt-get install -y nodejs

RUN node -v
RUN npm -v

RUN python -m pip install --upgrade pip
RUN python -m pip install gunicorn==20.0.4

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY package*.json .
RUN npm install

COPY . .

RUN npm run build
WORKDIR /app/eodhp_web_presence

EXPOSE 8000
CMD ["gunicorn", "eodhp_web_presence.wsgi:application", "--bind", "0.0.0.0:8000"]
