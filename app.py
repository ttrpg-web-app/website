from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user, current_user
import sqlite3
import os, re

app = Flask(__name__)

app.config['SECRET_KEY'] = 'abcdefghijklmnopqrstuvwxyz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Account.query.get(int(id))

class Account(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    groups = db.relationship('Group', backref='account', lazy=True)
    characters = db.relationship('Character', backref='account', lazy=True)
    
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accountID = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    groupName = db.Column(db.String(80), unique=True, nullable=False)
    groupDetails = db.Column(db.String(500), nullable=True) # noteContent
    # groupLogFilePath = db.Column(db.String(500), nullable=False) [not implemented]
    players = db.relationship("Player", backref='group', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characterID = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    groupID = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    characterID = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # characters = db.relationship('Character', backref='player', lazy=True)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accountID = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    playerID = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(80), nullable=True) #file for saved img path probably
    uniqueFields = db.relationship("UniqueField", backref='character', lazy=True)
    stats = db.relationship("Stats", backref='character', lazy=True)
    # account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # account = db.relationship('Account', backref=db.backref('characters', lazy=True))
    # account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # account = db.relationship('Account', backref=db.backref('characters', lazy=True))

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characterID = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    statName = db.Column(db.String(80), nullable=False)
    statNumericValue = db.Column(db.Integer, nullable=True)

class UniqueField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characterID = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    fieldName = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(500), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
        return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'] # may want to hash the password

        new_account = Account(username=username, email=email, password=password)
        db.session.add(new_account)
        db.session.commit()

        return redirect(url_for('login'))
    # else GET method:
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Account.query.filter_by(username=username).first()

        if user and user.password == password:
            # login success 
            session['username'] = request.form['username'] #save username for session        
            login_user(user)   
            return redirect(url_for('dashboard')) # change from index to dashboard later
        else: # user/pass do not exist in db
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/database')
def database():
    accounts = Account.query.all()
    groups = Group.query.all()
    players = Player.query.all()
 #   gameMasters = GameMaster.query.all()
    characters = Character.query.all()
    statistics = Stats.query.all()
    uniqueFields = UniqueField.query.all()
    return render_template('database.html', accounts=accounts, groups=groups, players=players, characters=characters, statistics=statistics, uniqueFields=uniqueFields)

@app.route('/logout')
@login_required
def logout():
    session.pop("username", None) #removed saved username for this session
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST']) # specifically account background
@login_required
def dashboard():
    # needs code probably
    if request.method == 'POST':
        # store groupID from POST request form into group
        if 'group' not in session:
             session['group'] = []
        formString = request.form['groups']
        idNumStr = re.search(r'\d+', formString)
        idNumStr2 = idNumStr.group()
        idNum = int(idNumStr2)
        session['group'] = idNum
        # storing groupID in session ends here
        return redirect(url_for('viewgroup')) # GROUP PAGE DOES NOT EXIT YET
    else:
        groups = Group.query.filter_by(accountID=current_user.id)
        return render_template('dashboard.html', groups=groups, name=current_user.username)

@app.route('/viewgroup')
@login_required
def viewgroup():
    # code...
    selectedGroupID = session['group']
    selectedGroup = Group.query.filter_by(id=selectedGroupID)
    return render_template('viewgroup.html', selectedGroup=selectedGroup)

@app.route('/addgroup', methods=['GET', 'POST'])
@login_required
def addgroup():
    if request.method == 'POST':
        groupName = request.form['name']
        groupDetails = request.form['details']
        playerList = session['username'] #get saved username for session        
        user = Account.query.filter_by(username=playerList).first() #uses saved username to find userID
        accountID = user.id
        new_group = Group(accountID=accountID, groupName=groupName, groupDetails=groupDetails, playerList=playerList) 
        db.session.add(new_group) #add new group to db
        db.session.commit()

        return redirect(url_for('dashboard'))
    return render_template('addgroup.html')

@app.route('/joingroup', methods=[ 'GET', 'POST'])
@login_required
def joingroup():
     if request.method == 'POST':
          nameOfGroup = request.form['group_name']
          groupQuery = Group.query.filter_by(groupName=nameOfGroup).first()
          groupID = groupQuery.id #
          accountID = current_user.id
          new_player = Player(groupID = groupID, characterID = accountID)
          db.session.add(new_player) #add new group to db
          db.session.commit()
          return redirect(url_for('dashboard'))
     else:
        groups = Group.query.all()  
        return render_template('joingroup.html', groups = groups)
     
# @app.route('/group', methods= ['GET', 'POST'])
# @login_required
# def group():
#      if request.method == "POST":
#           nameOfCharacter = request.form['character_name']
#           dbs.session.update 

@app.route('/uploads/<path:path>')
def images(path):
    return send_from_directory('uploads', path)

@app.route('/characters', methods=['GET', 'POST'])
@login_required
def characters():
    characters = Character.query.filter_by(accountID=current_user.id)
    return render_template('characters.html', characters=characters)

@app.route("/removecharacter/<int:id>", methods=['POST', 'GET'])
@login_required
def removecharacter(id):
    obj = Character.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for('characters'))

@app.route('/addcharacter',methods = ['POST', 'GET'] )
@login_required
def addcharacter():
	if(request.method == 'POST'):
		name= request.form['name']
		bio = request.form['bio']
		image = request.files['image']
		accountID = current_user.id
		if 'image' not in request.files:
			flash('No file part')
			return redirect('addcharacter.html')
		if image.filename == '':
			flash('The file name is empty')
			return redirect('addcharacter.html')
		if image:
			image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
			new_character = Character(name=name, bio=bio, image=image.filename, accountID = accountID)
			db.session.add(new_character),
			db.session.commit()
			return render_template('addcharacter.html')
	
	return render_template('addcharacter.html')

@app.route('/adduniquefield' ,methods = ['POST', 'GET'])
@login_required
def adduniquefield():
     
     return render_template('adduniquefield.html')


@app.route('/viewstats/<int:id>', methods=['GET', 'POST']) #to view and edit stats
@login_required
def viewstats(id):
    session['char'] = id

    curStats = Stats.query.filter_by(characterID=id) 
    return render_template('viewstats.html', stats=curStats)

@app.route('/viewstats/', methods=['GET', 'POST']) #to view and edit stats
@login_required
def viewstatss():
    curStatsChar = session['char']
    curStats = Stats.query.filter_by(characterID=curStatsChar)
    if request.method == 'POST':
        session['stats'] = request.form['stats']
        return redirect(url_for('editstats'))
    else:
        return render_template('viewstats.html', stats=curStats)


@app.route('/editstats', methods=['GET', 'POST'])
@login_required
def editstats():
    if request.method == 'POST':
         return redirect(url_for('characters'))
    else:
        curStats = session['stats']
        justNum = re.search(r'\d+', curStats)
        justNum2 = justNum.group()
        idNum = int(justNum2)
        idNumPass = Stats.query.filter_by(id=idNum)
        return render_template('editstats.html', stats=idNumPass)

@app.route('/addstats/<int:id>', methods = ['POST', 'GET']) #get id to pass to addstats
@login_required
def addstats(id):
     session['char'] = id
     characters = Character.query.filter_by(id=id)     
     return render_template('addstats.html', characters=characters)

@app.route('/addstats/', methods = ['POST', 'GET'])
@login_required
def addstatss():
     id = session['char']
     characters = Character.query.filter_by(id=id)
     if request.method == 'POST':
        statName = request.form['fieldname']
        statNumericValue = request.form['statvalue']
        new_stats = Stats(characterID=id, statName=statName, statNumericValue=statNumericValue)
        db.session.add(new_stats)
        db.session.commit()
        return redirect(url_for('characters'))
     return render_template('addstats.html', characters=characters)

#@app.route('/adduniquefield/<int:id>', methods = ['POST', 'GET'])
#@login_required
#def adduniquefield(id):
#    return render_template('adduniquefield.html')

@app.route('/addstats/<int:id>', methods = ['POST', 'GET']) #get id to pass to addstats
@login_required
def addstats(id):
     return render_template('addstats.html')
@app.route('/editcharacter/<int:id>', methods=['GET', 'POST'])
@login_required
def editCharacter(id):
      character = Character.query.get(id)
      if request.method == 'POST':
           character.name = request.form['name']
           character.bio  = request.form['bio']
           if 'image'in request.files:
                image = request.files['image']
                if image.filename != '':
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
                    character.image = image.filename
                db.session.commit()
                return redirect(url_for('characters'))           

      return render_template('editcharacter.html', character = character)

@app.route('/adduniquefield/<int:id>', methods = ['POST', 'GET'])
@login_required
def adduniquefield(id):
    session['uniquefieldid'] = id
    characters = Character.query.filter_by(id=id)
    if request.method == 'POST':
          fieldName = request.form['unique_field_name']
          details = request.form['unique_field_details']
          new_uniqueField = UniqueField(characterID = id,  fieldName= fieldName, details= details)
          db.session.add(new_uniqueField) #add new unique field to db
          db.session.commit()
          return redirect(url_for('characters'))
    return render_template('adduniquefield.html', characters = characters)

@app.route('/adduniquefield/', methods = ['POST', 'GET'])
@login_required
def adduniquefields():
    id = session['uniquefieldid']
    characters = Character.query.filter_by(id=id)
    if request.method == 'POST':
          fieldName = request.form['unique_field_name']
          details = request.form['unique_field_details']
          new_uniqueField = UniqueField(characterID = id,  fieldName= fieldName, details= details)
          db.session.add(new_uniqueField) #add new unique field to db
          db.session.commit()
          return redirect(url_for('characters'))
    return render_template('adduniquefield.html', characters = characters)

# @app.route('/joingroup', methods=[ 'GET', 'POST'])
# @login_required
# def joingroup():
#      if request.method == 'POST':
#           nameOfGroup = request.form['name']
#           groupQuery = Group.query.filter_by(groupName=nameOfGroup).first()
#           groupID = groupQuery.id #
#           accountID = current_user.id
#           new_player = Player(groupID = groupID, characterID = accountID)
#           db.session.add(new_player) #add new group to db
#           db.session.commit()
#           return redirect(url_for('dashboard'))
#      return render_template('joingroup.html')

if __name__ == '__main__':
    app.run(debug=True)
