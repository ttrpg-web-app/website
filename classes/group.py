import app, account, group

class Group(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    gameMasterID = app.db.Column(app.db.Integer, db.ForeignKey('account.id'), nullable=False)
    groupName = app.db.Column(app.db.String(80), nullable=False)
    groupDetails = app.db.Column(app.db.String(500), nullable=True) # aka GM's noteContent
    # groupLogFilePath = app.db.Column(app.db.String(500), nullable=False) [not implemented]
    playerList = app.db.Column(app.db.String(500), nullable=True)
    players = app.db.relationship("Player", backref='group', lazy=True)

@app.route('/addgroup', methods=['GET', 'POST'])
@login_required
def addgroup():
    if request.method == 'POST':
        groupName = request.form['name']
        groupDetails = request.form['details']
        playerList= session['username'] #get saved username for session        
        user = account.Account.query.filter_by(username=playerList).first() #uses saved username to find userID
        accountID = user.id
        new_group = group.Group(accountID=accountID, groupName=groupName, groupDetails=groupDetails, playerList=playerList) 
        app.db.session.add(new_group) #add new group to db
        app.db.session.commit()

        group_ID_Num = group.Group.query.filter_by(groupName=groupName, accountID=accountID).first() #searches for  using groupName and accountID
        groupID = group_ID_Num.id #get groupID number
        new_gameMaster = group.Group(accountID=accountID)
        app.db.session.add(new_gameMaster) #add new gameMaster to db
        app.db.session.commit()

        return redirect(url_for('dashboard'))
    return render_template('addgroup.html')