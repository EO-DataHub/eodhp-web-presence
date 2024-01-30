#FROM python:3.8.1-slim-buster
#FROM python:3.9.5-slim-buster
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

WORKDIR /app
COPY eodhp_website/requirements.txt .
RUN python -m pip install -r requirements.txt
 
COPY eodhp_website .
 
EXPOSE 8000
CMD ["gunicorn", "eodhp_website.wsgi:application", "--bind", "0.0.0.0:8000"]
# CMD ["python", "manage.py", "runserver"]
