#!/bin/sh
python3 manage.py wait_for_db
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py initadmin
rm /var/run/celery/w1.pid
rm /var/run/celery/w2.pid
rm /var/run/celery/w3.pid
rm /var/run/celery/beat.pid
celery multi restart w1 w2 w3 -A main --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log --loglevel=INFO --time-limit=0
celery -A main beat --pidfile=/var/run/celery/beat.pid --logfile=/var/log/celery/beat.log --loglevel=INFO --detach
python3 manage.py runserver 0.0.0.0:5000
#gunicorn main.wsgi:application --bind 0.0.0.0:5000 -w 4