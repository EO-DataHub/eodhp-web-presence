python manage.py makemigrations --settings=eodhp_website.settings.dev
python manage.py migrate --settings=eodhp_website.settings.dev
#python manage.py migrate --settings=eodhp_web_presence.settings.dev --run-syncdb