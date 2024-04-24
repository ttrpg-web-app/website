import app

class Stats(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    characterID = app.db.Column(app.db.Integer, db.ForeignKey('character.id'), nullable=False)
    statName = app.db.Column(app.db.String(80), nullable=False)
    diceAmount = app.db.Column(app.db.Integer, nullable=True)
    diceFaceValue = app.db.Column(app.db.Integer, nullable=True)
    statNumericValue = app.db.Column(app.db.Integer, nullable=True)