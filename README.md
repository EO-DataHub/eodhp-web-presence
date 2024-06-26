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

5. Set up environment

Environment variables can be defined in a `.env` file and imported. `example.env` can be found in the top level.
```commandline
set -a
. .env
```

## Docker Compose Setup
### Production
1. Run `docker compose up --build` to build and run the docker container. This will run the webserver on port 8000

2. Create a superuser (optional)

```commandline
docker compose exec web python manage.py createsuperuser
```

### Development Environment (Live reloading)
1. Run `docker compose -f docker-compose.dev.yaml up --build`
2. Create a superuser

```commandline
docker compose exec web python manage.py createsuperuser
```

3. Navigate to port 8000 to view the site


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



## Database importing and exporting

To export the contents of the current database, run `database_dump.py`. The user-added contents of the database are 
exported to the `web-database-exports` S3 bucket.

To overwrite the user-added tables, run `database_load.py <my_file_name.sql>` where `my_file_name.sql` can be found in 
the S3 bucket.

Both database scripts can be found in the same folder as `manage.py`