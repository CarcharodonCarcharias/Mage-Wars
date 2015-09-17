#######
#v2.0.0.0#
#######

def optionsMenu(group,x=0,y=0):
	#Consolidates the many game toggle options into a single menu
	settingsList = [
		{True : "Auto Calculate Upkeep Effects Enabled",False: "Auto Calculate Upkeep Effects Disabled","setting": "AutoResolveEffects"},
		{True : "Auto Attachments Enabled",False: "Auto Attachments Disabled","setting": "AutoAttach"},
		{True : "Prompt for Game Selection and Board",False: "Standard Arena Gameboard Enabled","setting": "AutoBoard"},
		{True : "Battle Calculator Enabled",False: "Battle Calculator Disabled","setting": "BattleCalculator"},
		{True : "Sound Effects Enabled",False: "Sound Effects Disabled","setting": "AutoConfigSoundFX"},
		{True : "Place the Roll Dice Area to the Side",False: "Place the Dice Roll Area to the Bottom","setting": "RDALocation"},
		{True : "Tutorial Enabled",False: "Tutorial Disabled","setting": "octgnTutorial"}
	]
	choices = [e[getSetting(e["setting"],True)] for e in settingsList] + ["Done"]
	colors = [{True:"#006600",False:"#800000"}[getSetting(e["setting"],True)] for e in settingsList] + ["#000000"]
	choice = askChoice("Click to toggle any game setting",choices,colors)
	if choice not in [0,len(choices)]:
		setSetting(settingsList[choice-1]["setting"],not getSetting(settingsList[choice-1]["setting"],True))
		optionsMenu(group)

#This function lets the player set a timer
def setTimer(group,x,y):
		timerIsRunning = eval(getGlobalVariable("TimerIsRunning"))
		if timerIsRunning:
				whisper("You cannot start a new timer until the current one finishes!")
				return
		setGlobalVariable("TimerIsRunning",str(True))
		timerDefault = getSetting('timerDefault',300)
		choices = ["15 seconds","30 seconds","60 seconds","180 seconds","{} seconds".format(str(timerDefault)),"Other"]
		colors = ["#006600" for c in choices][:-1] + ['#003366']
		choice = askChoice("Set timer for how long?",choices,colors)
		if choice == 0: return
		seconds = {1:15,2:30,3:60,4:180,5:timerDefault}.get(choice,0)
		if choice == 6:
				seconds = askInteger("Set timer for how many seconds?",timerDefault)
				setSetting('timerDefault',seconds)
		notify("{} sets a timer for {} minutes,{} seconds.".format(me,seconds/60,seconds%60))
		playSoundFX('Notification')
		time.sleep(0.2)
		playSoundFX('Notification')
		notifications = range(11) + [30] + [x*60 for x in range(seconds/60+1)][1:]
		endTime = time.time() + seconds
		notifications = [endTime - t for t in notifications if t < seconds]
		updateTimer(endTime,notifications)

#This function checks the timer,and then remotecalls itself if the timer has not finished
def updateTimer(endTime,notifications):
		mute()
		currentTime = time.time()
		if currentTime>notifications[-1]:
				timeLeft = int(endTime - notifications[-1])
				playSoundFX('Notification')
				if timeLeft > 60: notify("{} minutes left!".format(timeLeft/60))
				else: notify("{} seconds left!".format(timeLeft))
				notifications.remove(notifications[-1])
		if notifications: remoteCall(me,"updateTimer",[endTime,notifications])
		else:
				playSoundFX('Alarm')
				notify("Time's up!")
				setGlobalVariable("TimerIsRunning",str(False))

def playerDone(group,x=0,y=0):
	notify("{} is done".format(me.name))

def genericAttack(group,x=0,y=0):
	target = [cards for cards in table if cards.targetedBy==me]
	defender = (target[0] if len(target) == 1 else None)
	dice = diceRollMenu(None,defender).get('Dice',-1)
	if dice >=0: rollDice(dice)

def flipCoin(group,x = 0,y = 0): #do we still need this ACG? from before my time......we can get rid of it and the menu item.....
	mute()
	n = rnd(1,2)
	if n == 1:
		notify("{} flips heads.".format(me))
	else:
		notify("{} flips tails.".format(me))

