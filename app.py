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
    
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accountID = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    groupName = db.Column(db.String(80), unique=True, nullable=False)
    groupDetails = db.Column(db.String(500), nullable=True) # noteContent

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characterID = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    groupID = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    accountID = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accountID = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    playerID = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(80), nullable=True) #file for saved img path probably

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
        
        existing_user = Account.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already exists. Please choose a different username."
            return render_template('register.html', error=error)
        else:
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

@app.route('/gmview', methods=['GET', 'POST'])
@login_required
def gmview():
    if request.method == 'POST':
        # store groupID from POST request form into group
        if 'group' not in session:
             session['group'] = []
        formString = request.form['group']
        idNumStr = re.search(r'\d+', formString)
        idNumStr2 = idNumStr.group()
        idNum = int(idNumStr2)
        session['group'] = idNum
        return redirect(url_for('viewgroup'))
    
@app.route('/playerview', methods=['GET', 'POST'])
@login_required
def playerview():
    if request.method == 'POST':
        # store groupID from POST request form into group
        if 'group' not in session:
             session['group'] = []
        formString = request.form['group']
        idNumStr = re.search(r'\d+', formString)
        idNumStr2 = idNumStr.group()
        idNum = int(idNumStr2)
        session['group'] = idNum
        return redirect(url_for('viewgroup'))

@app.route('/dashboard', methods=['GET', 'POST']) # specifically account background
@login_required
def dashboard():
    # needs code probably
    if request.method == 'POST':
        # store groupID from POST request form into group
        if 'group' not in session:
             session['group'] = []
        formString = request.form['pg']
        idNumStr = re.search(r'\d+', formString)
        idNumStr2 = idNumStr.group()
        idNum = int(idNumStr2)
        session['group'] = idNum
        # storing groupID in session ends here

        return redirect(url_for('viewgroup'))
    else:
        groups = Group.query.filter_by(accountID=current_user.id)

        player_query = Player.query.filter_by(accountID=current_user.id).all()
        group_ids = [player.groupID for player in player_query]
        playerGroups = Group.query.filter(Group.id.in_(group_ids))
        
        
        amtG = groups.count()
        amtPG = playerGroups.count()

        return render_template('dashboard.html', groups=groups, name=current_user.username, playerGroups=playerGroups, amtG=amtG, amtPG=amtPG) #players=playerGroups

@app.route('/viewgroup')
@login_required
def viewgroup():
    # retrieve group from the session arr
    selectedGroupID = session['group']
    selectedGroup = Group.query.filter_by(id=selectedGroupID)

    # retrieve player classes with matching group id
    players = Player.query.filter_by(groupID=selectedGroupID).all()
    
    # retrieve and send the characters attached to players !!
    character_ids = [player.characterID for player in players]
    characters_in_group = Character.query.filter(Character.id.in_(character_ids)).all()

    stats = Stats.query.filter(Stats.characterID.in_(character_ids)).all()
    uniqueFields = UniqueField.query.filter(UniqueField.characterID.in_(character_ids)).all()

    currentUser = session['username'] #get saved username for session        
    currentUserID = Account.query.filter_by(username=currentUser).first().id #uses saved username to find userID

    return render_template('viewgroup.html', selectedGroup=selectedGroup, players=players, characters=characters_in_group, stats=stats, uniqueFields=uniqueFields, currentUserID=currentUserID)

@app.route('/addgroup', methods=['GET', 'POST'])
@login_required
def addgroup():
    if request.method == 'POST':
        groupName = request.form['name']
        groupDetails = request.form['details']
        playerList = session['username'] #get saved username for session        
        user = Account.query.filter_by(username=playerList).first() #uses saved username to find userID
        accountID = user.id
        new_group = Group(accountID=accountID, groupName=groupName, groupDetails=groupDetails) 
        db.session.add(new_group) #add new group to db
        db.session.commit()

        return redirect(url_for('dashboard'))
    return render_template('addgroup.html')

