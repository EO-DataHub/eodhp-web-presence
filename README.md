# eodhp-website

## First time installation
1. Follow the instructions [here](https://github.com/UKEODHP/template-python/blob/main/README.md) for installing a 
Python 3.11 environment.

2. Install dependencies:

```commandline
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```

3. Set up environment

Copy `example.env` to `.env` and check its contents are suitable for your environment. If you wish
to use PostgreSQL (to match the production environment) then install it now, create a user and use
something like this in place of the existing settings:

```commandline
SQL_ENGINE="django.db.backends.postgresql"
SQL_DATABASE="web"
SQL_USER="<username>"
SQL_PASSWORD="..."
```

You will then need

```commandline
set -a
. .env
```

to be able to run `manage.py` from your shell (not necessary for `make run`).

4. Run migrations

```commandline
python manage.py makemigrations 
python manage.py migrate 
```

5. Set up a superuser

```commandline
python manage.py createsuperuser
```
Follow the on-screen instructions

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
make run
```

Access website at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The admin panel can be accessed at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

Changes to static files should be picked up automatically. To also pick up changes to Javascript/SCSS, run

```commandline
npm run dev-watch
```

which will run `webpack` in watch mode, rebuilding each time you save.


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