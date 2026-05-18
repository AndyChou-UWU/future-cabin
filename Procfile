release: python manage.py collectstatic --noinput --clear

web: gunicorn my_cabin.wsgi:application --workers 2