release: python smart_cabin_project/manage.py collectstatic --noinput
web: gunicorn -w 4 -b 0.0.0.0:$PORT smart_cabin_project.my_cabin.wsgi --log-file -
