############################################################################
##########################    v1.11.0.0    ##################################
############################################################################
############################
# Card Attachment and Alignment
############################

"""
This module contains the bulk of the attachment code.
Features:
- The attachments of each card are preserved in the order in which they were attached to that card.
- Removing a card from the table detaches everything that was attached to it.
- Two methods of attaching a card; explicitly, using targeting and alt+q, and by simply dragging one
card over the other (if autoAttach is enabled), using the moveToCard method in actions.py
- Detaching a card is as easy as dragging it away from the card to which it was attached

Bugs/Missing Features:
- Mass selecting a stack of cards and dragging it causes the cards to unattach and semi-randomly attach
to each other
- Right now, the criteria for what may be attached to what are pretty loose. It will be easy to add
restrictions, however.
"""

def menuDetachAction(card,x=0,y=0):
    """This detaches <card> and returns it to its home location"""
    mute()
    if isAttached(card):
        detach(card)
        returnCardToHome(card)

def attachToTarget(card,x=0,y=0):
    """This command is used to explicitly attach one card to the card currently being targeted."""
    mute()
    if isAttachCardsEnabled() == "True":
        if card.controller == me:
            target = [cards for cards in table if cards.targetedBy==me]
            if len(target) == 0 or (len(target) == 1 and card in target):
                c,t = detach(card)
                if t:
                    notify("{} detaches {} from {}.".format(me,c,t))
            elif len(target) == 1:
                c,t = attach(card, target[0])
                if t:
                    notify("{} attaches {} to {}.".format(me,c,t))
            else:
                whisper("Incorrect targets, select up to 1 target.")
                return
    else:
        whisper("AttachCards must be enabled to use this feature")
    return

def attach(card,target):
    """Controller of <card> may attach it to <target>."""
    mute()
    if card.controller == me and canAttach(card,target):
        if card.type == 'Enchantment' and not card.isFaceUp: enchantmentAttachCost(card,target) #Ask if controller would like to pay mana to attach it
        detachAll(card)
        consolidateAttachments(target)
        setGlobalDictEntry("attachDict",card._id,[target._id,len(getAttachments(target))+1])
        remoteCall(target.controller,'alignAttachments',[target])
        return card,target
    return card,None

def enchantmentAttachCost(card,target): #Target useful for when things like Harshforge Plate are integrated into this.
    discountStr = ''
    discount = 0
    foundDiscounts = []
    infostr = 'Enchantments cost 2 mana to cast.'
    notifyStr = "{} attaches a hidden enchantment on {}, with a base cost of 2 mana.".format(me, target.name)
    for c in table:
        if c.controller == me and c.isFaceUp and "[Casting Discount]" in c.Text and c != card:
            dc = findDiscount(card, c)
            debug("Discount Count Returned from test: {} from card: {}".format(dc, c.Name))
            if dc > 0:
                discountStr = "\nCost reduced by {} due to {}".format(dc, c.name)
                infostr = notifyStr + discountStr
                notifyStr = notifyStr + discountStr
                discount += dc
                foundDiscounts.append(c)
            elif dc < 0:
                discountStr = "\n{} already reached max uses this round.".format(c.name)
                infostr = notifyStr + discountStr
                notifyStr = notifyStr + discountStr
    choice = askChoice('Do you want to cast {} face-down on {}?'.format(card.name,target.name),['Yes, I am casting this as a spell','No, I want to attach it for other reasons'],["#171e78","#de2827"])
    if choice == 1:
        infostr += "\nTotal mana amount to subtract from mana pool?"
	manacost = askInteger(infostr, 2 - discount)
	if manacost == None: return # player closed the window and didn't cast the spell
        elif me.Mana < manacost:
                notify("{} has insufficient mana in pool".format(me))
                return
        for dc in foundDiscounts:
	    doDiscount(dc)
	me.Mana -= manacost 
        notify(notifyStr)
                
