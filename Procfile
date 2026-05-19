release: python smart_cabin_project/manage.py migrate --noinput && python smart_cabin_project/manage.py collectstatic --noinput --clear
web: gunicorn smart_cabin_project.smart_cabin_project.wsgi:application --workers 2 --log-file -
