# eodhp-website

## First time installation
1. Follow the instructions [here](https://github.com/UKEODHP/template-python/blob/main/README.md) for installing a
Python 3.11 environment. You will also need to install nodejs.

2. Install dependencies:

```commandline
make setup
```

This will create a virtual environment called `venv`, build `requirements.txt` and
`requirements-dev.txt` from `pyproject.toml` if they're out of date, install the Python
and Node dependencies and install `pre-commit`.

It's safe and fast to run `make setup` repeatedly as it will only update these things if
they have changed.

After `make setup` you can run `pre-commit` to run pre-commit checks on staged changes and
`pre-commit run --all-files` to run them on all files. This replicates the linter checks that
run from GitHub actions.

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

to be able to run `manage.py` from your shell (not necessary for `make run` or other make targets).

## Running for Development

The system can be run in development in two ways: directly, and in Docker with Docker Compose.
Running in Docker provides hot-reload of changes to JS/CSS, meaning that no refresh of the browser
is necessary. However, this sometimes fails. It will also require a Docker image rebuild when
dependencies change and does not work with a PostgreSQL database.

### Running Directly

1. Run migrations - this will create the initial database contents if necessary. This step will
   need to be repeated whenever the migrations are changed (by any developer).

```commandline
./venv/bin/python ./eodhp_web_presence/manage.py migrate
```

2. Set up a superuser

```commandline
./venv/bin/python ./eodhp_web_presence/manage.py createsuperuser
```
Follow the on-screen instructions.

3. Either build and run the webserver in production mode

```commandline
. venv/bin/activate
npm run build
cd eodhp_web_presence
gunicorn eodhp_web_presence.wsgi:application --bind 0.0.0.0:8000
```

or (more useful for development)

```commandline
make run
```

This will run three things:

* Django/Wagtail in DEBUG=True mode, including serving the static files and Webpack build outputs.
* Webpack in watch mode so that Webpack build outputs are rebuilt automatically every time you
  change a source file.
* `ptw` (pytest watcher) which will run the pytest tests on source file change.
  
Access website at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The admin panel can be accessed at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

Changes to static files and Javascript/CSS should be picked up automatically.


### Running in Docker Compose

Note that this currently runs as root inside the container and may create some files owned by root,
causing errors if you later try to run the unit tests or server outside Docker. Delete or change
the ownership of these files if you need to.

#### Production-like

1. Run `docker compose up --build` to build and run the docker container. This will run the webserver on port 8000

2. Create a superuser (optional)

```commandline
docker compose exec web python manage.py createsuperuser
```

#### Development Environment (Live reloading)

1. Run `docker compose -f docker-compose.dev.yaml up --build`
2. Create a superuser

```commandline
docker compose exec web python manage.py createsuperuser
```

3. Navigate to port 8000 to view the site


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

