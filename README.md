# EODHP Web Presence

## Install Dependencies

Python and npm are required to build this project.

### Minimal Install

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install .[dev]
npm install
```

### Recommended Development Install

```bash
make setup
```

This will create a virtual environment called `venv`, build `requirements.txt` and `requirements-dev.txt` from `pyproject.toml` if they're out of date, install the Python and Node dependencies and install `pre-commit`.

It's safe and fast to run `make setup` repeatedly as it will only update these things if they have changed.

After `make setup` you can run `pre-commit` to run pre-commit checks on staged changes and `pre-commit run --all-files` to run them on all files. This replicates the linter checks that run from GitHub actions.

## Running the App

### Initial Configuration

```bash
npm run dev  # build webpack bundles
cd eodhp_web_presence
python manage.py migrate  # create initial sqlite database
python manage.py createsuperuser  # create an admin user for wagtail admin backend
```

### Development

When just working with the Python code, you can run the app using Django runserver standalone. The app will be available on http://127.0.0.1:8000 by default.

```bash
npm run dev  # create webpack bundles to be served statically by Django
export DEBUG=true
cd eodhp_web_presence
python manage.py runserver  # will reload on any changes to Python code
```

If you are also working with the webpack source files and would like to see hot reloading then you can serve the app using the webpack dev server, which by default is served on http://127.0.0.1:3000. This will hot reload the app when the webpack source files in assets/ are updated. This requires two terminals, one to serve the webpack bundles and the other to run the Django app.

```bash
# terminal 1
npm run serve  # will reload on any changes to webpack source files
```

```bash
# terminal 2
export DEBUG=true
export WEBPACK_SERVE=true
cd eodhp_web_presence
python manage.py runserver  # will reload on any changes to Python code
```

## Configuration

See _eodhp_web_presence/eodhp_web_presence/settings.py_ for all available environment variables.

Copy `example.env` to `.env` and check its contents are suitable for your environment. If you wish to use PostgreSQL (to match the production environment) then install it now, create a user and use something like this in place of the existing settings:

```bash
# production database
SQL_ENGINE="django.db.backends.postgresql"
SQL_DATABASE="web"
SQL_USER="<username>"
SQL_PASSWORD="..."
```

To load env vars from .env file for export to `python manage.py runserver`:

```bash
set -a  # enable export of all env vars from shell
. .env  # source the env vars into current shell
```

This is not necessary for `make run` or other make targets.

## Testing

```bash
cd eodhp_web_presence
pytest .
```

## Usage

Access website at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

The admin panel can be accessed at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin).

## Build Image

A Dockerfile has been provided for packaging the app for deployment in production.

```bash
docker build -t eodhp-web-presence .
docker run --rm -p 8000:8000 --env-file .env eodhp-web-presence
```

You will need to serve static files via a proxy or otherwise.

## Database importing and exporting

To export the contents of the current database, run `database_dump.py`. The user-added contents of the database are exported to the `web-database-exports` S3 bucket.

To overwrite the user-added tables, run `database_load.py <my_file_name.sql>` where `my_file_name.sql` can be found in the S3 bucket.

Both database scripts can be found in the same folder as `manage.py`.
