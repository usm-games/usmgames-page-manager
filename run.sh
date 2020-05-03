flask db init
flask db migrate
gunicorn -w 4 "usmgpm.app:init_app()"