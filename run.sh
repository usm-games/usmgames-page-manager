flask db upgrade
gunicorn -w 4 "usmgpm.app:init_app()"