def createVineMarker(group,x=0,y=0):
	mute()
	table.create("ed8ec185-6cb2-424f-a46e-7fd7be2bc1e0",x,y)
	notify("{} creates a Green Vine Marker.".format(me))

def createCompassRose(group,x=0,y=0):
	table.create("7ff8ed79-159c-46e5-9e87-649b3269a931",x,y)

def createAltBoardCard(group,x=0,y=0):
	table.create("af14ca09-a83d-4185-afa0-bc38a31dbf82",0,0)
	
def toggleDebug(group,x=0,y=0):
	global debugMode
	debugMode = not debugMode
	if debugMode:
		notify("{} turns on debug".format(me))
	else:
		notify("{} turns off debug".format(me))

def nextPhase(group,x=0,y=0):
	mute()
	gameMode = getGlobalVariable("GameMode")
	if gameMode == "Arena" or "Domination": nextPhaseArena()
	elif gameMode == "Academy": nextPhaseAcademy()

############################################################################
######################		Chat Actions			################################
############################################################################
def sayYes(group,x=0,y=0):
	notify("{} says Yes".format(me.name))

def sayNo(group,x=0,y=0):
	notify("{} says No".format(me.name))

def sayPass(group,x=0,y=0):
	notify("{} says Pass".format(me.name))

def sayThinking(group,x=0,y=0):
	notify("{} says I am thinking....".format(me.name))

def askThinking(group,x=0,y=0):
	notify("{} asks are you thinking?".format(me.name))

def askYourTurn(group,x=0,y=0):
	notify("{} asks is it your turn?".format(me.name))

def askMyTurn(group,x=0,y=0):
	notify("{} asks is it my turn?".format(me.name))

def askRevealEnchant(group,x=0,y=0):
	notify("{} asks do you wish to Reveal your Enchantment?".format(me.name))
	
def createCard(group,x=0,y=0):
		mute()
		global debugMode
		cardName = askString("Create which card?","Enter card name here")
		guid,quantity = askCard({'Name':cardName},title="Select card version and quantity")
		if guid and quantity:
				cards = ([table.create(guid,0,0,1,True)] if quantity == 1 else table.create(guid,0,0,quantity,True))
				for card in cards:
						card.moveTo(me.hand)
						if not debugMode:
							notify("*** ILLEGAL *** - Spellbook is no longer valid")
						notify("A card was created and was placed into {}'s spellbook.".format(me))

#Card Actions
##########################     Add/Subtract Tokens     ##############################

tokenList=['Armor',
		   'Banish',
		   'Bleed',
		   'Burn',
		   'Cripple',
		   'Corrode',
		   'Disable',
		   'Daze',
		   'Growth',
		   'Mana',
		   'Melee',
		   'Rage',
		   'Ranged',
		   'Rot',
		   'Slam',
		   'Stun',
		   'Stuck',
		   'Sleep',
		   'Tainted',
		   'Veteran',
		   'Weak',
		   'Wrath',
		   'Zombie'
		   ]

for token in tokenList:
		exec('def add'+token+'(card,x = 0,y = 0):\n\taddToken(card,'+token+')')
		exec('def sub'+token+'(card,x = 0,y = 0):\n\tsubToken(card,'+token+')')

def addControlMarker(card,x = 0,y = 0):
	mute()
	placeControlMarker(me,card)

def placeControlMarker(attacker,defender):
	mute()
	#First,If orb is off,turn it on
	if defender.alternate == "":
		defender.alternate = "B"
		notify("{} flips V'Tar Orb On.".format(me))
	#Second,check to see if there is a control marker on the Orb already and if so remove it
	markerColor = playerColorDict[int(attacker.getGlobalVariable("MyColor"))]["ControlMarker"]
	if defender.markers[markerColor] == 1:
		notify("{} already has control of the V'tar Orb!".format(attacker.name))
		return
	elif sum([defender.markers[m] for m in listControlMarkers]) > 0:
		for m in listControlMarkers:
			defender.markers[m] = max(defender.markers[m]-1,0)
		notify("{} neutralizes the V'tar Orb!".format(attacker.name))
	else:
		defender.markers[markerColor] = 1
		notify("{} asserts control over the V'tar Orb!\nIndicating control using a {}.".format(attacker.name,markerColor[0]))

