web: gunicorn ocp.wsgi --log-file -
python manage.py populate_ocp.py
worker: celery -A ocp worker --loglevel=info

