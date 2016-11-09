cd c:\CorgiShot
python manage.py flush

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_data.json
python manage.py createsuperuser --username hejian --email hksac@139.com
