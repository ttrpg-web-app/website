import app

class Player(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    groupID = app.db.Column(app.db.Integer, app.db.ForeignKey('group.id'), nullable=False)
    noteContent = app.db.Column(app.db.String(500), nullable=True)
    characters = app.db.relationship('Character', backref='player', lazy=True)