from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user, current_user
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = 'abcdefghijklmnopqrstuvwxyz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

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
    groupName = db.Column(db.String(80), nullable=False)
    groupDetails = db.Column(db.String(500), nullable=True)
    # groupLogFilePath = db.Column(db.String(500), nullable=False) [not implemented]
    playerList = db.Column(db.String(500), nullable=True)
    players = db.relationship("Player", backref='group', lazy=True)
    # FKs for GameMaster only works if I comment this out @-@
    #gameMaster = db.relationship("GameMaster", backref='group', uselist=False, lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupID = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    noteContent = db.Column(db.String(500), nullable=True)
    characters = db.relationship('Character', backref='player', lazy=True)

class GameMaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accountID = db.Column(db.Integer, db.ForeignKey('group.accountID'), nullable=False)
    groupID = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    noteContent = db.Column(db.String(500), nullable=True)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accountID = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    playerID = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(80), nullable=True) #file for saved img path probably
    # inventory = array or something?
    uniqueFields = db.relationship("UniqueField", backref='character', lazy=True)
    stats = db.relationship("Stats", backref='character', lazy=True)

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characterID = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    statName = db.Column(db.String(80), nullable=False)
    diceAmount = db.Column(db.Integer, nullable=True)
    diceFaceValue = db.Column(db.Integer, nullable=True)
    statNumericValue = db.Column(db.Integer, nullable=True)

class UniqueField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characterID = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    fieldName = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(500), nullable=True)
    diceAmount = db.Column(db.Integer, nullable=True)
    diceFaceValue = db.Column(db.Integer, nullable=True)

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
    return render_template('database.html', accounts=accounts, groups=groups)

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
        session['group'] = request.form['groups'] # for some reason it just returns None
        print(session['group'])
        return redirect(url_for('viewgroup')) # GROUP PAGE DOES NOT EXIT YET
    else:
        groups = Group.query.filter_by(accountID=current_user.id)
        return render_template('dashboard.html', groups=groups, name=current_user.username)

@app.route('/viewgroup')
@login_required
def viewgroup():
    # code...
    selectedGroup = session['selectedGroup']
    return render_template('viewgroup.html', selectedGroup=selectedGroup)

@app.route('/addgroup', methods=['GET', 'POST'])
@login_required
def addgroup():
    if request.method == 'POST':
        groupName = request.form['name']
        groupDetails = request.form['details']
        playerList= session['username'] #get saved username for session        
        user = Account.query.filter_by(username=playerList).first() #uses saved username to find userID
        accountID = user.id
        new_group = Group(accountID=accountID, groupName=groupName, groupDetails=groupDetails, playerList=playerList) 
        db.session.add(new_group) #add new group to db
        db.session.commit()

        group_ID_Num = Group.query.filter_by(groupName=groupName, accountID=accountID).first() #searches for  using groupName and accountID
        groupID = (str(group_ID_Num.id) + str(accountID)) #concates groupID and accountID to create groupID
        new_gameMaster = GameMaster(accountID=accountID,groupID=groupID)
        db.session.add(new_gameMaster) #add new gameMaster to db
        db.session.commit()

        return redirect(url_for('dashboard'))
    return render_template('addgroup.html')

@app.route('/addcharacter')
@login_required
def addcharacter():
    return render_template('addcharacter.html')

if __name__ == '__main__':
    app.run(debug=True)