def addDamage(card,x = 0,y = 0):
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if "Mage" in card.Subtype and card.controller == me:
		me.Damage += 1
	else:
		addToken(card,Damage)

def addOther(card,x = 0,y = 0):
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	marker,qty = askMarker()
	if qty == 0:
		return
	card.markers[marker] += qty

def subDamage(card,x = 0,y = 0):
	if card.Subtype == "Mage" and card.controller == me:
			me.Damage -= 1
	else:
		subToken(card,Damage)

def clearTokens(card,x = 0,y = 0):
	mute()
	for tokenType in card.markers:
		card.markers[tokenType] = 0
	notify("{} removes all tokens from {}".format(me,card.Name))

##########################     Toggle Actions/Tokens     ##############################


def toggleAction(card,x=0,y=0):
	mute()
	myColor = int(me.getGlobalVariable("MyColor"))
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if myColor == "0":
		whisper("Please perform player setup to initialize player color")
	elif myColor == 1: # Red
		if card.markers[ActionRedUsed] > 0:
			card.markers[ActionRed] = 1
			card.markers[ActionRedUsed] = 0
			notify("{} readies Action Marker".format(card.Name))
		else:
			card.markers[ActionRed] = 0
			card.markers[ActionRedUsed] = 1
			notify("{} spends Action Marker".format(card.Name))
	elif myColor == 2: # Blue
		if card.markers[ActionBlueUsed] > 0:
			card.markers[ActionBlue] = 1
			card.markers[ActionBlueUsed] = 0
			notify("{} readies Action Marker".format(card.Name))
		else:
			card.markers[ActionBlue] = 0
			card.markers[ActionBlueUsed] = 1
			notify("{} spends Action Marker".format(card.Name))
	elif myColor == 3: #Green
		if card.markers[ActionGreenUsed] > 0:
			card.markers[ActionGreen] = 1
			card.markers[ActionGreenUsed] = 0
			notify("{} readies Action Marker".format(card.Name))
		else:
			card.markers[ActionGreen] = 0
			card.markers[ActionGreenUsed] = 1
			notify("{} spends Action Marker".format(card.Name))
	elif myColor == 4: #Yellow
		if card.markers[ActionYellowUsed] > 0:
			card.markers[ActionYellow] = 1
			card.markers[ActionYellowUsed] = 0
			notify("{} readies Action Marker".format(card.Name))
		else:
			card.markers[ActionYellow] = 0
			card.markers[ActionYellowUsed] = 1
			notify("{} spends Action Marker".format(card.Name))
	elif myColor == 5: #Purple
		if card.markers[ActionPurpleUsed] > 0:
			card.markers[ActionPurple] = 1
			card.markers[ActionPurpleUsed] = 0
			notify("{} readies Action Marker".format(card.Name))
		else:
			card.markers[ActionPurple] = 0
			card.markers[ActionPurpleUsed] = 1
			notify("{} spends Action Marker".format(card.Name))
	elif myColor == 6: #Grey
		if card.markers[ActionGreyUsed] > 0:
			card.markers[ActionGrey] = 1
			card.markers[ActionGreyUsed] = 0
			notify("{} readies Action Marker".format(card.Name))
		else:
			card.markers[ActionGrey] = 0
			card.markers[ActionGreyUsed] = 1
			notify("{} spends Action Marker".format(card.Name))

