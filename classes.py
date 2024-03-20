class Account:
   def __init__(self, accountID, username, email, password):
       self.accountID = accountID
       self.username = username
       self.email = email
       self.password = password

    # getters and setters
      
class Group:
    def __init__(self, groupID, gameDetails, gameLogFilePath, playerList):
        self.groupID = groupID
        self.gameDetails = gameDetails
        self.gameLogFilePath = gameLogFilePath
        self.playerList = playerList

    # getters and setters

    def leaveGroup(self, playerID): #needs to know which player is leaving
        # player removes self from group (playerList)
    def deleteGroup(self):
        # deletes a group, only the GM should have the ability to do so
    def invitePlayer(self, accountID): #needs to know which player is joining
	    # sends an invite to an account
    def addPlayer(self, accountID):
	    # creates a player to be added to playerList associated with an account
      
class GameMaster:
   def __init__(self, gameMasterID, noteContent):
       self.gameMasterID = gameMasterID
       self.noteContent = noteContent  

    # getters and setters


class Player:
   def __init__(self, playerID, currentCharacterID, noteContent):
	self.playerID = playerID
	self.currentCharacterID = currentCharacterID
	self.noteContent = noteContent
 
	# getters and setters


class Stats:
   def __init__(self, statName, statNumericValue, diceAmount, diceFaceValue)
	self.statName = statName
	self.statNumericValue = statNumericValue
	self.diceAmount = diceAmount
	self.diceFaceValue = diceFaceValue

	# getters and setters

	def roll_stat_dice(self, diceAmount, diceFaceValue):
		# rolls dice for specific stats


class Character:
	def __init__(self, characterID, accountID, name, bio, image, inventory):
        self.characterID = characterID
	    self.accountID = accountID
        self.name = name
        self.bio = bio
        self.image = image # probably a file location, can be empty
        self.inventory = inventory if inventory is not None else []

	# getters and setters

   	def uploadImage():
		# upload img into system and update display
    def add_to_inventory(self, item):
	    # add string item to inventory array
    def remove_from_inventory(self, item):
	    # remove item from array


class UniqueField:
   def __init__(self, fieldName, fieldDetails, diceAmount, diceFaceValue):
        self.fieldName = fieldName
	    self.fieldDetails = fieldDetails
	    self.diceAmount = diceAmount
 	    self.diceFaceValue = diceFaceValue

	# getters and setters

	def roll_field_dice(self, diceAmount, diceFaceValue):
		# roll dice for unique field