def detach(card):
    """Removes <card> from its target, then consolidates remaining cards on target."""
    mute()
    if isAttached(card) and card.controller == me:
        target = getGlobalDictEntry('attachDict',card._id)
        setGlobalDictEntry('attachDict',card._id,None)
        if target:
            target = Card(target[0])
            consolidateAttachments(target)
            remoteCall(target.controller,'alignAttachments',[target])
        return card,target
    return card,None

def alignAttachments(card):
    """Orders <card> and its attachments"""
    mute()
    if card.controller == me:
        attachments = getAttachments(card)
        prevCards  = [card]
        count = 1
        x,y = card.position
        alignQueue = {}
        side = (-1 if table.isInverted(y) else 1)
        for c in attachments:
            Y = y-(count*side)*12
            #Please align your own cards first...
            if c.controller == me:
                c.moveToTable(x,Y)
                for p in reversed(prevCards):
                    if p.controller == me:
                        c.setIndex(p.getIndex)
                        break
            #...before assisting other players
            else:
                controller = c.controller
                if controller not in alignQueue: alignQueue[controller] = []
                alignQueue[controller].append({'cardId' : c._id, 'X' : x, 'Y' : Y, 'prevCardIds' : [i._id for i in prevCards]})
            count += 1
            prevCards.append(c)
        #Remotely trigger alignment in other players
        alignedPlayers = [me]
        for p in alignQueue:
            if p in getPlayers():
                alignedPlayers.append(p)
                rnd(1,10) #avoids desync issues
                remoteCall(p,'remoteAlign',[alignQueue[p],alignedPlayers])

def remoteAlign(alignData,alignedPlayers):
    mute()
    for d in alignData:
        card,X,Y,prevCards = Card(d['cardId']),d['X'],d['Y'],[Card(i) for i in d['prevCardIds']]
        card.moveToTable(X,Y)
        for c in reversed(prevCards):
            if c.controller in alignedPlayers:
                card.setIndex(c.getIndex)
                break

def detachAll(card):
    """Removes all attachments from <card> and places them in front of their owners"""
    mute()
    attachments = getAttachments(card)
    for c in attachments:
        if c.controller == me:
            detach(c)
            returnCardToHome(c)
        else:
            remoteCall(c.controller,'detach',[c])
            remoteCall(c.controller,'returnCardToHome',[c])
        rnd(0,0)

def returnCardToHome(card):
    """This function returns a card to above the home position of its controller."""
    mute()
    global playerNum
    x,y = {
            1 : (-595, -240),
            2 : (460, 120),
            3 : (-595, 120),
            4 : (460, -240),
            5 : (-595, -40),
            6 : (460, -40)}[playerNum]
    card.moveToTable(x,y-card.height())
    
def isAttached(card):
    """Determines whether <card> is attached to anything."""
    mute()
    if getGlobalDictEntry('attachDict',card._id) and card in table:
        return True
    return False

def consolidateAttachments(card):
    return
    """Reorders attachments on target card to eliminate gaps between indices"""
    mute()
    aDict = eval(getGlobalVariable("attachDict"))
    attachments=getAttachments(card)
    count = 1
    for c in attachments:
        aDict[c._id] = [card,count]
        count +=1
    setGlobalVariable("attachDict",str(aDict))

def getAttachments(card):
    """Returns a list of cards that are attached to <card>, sorted by their attachment order"""
    mute()
    aDict = eval(getGlobalVariable("attachDict"))
    attachList = [key for key in aDict if aDict[key] and int(aDict[key][0]) == card._id]
    attachList.sort(key=lambda k: aDict[k][1])
    return [Card(key) for key in attachList if Card(key) in table]

def getAttachTarget(card):
    mute()
    result = getGlobalDictEntry('attachDict',card._id)
    if result and card in table: return Card(result[0])

