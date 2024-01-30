# eodhp-website

## First time installation
1. Follow the instructions [here](https://github.com/UKEODHP/template-python/blob/main/README.md) for installing a 
Python 3.11 environment.
2. Install dependencies:

```commandline
pip3 install -r eodhp_website/requrements.txt
pip3 install -r eodhp_website/requrements-dev.txt
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

5. Access website at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

The admin panel can be accessed at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
