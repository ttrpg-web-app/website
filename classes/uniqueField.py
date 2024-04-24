import app

class UniqueField(app.db.Model):
    id = app.app.db.Column(app.app.db.Integer, primary_key=True)
    characterID = app.db.Column(app.db.Integer, app.db.ForeignKey('character.id'), nullable=False)
    fieldName = app.db.Column(app.db.String(80), nullable=False)
    details = app.db.Column(app.db.String(500), nullable=True)
    diceAmount = app.db.Column(app.db.Integer, nullable=True)
    diceFaceValue = app.db.Column(app.db.Integer, nullable=True)