def toggleDeflect(card,x=0,y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[DeflectR] > 0:
		card.markers[DeflectR] = 0
		card.markers[DeflectU] = 1
		notify("{} uses deflect".format(card.Name))
	else:
		card.markers[DeflectR] = 1
		card.markers[DeflectU] = 0
		notify("{} readies deflect".format(card.Name))

def toggleGatetoHell(card,x=0,y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[GateClosed] > 0:
		card.markers[GateClosed] = 0
		card.markers[GateOpened] = 1
		notify("The Gate to Hell has been Opened!")
	else:
		card.markers[GateClosed] = 1
		card.markers[GateOpened] = 0
		notify("The Gate to Hell has been Closed!")

def toggleGuard(card,x=0,y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	toggleToken(card,Guard)

def toggleInvisible(card,x=0,y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[Invisible] > 0:
		card.markers[Invisible] = 0
		card.markers[Visible] = 1
		notify("{} becomes visible".format(card.Name))
	else:
		card.markers[Invisible] = 1
		card.markers[Visible] = 0
		notify("{} becomes invisible".format(card.Name))

def toggleReady(card,x=0,y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[Ready] > 0:
		card.markers[Ready] = 0
		card.markers[Used] = 1
		notify("{} spends the Ready Marker on {}".format(me,card.Name))
	else:
		card.markers[Ready] = 1
		card.markers[Used] = 0
		notify("{} readies the Ready Marker on {}".format(me,card.Name))

def toggleReadyII(card,x=0,y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[ReadyII] > 0:
		card.markers[ReadyII] = 0
		card.markers[UsedII] = 1
		notify("{} spends the Ready Marker II on {}".format(me,card.Name))
	else:
		card.markers[ReadyII] = 1
		card.markers[UsedII] = 0
		notify("{} readies the Ready Marker II on {}".format(me,card.Name))

def toggleQuick(card,x=0,y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[Quick] > 0:
		card.markers[Quick] = 0
		card.markers[QuickBack] = 1
		notify("{} spends Quickcast action".format(card.Name))
	else:
		card.markers[Quick] = 1
		card.markers[QuickBack] = 0
		notify("{} readies Quickcast Marker".format(card.Name))

def toggleVoltaric(card,x=0,y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[VoltaricON] > 0:
		card.markers[VoltaricON] = 0
		card.markers[VoltaricOFF] = 1
		notify("{} disables Voltaric shield".format(card.Name))
	else:
		choice = askChoice('Do you want to enable your Voltaric Shield by paying 2 mana?'['Yes','No'],["#171e78","#de2827"])
		if choice == 1:
			if me.Mana < 2:
				notify("{} has insufficient mana in pool".format(me))
				return
			me.Mana -= 2
			card.markers[VoltaricON] = 1
			card.markers[VoltaricOFF] = 0
			notify("{}  spends two mana to enable his Voltaric shield".format(me))
		else: notify("{} chose not to enable his Voltaric shield".format(me))

############################################################################
######################		Other Actions		################################
############################################################################


def rotateCard(card,x = 0,y = 0):
	# Rot90,Rot180,etc. are just aliases for the numbers 0-3
	mute()
	if card.controller == me:
		card.orientation = (card.orientation + 1) % 4
		if card.isFaceUp:
			notify("{} Rotates {}".format(me,card.Name))
		else:
			notify("{} Rotates a card".format(me))

def flipcard(card,x = 0,y = 0):
	mute()
	tutorialMessage("Advance Phase")
	cardalt = card.alternates
	cZone = getZoneContaining(card)
	# markers that are cards in game that have two sides
	if "Vine Marker" in card.Name and card.controller == me:
		if card.alternate == "":
			card.alternate = "B"
			notify("{} flips the Vine Marker to use its Black side.".format(me))
		else:
			card.alternate = ""
			notify("{} flips the Vine Marker to use its Green side.".format(me))
		return
	elif "Alt Zone" in card.Name and card.controller == me:
		if card.alternate == "B":
			card.alternate = ""
		else:
			card.alternate = "B"
		notify("{} flips Zone Marker.".format(me))
		return
	elif "V'Tar Orb" in card.Name and card.controller == me:
		if card.alternate == "B":
			card.alternate = ""
			notify("{} flips V'Tar Orb Off".format(me))
		else:
			card.alternate ="B"
			notify("{} flips V'Tar Orb On.".format(me))
		return
	elif "Player Token" in card.Name:
		nextPlayer = getNextPlayerNum()
		debug(nextPlayer)
		setGlobalVariable("PlayerWithIni",str(nextPlayer))
		for p in players:
			remoteCall(p,"changeIniColor",[card])

	# do not place markers/tokens on table objects like Initative,Phase,and Vine Markers
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList: return
	# normal card flipping processing starts here
	if card.isFaceUp == False:
		card.isFaceUp = True
		if card.Type != "Enchantment"  and "Conjuration" not in card.Type: #leaves the highlight around Enchantments and Conjurations
			card.highlight = None
		if card.Type == "Creature": #places action marker on card
			toggleAction(card)
		if card.Subtype == "Mage": #once more to flip action to active side
			toggleAction(card)
			toggleQuick(card)
			if "Wizard" in card.Name:
					card.markers[VoltaricOFF] = 1
			if "Forcemaster" == card.Name:
					card.markers[DeflectR] = 1
			if "Beastmaster" == card.Name:
					card.markers[Pet] = 1
			if "Johktari Beastmaster" == card.Name:
					card.markers[WoundedPrey] = 1
			if "Priest" == card.Name:
					card.markers[HolyAvenger] = 1
			if "Druid" == card.Name:
					card.markers[Treebond] = 1
			if "Necromancer" == card.Name:
					card.markers[EternalServant] = 1
			if "Warlock" == card.Name:
					card.markers[BloodReaper] = 1
		if "Anvil Throne Warlord Stats" == card.Name:
					card.markers[RuneofFortification] = 1
					card.markers[RuneofPower] = 1
					card.markers[RuneofPrecision] = 1
					card.markers[RuneofReforging] = 1
					card.markers[RuneofShielding] = 1
		if card.Name in typeChannelingList and card.controller == me and card.isFaceUp == True:
			notify("{} increases the Channeling stat by 1 as a result of {} being revealed".format(me,card))
			me.Channeling += 1
		if "Harmonize" == card.Name and card.controller == me and isAttached(card) and card.isFaceUp == True:
			magecard = getAttachTarget(card)
			if magecard.Subtype == "Mage":
				notify("{} increases the Channeling stat by 1 as a result of {} being revealed".format(me,card))
				me.Channeling += 1
		if card.Type == "Creature":
			if "Invisible Stalker" == card.Name:
					card.markers[Invisible] = 1
			if "Thorg,Chief Bodyguard" == card.Name:
					card.markers[TauntT] = 1
			if "Sosruko,Ferret Companion" == card.Name:
					card.markers[Taunt] = 1
			if "Skeelax,Taunting Imp" == card.Name:
					card.markers[TauntS] = 1
			if "Ichthellid" == card.Name:
					card.markers[EggToken] = 1
			if "Talos" == card.Name:
					toggleAction(card)
			if "Orb Guardian" in card.name and card.special == "Scenario" and [1 for c in getCardsInZone(myZone) if "V'Tar Orb" in c.name]:
					card.markers[Guard] = 1
		if card.Type == "Conjuration":
			if "Ballista" == card.Name:
				card.markers[LoadToken] = 1
			if "Akiro's Hammer" == card.Name:
				card.markers[LoadToken] = 1
			if "Corrosive Orchid" == card.Name:
				card.markers[MistToken] = 1
			if "Nightshade Lotus" == card.Name:
				card.markers[MistToken] = 1
			if "Rolling Fog" == card.Name:
				card.markers[DissipateToken] = 3
			if "Gate to Hell" == card.Name:
				card.markers[GateClosed] = 1
		if "Defense" in card.Stats and not card.Name=="Forcemaster":
			if "1x" in card.Stats:
				card.markers[Ready] = 1
			if "2x" in card.Stats:
				card.markers[Ready] = 1
				card.markers[ReadyII] = 1
		if "Forcefield" == card.Name:
			card.markers[FFToken] = 3
		if "[ReadyMarker]" in card.Text:
			card.markers[Ready] = 1
	elif card.isFaceUp and not "B" in cardalt:
		notify("{} turns {} face down.".format(me,card.Name))
		card.isFaceUp = False
		card.peek()
	elif card.isFaceUp and "B" or "C" in cardalt:
		if card.alternate == "":
			notify("{} flips {} to the alternate version of the card.".format(me,card))
			card.alternate = "B"
		elif card.alternate == "B" and "C" in cardalt:
			notify("{} flips {} to the alternate version of the card.".format(me,card))
			card.alternate = "C"
		else:
			notify("{} flips {} to the standard version of the card.".format(me,card))
			card.alternate = ""

def discard(card,x=0,y=0):
	mute()
	#[formatCardObject(c) for c in table if c.Type == "Creature"]
	#[c.onDiscard(card) for c in table if c.Type == "Creature"] #Testing the new discard method
	if card.controller != me:
		whisper("{} does not control {} - discard cancelled".format(me,card))
		return
	if card.Name in typeChannelingList and card.controller == me and card.isFaceUp == True:
			notify("{} decreases the Channeling stat by 1 because {} is being discarded".format(me,card))
			me.Channeling -= 1
	elif "Harmonize" == card.Name and card.controller == me:
		discardedCard = getAttachTarget(card)
		if card.Subtype == "Mage":
			notify("{} decreases the Channeling stat by 1 as a result of {} being discarded".format(me,card))
			me.Channeling -= 1
	elif card.special == "Scenario":
		obliterate(card)
		return
	card.isFaceUp = True
	detach(card)
	card.moveTo(me.piles['Discard'])
	notify("{} discards {}".format(me,card))

def obliterate(card,x=0,y=0):
	mute()
	if card.controller != me:
		whisper("{} does not control {} - card obliteration cancelled".format(me,card))
		return
	if card.Name in typeChannelingList and card.controller == me and card.isFaceUp == True:
			notify("{} decreases the Channeling stat by 1 because {} has been obliterated".format(me,card))
			me.Channeling -= 1
	elif "Harmonize" == card.Name and card.controller == me:
		discardedCard = getAttachTarget(card)
		if card.Subtype == "Mage":
			notify("{} decreases the Channeling stat by 1 because {} has been obliterated".format(me,card))
			me.Channeling -= 1
	else:
			notify("{} obliterates {}".format(me,card))
	card.isFaceUp = True
	detach(card)
	card.moveTo(me.piles['Obliterate Pile'])

def defaultAction(card,x=0,y=0):
	mute()
	if card.controller == me:
		if not card.isFaceUp:
			#is this a face-down enchantment? if so,prompt before revealing
			payForAttack = not (getSetting('BattleCalculator',True) and card.Type=='Attack')
			if card.Subtype == "Mage" or not payForAttack or card.Type == "Magestats": #Attack spells will now be paid for through the battlecalculator
				flipcard(card,x,y)

				if not getSetting('attackChangeNotified',False) and not payForAttack:
					whisper('Note: Mana for {} will be paid when you declare an attack using the Battle Calculator,or if you double-click on {} again.'.format(card,card))
					setSetting('attackChangeNotified',True)
			elif card.Type == "Enchantment": revealEnchantment(card)
			else: castSpell(card)

		else:
			if card.Type == "Incantation" or card.Type == "Attack": castSpell(card) #They can cancel in the castSpell prompt; no need to add another menu

############################################################################
######################		Utility Functions		########################
############################################################################

def addToken(card,tokenType):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList: return  # do not place markers/tokens on table objects like Initative,Phase,and Vine Markers
	card.markers[tokenType] += 1
	if card.isFaceUp:
		notify("{} added to {}".format(tokenType[0],card.Name))
	else:
		notify("{} added to face-down card.".format(tokenType[0]))

def subToken(card,tokenType):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList: return  # do not place markers/tokens on table objects like Initative,Phase,and Vine Markers
	if card.markers[tokenType] > 0:
		card.markers[tokenType] -= 1
		if card.isFaceUp:
			notify("{} removed from {}".format(tokenType[0],card.Name))
		else:
			notify("{} removed from face-down card.".format(tokenType[0]))

def toggleToken(card,tokenType):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList: return  # do not place markers/tokens on table objects like Initative,Phase,and Vine Markers
	if card.markers[tokenType] > 0:
		card.markers[tokenType] = 0
		if card.isFaceUp:
			notify("{} removes a {} from {}".format(me,tokenType[0],card.Name))
		else:
			notify("{} removed from face-down card.".format(tokenType[0]))
	else:
		card.markers[tokenType] = 1
		if card.isFaceUp:
			notify("{} adds a {} token to {}".format(me,tokenType[0],card.Name))
		else:
			notify("{} added to face-down card.".format(tokenType[0]))

def playCardFaceDown(card,x=0,y=0):
	mute()
	tutorialMessage("Reveal Card")
	myHexColor = playerColorDict[eval(me.getGlobalVariable("MyColor"))]['Hex']
	card.isFaceUp = False
	moveCardToDefaultLocation(card)
	card.peek()
	card.highlight = myHexColor
	notify("{} prepares a Spell from their Spellbook by placing a card face down on the table.".format(me))
