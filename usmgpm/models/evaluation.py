from usmgpm.models.db import db


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    links = db.Column(db.String, nullable=False)
    evaluation_note = db.Column(db.Text, nullable=True, default=None)
    checked = db.Column(db.Boolean, nullable=True, default=None)
