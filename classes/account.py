import app

class Account(app.UserMixin, app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    username = app.db.Column(app.db.String(80), unique=True, nullable=False)
    email = app.db.Column(app.db.String(80), nullable=False)
    password = app.db.Column(app.db.String(80), nullable=False)
    groups = app.db.relationship('Group', backref='account', lazy=True)
    characters = app.db.relationship('Character', backref='account', lazy=True)