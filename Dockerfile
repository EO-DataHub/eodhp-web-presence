FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
 
RUN apt-get update --yes --quiet
RUN apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
RUN python -m pip install gunicorn==20.0.4

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /app
RUN python eodhp_web_presence/manage.py collectstatic --noinput

COPY eodhp_web_presence .
 
EXPOSE 8000
CMD ["gunicorn", "eodhp_web_presence.wsgi:application", "--bind", "0.0.0.0:8000"]
