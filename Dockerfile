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

RUN npm install -g bootstrap@5.3.3

RUN python -m pip install --upgrade pip
RUN python -m pip install gunicorn==20.0.4

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY eodhp_web_presence .

RUN python manage.py sass eodhp_web_presence/static/scss/custom.scss eodhp_web_presence/static/css/custom.css
RUN python manage.py sass eodhp_web_presence/static/scss/fira.scss eodhp_web_presence/static/css/fira.css
RUN python manage.py sass eodhp_web_presence/static/scss/footer.scss eodhp_web_presence/static/css/footer.css
RUN python manage.py sass eodhp_web_presence/static/scss/home.scss eodhp_web_presence/static/css/home.css
RUN python manage.py sass eodhp_web_presence/static/scss/home_menu.scss eodhp_web_presence/static/css/home_menu.css
RUN python manage.py sass eodhp_web_presence/static/scss/menu.scss eodhp_web_presence/static/css/menu.css
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "eodhp_web_presence.wsgi:application", "--bind", "0.0.0.0:8000"]
