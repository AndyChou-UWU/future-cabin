release: python manage.py collectstatic --noinput --clear

web: gunicorn --workers 2 my_cabin.wsgi:application