import app

class Character(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    accountID = app.db.Column(app.db.Integer, app.db.ForeignKey('account.id'), nullable=False)
    playerID = app.db.Column(app.db.Integer, app.db.ForeignKey('player.id'), nullable=False)
    name = app.db.Column(app.db.String(80), nullable=False)
    bio = app.db.Column(app.db.String(500), nullable=True)
    image = app.db.Column(app.db.String(80), nullable=True) #file for saved img path probably
    # inventory = array or something?
    uniqueFields = app.db.relationship("UniqueField", backref='character', lazy=True)
    stats = app.db.relationship("Stats", backref='character', lazy=True)

@app.route('/addcharacter')
@login_required
def addcharacter():
    return render_template('addcharacter.html')

if __name__ == '__main__':
    app.app.run(debug=True)