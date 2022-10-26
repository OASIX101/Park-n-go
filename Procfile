web: gunicorn -b "0.0.0.0:$PORT" -w 3 TM30_project.wsgi
release: python manage.py migrate