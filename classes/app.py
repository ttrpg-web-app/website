# frameworks & backend
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user, current_user
import sqlite3

# classes/tables for the database
import account, group, player, character, stats, uniqueField

app = Flask(__name__)

app.config['SECRET_KEY'] = 'abcdefghijklmnopqrstuvwxyz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return account.Account.query.get(int(id))

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

        new_account = account.Account(username=username, email=email, password=password)
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

        user = account.Account.query.filter_by(username=username).first()

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
    accounts = account.Account.query.all()
    groups = group.Group.query.all()
    players = player.Player.query.all()
    characters = character.Character.query.all()
    statistics = stats.Stats.query.all()
    uniqueFields = uniqueField.UniqueField.query.all()
    return render_template('database.html', accounts=accounts, groups=groups, players=players, characters=characters, statistics=statistics, uniqueFields=uniqueFields)

@app.route('/logout')
@login_required
def logout():
    session.pop("username", None) #removed saved username for this session
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # needs code probably
    return render_template('dashboard.html') #need to pass needed variables