@app.route('/joingroup', methods=[ 'GET', 'POST'])
@login_required
def joingroup():
     if request.method == 'POST':
          
          username = session['username']
          user = Account.query.filter_by(username=username).first()
          existing_character = Character.query.filter_by(accountID=user.id).first()
          if not existing_character:
            error = "You need a character to join a group."
            groups = Group.query.all()
            return render_template('joingroup.html', error=error, groups=groups)
          else:
            nameOfGroup = request.form['group_name']
            character = request.form['character']
            groupQuery = Group.query.filter_by(groupName=nameOfGroup).first()
            groupID = groupQuery.id
            accountID = current_user.id
            new_player = Player(groupID = groupID, accountID = accountID, characterID = character)
            db.session.add(new_player) #add new group to db
            db.session.commit()
          return redirect(url_for('dashboard'))

     else:
        characters = Character.query.filter_by(accountID=current_user.id)
        groups = Group.query.all()
        # groupamt = groups.count()
        return render_template('joingroup.html', groups = groups, characters=characters)

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

    stats = Stats.query.filter_by(characterID=id).all()
    for stat in stats:
        db.session.delete(stat)
        db.session.commit()

    ufs = UniqueField.query.filter_by(characterID=id).all()
    for uf in ufs:
        db.session.delete(uf)
        db.session.commit()

    return redirect(url_for('characters'))

@app.route("/leavegroup/<int:id>", methods=['POST', 'GET'])
@login_required
def leavegroup(id):
    obj = Player.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/deletegroup/<int:id>", methods=['POST', 'GET'])
@login_required
def deletegroup(id):
    obj = Group.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()

    players = Player.query.filter_by(groupID=id).all()
    for player in players:
        db.session.delete(player)
        db.session.commit()

    return redirect(url_for('dashboard'))

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

@app.route('/adduniquefield/<int:id>', methods = ['POST', 'GET'])
@login_required
def adduniquefield(id):
    session['uniquefieldid'] = id
    characters = Character.query.filter_by(id=id)

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


@app.route('/viewuniquefields/<int:id>', methods=['GET', 'POST']) #to view and edit uniquefields
@login_required
def viewuniquefields(id):
    session['viewuniquefields'] = id
    curUniqueField = UniqueField.query.filter_by(characterID =id)
    return render_template('viewuniquefields.html', uniquefields=curUniqueField)

@app.route('/edituniquefield/<int:id>', methods = ['POST', 'GET']) #get id to pass to addstats
@login_required
def edituniquefield(id):

     session['viewuniquefields']=id
     getUniqueField = UniqueField.query.filter_by(id=id)

     return render_template('edituniquefield.html', uniquefields=getUniqueField)

@app.route('/edituniquefield/', methods = ['POST', 'GET'])
@login_required
def edituniquefields():
     curUField = session['viewuniquefields']
     getCurUField = UniqueField.query.get(curUField)

     if request.method == 'POST':
          getCurUField.fieldName = request.form['fieldname']
          getCurUField.details = request.form['statdetails']
          db.session.commit()
          return redirect(url_for('characters'))

     return render_template('edituniquefield.html', uniquefields=getCurUField)

@app.route("/removeuniquefield/<int:id>", methods=['POST', 'GET'])
@login_required
def removeuniquefield(id):
    obj = UniqueField.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()

    return redirect(url_for('characters'))

@app.route("/removestats/<int:id>", methods=['POST', 'GET'])
@login_required
def removestats(id):
    obj = Stats.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()

    return redirect(url_for('characters'))

@app.route('/viewstats/<int:id>', methods=['GET', 'POST']) #to view and edit stats
@login_required
def viewstats(id):
    session['viewstat'] = id

    curStats = Stats.query.filter_by(characterID =id)
    return render_template('viewstats.html', stats=curStats)

@app.route('/editstats/<int:id>', methods = ['POST', 'GET']) #get id to pass to addstats
@login_required
def editstats(id):

     session['sessionstats']=id
     getStats = Stats.query.filter_by(id=id)

     return render_template('editstats.html', stats=getStats)

@app.route('/editstats/', methods = ['POST', 'GET']) #get id to pass to addstats
@login_required
def editstatss():
     stats = session['sessionstats']
     getStats = Stats.query.get(stats)

     if request.method == 'POST':
          getStats.statName = request.form['fieldname']
          getStats.statNumericValue = request.form['statvalue']
          db.session.commit()
          return redirect(url_for('characters'))

     return render_template('editstats.html', stats=getStats)



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

if __name__ == '__main__':
    app.run(debug=True)