def getGlobalDictEntry(dictionary,key):
    """Dictionary is input as a string. If the value is empty, returns False"""
    mute()
    gDict = eval(getGlobalVariable(dictionary))
    if key in gDict:
        return gDict[key]
    return None

def setGlobalDictEntry(dictionary,key,value):
    """Note that dictionary is input as a string"""
    mute()
    gDict = eval(getGlobalVariable(dictionary))
    gDict[key] = value
    setGlobalVariable(dictionary,str(gDict))

def canAttach(card,target):
    """Determines whether <card> may be attached to <target>"""
    if (isAttached(target)
        or getAttachments(card)
        or card==target
        or not target in table
        or not card in table
        or not target.isFaceUp):
        return False
    if (card.Type == 'Enchantment'
        or (card.Type == 'Equipment' and target.Type == 'Mage')
        or target.Type == 'Magestats'
        or (card.Name in ['Tanglevine','Stranglevine','Quicksand'] and target.Type == 'Creature')
#Familiars
        or (target.name == 'Goblin Builder' and 'Conjuration' in card.Type and card.Name not in['Tanglevine','Stranglevine','Quicksand'])
        or (target.name == 'Thoughtspore' and card.Type in ['Attack','Incantation'] and sum([int(i) for i in card.level.split('+')])<=2)
        #or sectarus, but enchants are already legal to attach to everything
        or (target.name == 'Wizard\'s Tower' and card.Type == 'Attack' and 'Epic' not in card.Traits and card.Action == 'Quick')
        or (target.name == 'Sersiryx, Imp Familiar' and card.Type == 'Attack' and 'Fire' in card.School and sum([int(i) for i in card.level.split('+')])<=2) #Again, enchantments are automatically legal
        #fellella is covered
        or (target.name == 'Huginn, Raven Familiar' and card.Type == 'Incantation' and sum([int(i) for i in card.level.split('+')])<=2)
        or (target.name == 'Gurmash, Orc Sergeant' and 'Command' in card.Subtype)
#Spawnpoints
        or (target.name == 'Barracks' and card.Type == 'Creature' and 'Soldier' in card.Subtype)
        or (target.name == 'Battle Forge' and card.Type == 'Equipment')
        or (target.name == 'Gate to Voltari' and card.Type == 'Creature' and 'Arcane' in card.School)
        or (target.name == 'Lair' and card.Type == 'Creature' and 'Animal' in card.School)
        or (target.name == 'Pentagram' and card.Type == 'Creature' and 'Dark' in card.School and not ('Nonliving' in card.Traits or 'Incorporeal' in card.Traits))
        or (target.name == 'Temple of Asyra' and card.Type == 'Creature' and 'Holy' in card.School)
        or (target.name == 'Graveyard' and card.Type == 'Creature' and 'Dark' in card.School and ('Nonliving' in card.Traits or 'Incorporeal' in card.Traits))
        or (target.name == 'Seedling Pod' and card.Type in ['Creature','Conjuration','Conjuration-Wall'] and 'Plant' in card.Sybtype)
        or (target.name == 'Samara Tree' and card.name == 'Seedling Pod')
        or (target.name == 'Vine Tree' and card.Type in ['Creature','Conjuration','Conjuration-Wall'] and 'Vine' in card.Sybtype)
        or (target.name == 'Libro Mortuos' and card.Type == 'Creature' and 'Undead' in card.Subtype)
#Spellbind (only)
        or (target.name == 'Helm of Command' and card.Type == 'Incantation' and 'Epic' not in card.Traits and 'Command' in card.Subtype)
        or (target.name == 'Elemental Wand' and card.Type == 'Attack' and 'Epic' not in card.Traits)
        or (target.name == 'Mage Wand' and card.Type == 'Incantation' and 'Epic' not in card.Traits)):
        return True
    return False

def isAttachCardsEnabled():
    """Checks whether the attachCards module is turned on."""
    return getSetting("attachCards", "True")