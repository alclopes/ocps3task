web: gunicorn ocp.wsgi --log-file -
worker: python manage.py populate_ocp.py
worker: celery -A ocp worker --loglevel=info