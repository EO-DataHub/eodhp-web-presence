# eodhp-website

## First time installation
1. Follow the instructions [here](https://github.com/UKEODHP/template-python/blob/main/README.md) for installing a 
Python 3.11 environment.
2. Install dependencies:

```commandline
pip3 install -r eodhp_web_presence/requirements.txt
pip3 install -r eodhp_web_presence/requirements-dev.txt
```

3. Run migrations

```commandline
python manage.py makemigrations 
python manage.py migrate 
```

4. Set up a superuser

```commandline
python manage.py createsuperuser
```
Follow the on-screen instructions


## Running webserver locally
For non-production environments, run the following:

```commandline
cd eodhp_web_presence
python manage.py runserver
```

Access website at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The admin panel can be accessed at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)


## Building a dockerfile

```commandline
docker build -t eodhp-web-presence .
docker run --rm -p 8000:8000 --env-file .env eodhp-web-presence
```

Access website at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The admin panel can be accessed at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
