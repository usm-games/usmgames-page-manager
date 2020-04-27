from flask import Flask

from usmgpm.models import init_db
from usmgpm.resources import init_api


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)
init_api(app)
