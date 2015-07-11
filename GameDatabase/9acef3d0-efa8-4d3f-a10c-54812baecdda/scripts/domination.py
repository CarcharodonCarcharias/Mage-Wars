###########################################################################
##########################    v1.12.5.0     #######################################
###########################################################################

############################################################################
############################	   Map Construction      ################################
############################################################################

def checkDominationVictory():
        goal = eval(getGlobalVariable("Goal")).get("Goal")
        debug(str(goal))
        victoriousPlayers = []
        for player in players:
                mage = [c for c in table if c.type=="Mage" and c.controller == player][0]
                vtar = mage.markers[VTar] + 3*mage.markers[VTar3] + 5*mage.markers[VTar5]
                if vtar >= goal: victoriousPlayers.append([player,vtar])
        soleWinner = None
        for player in victoriousPlayers:
                for other in list(victoriousPlayers):
                        if other[1] >= player[1] and other!=player: break
                        soleWinner = player
        if soleWinner:
                notify("{} wins with {} V'tar!".format(soleWinner[0],soleWinner[1]))
                return True

def DominationTracker():
        mute()
        #need dynamic proxy card generation for this to work....
        card = table.create("a25a6dd5-04a8-490f-b5e6-834ffac8d018",-591,-5)
        card.Special1 = str(eval(getGlobalVariable("Map")).get("Map Name"))
        card.Special2 = str(eval(getGlobalVariable("Goal")).get("Goal"))

def importArray(filename):
        """Takes a txt character array and outputs a dictionary of arrays (sets of columns). To get an entry from an array, use array[x][y]"""
        #Open the file
        directory = os.path.split(os.path.dirname(__file__))[0]+'\{}'.format('maps')
        try: raw = open('{}\{}{}'.format(directory,filename,'.txt'),'r')
        except: return #Bad practice, I know. I'll try to find a better way later.
        #Create an empty array.
        #Because of the order in which data are read, we will need to transpose it.
        transposeArray = []
        #Fill up the transposed array, as a set of rows.
        scenarioDict = {}
        dictKey = None
        for line in raw:
                if line == '\n': pass #ignore blank lines
                elif "@Scenario" in line:
                        raw = line.replace('\n','').strip('@')
                        split = raw.split("=")[1].strip("[]").split(",")
                        scenarioDict["Scenario"] = {"Type":split[0],"Goal":int(split[1])}
                elif "@" in line:
                        raw = line.replace('\n','').strip('@')
                        split = raw.split("=")
                        key = split[0]
                        locations = eval(split[1])
                        scenarioDict[key] = locations
                elif line[0] != '#':
                        row = []
                        for char in range(len(line.replace('\n',''))):
                            if line[char] != '\n':
                                row.append(line[char])
                        transposeArray.append(row)
                else:
                        dictKey = line.replace('\n','').strip('#')
                        X0 = len(transposeArray[0])
                        X1 = len(transposeArray)
                        array = [[transposeArray[x1][x0] for x1 in range(X1)] for x0 in range(X0)]
                        #transposeArray = []
                        scenarioDict[dictKey] = array
        return scenarioDict

def loadMapFile(group, x=0, y=0):
        mute()
        directory = os.path.split(os.path.dirname(__file__))[0]+'\{}'.format('maps')
        fileList = [f.split('.')[0] for f in os.listdir(directory) if (os.path.isfile(os.path.join(directory,f)) and f.split('.')[1]=='txt')]
        choices = fileList+['Cancel']
        colors = ['#6600CC' for f in fileList] + ['#FF0000']
        choice = askChoice('Load which map?',choices,colors)
        if choice == 0 or choice == len(choices): return
        choiceName = choices[choice-1]
        scenario = importArray(fileList[choice-1])
        notify('{} loads {}.'.format(me,fileList[choice-1]))

        if scenario.get("Scenario"): setGlobalVariable("Goal",str(scenario["Scenario"]))

        mapArray = scenario.get('Map',False)
        mapTileSize = 250 #replace 250 with a stored tilesize from scenario if we later decide to allow the design of maps with non-standard tilesizes.
        mapObjects = [(k,scenario.get(k,[])) for k in mapObjectsDict]
        startZones = scenario.get("startZoneDict",{}) #should probably include a default placement dictionary.

        for c in table:
                if (c.type == "Internal" or "Scenario" in c.special) and c.controller == me:
                        c.delete() # delete Scenario creatures and other game markers
                elif (c.type == "Internal" or "Scenario" in c.special)  and c.controller != me:
                        remoteCall(c.controller,'remoteDeleteCard', [c])

        #iterate over elements, top to bottom then left to right.
        I,J = len(mapArray),len(mapArray[0])
        X,Y = I*mapTileSize,J*mapTileSize
        x,y = (-X/2,-Y/2) #Do we want 0,0 to be the center, or the upper corner? Currently set as center.

        zoneArray = mapArray

        for i in range(I):
                for j in range(J): #Might as well add support for non-rectangular maps now. Though this won't help with the rows.
                        if mapArray:
                                tile = mapTileDict.get(mapArray[i][j],None)
                                SPT = (True if tile == "c3e970f7-1eeb-432b-ac3f-7dbcd4f45492" else False) #Spiked Pit Trap
                                zoneArray[i][j] = (1 if tile else 0)
                                if tile:
                                        tile = table.create(tile,x,y)
                                        tile.anchor = True
                                        if SPT: table.create("8731f61b-2af8-41f7-8474-bb9be0f32926",x+mapTileSize/2 - 28,y+mapTileSize/2 - 40) #Add trap marker
                        y += mapTileSize
                x += mapTileSize
                y = -Y/2
        x = -X/2

        mapDict = createMap(I,J,zoneArray,mapTileSize)

        mapDict["Map Name"] = choiceName
        debug(mapDict.get("Map Name","Unnamed map"))
        for z in startZones:
                playerNumber = z["Player"]
                zx,zy = eval(z["Zone"])
                mapDict['zoneArray'][zy-1][zx-1]['startLocation'] = str(playerNumber)

        setGlobalVariable("Map",str(mapDict))

        for obj,locations in mapObjects:
                for L in locations:
                        j,i = L
                        mapPlace(obj,(i-1,j-1))

        setNoGameBoard(table)

def mapPlace(key,coords):
        mapDict = eval(getGlobalVariable("Map"))
        mapTileSize = mapDict['tileSize']
        i,j = coords
        x,y = i*mapTileSize+mapDict["x"],j*mapTileSize+mapDict["y"]
        GUID=mapObjectsDict[key]["GUID"]
        offset=mapObjectsDict[key]["Offset"]
        multiOffset=mapObjectsDict[key]["Multiple Offset"]
        x += offset
        y += offset
        while True:
                finished = True
                for c in table:
                        cx,cy = c.position
                        if cx==x and cy == y: #and c.Type == "Creature"
                                x += multiOffset
                                finished = False
                                break
                if finished: break

        card = table.create(GUID,x,y)
        if card.type == "Creature":
                card.special = "Scenario"
                if "Orb Guardian" in card.name:
                        toggleGuard(card)
        elif card.type == "Conjuration":
                card.special = "Scenario"

### Map Definitions ###

mapTileDict = {
        "1" : "5fbc16dd-f861-42c2-ad0f-3f8aaf0ccb64", #V'Torrak
        "2" : "6136ff26-d2d9-44d2-b972-1e26214675b5", #Corrosive Pool
        "3" : "8972d2d1-348c-4c4b-8c9d-a1d235fe482e", #Altar of Oblivion
        "4" : "a47fa32e-ac83-4ced-8f6a-23906ee38880", #Septagram
        "5" : "bf833552-8ee4-4c62-abd2-83da233da4ce", #Molten Rock
        "6" : "c3e970f7-1eeb-432b-ac3f-7dbcd4f45492", #Spiked Pit
        "7" : "edca7d45-53e0-468d-83a5-7a446c81f070", #Samandriel's Circle
        "8" : "f8d70e09-2734-4de8-8351-66fa98ae0171", #Ethereal Mist
        "." : "4f1b033d-7923-4e0e-8c3d-b92ae19fbad1"} #Generic Tile

mapObjectsDict = {
        "Orb" : {"GUID":"3d339a9d-8804-4afa-9bd5-1cabb1bebc9f", "Offset":175, "Multiple Offset": -100},
        "Sslak" : {"GUID":"bf217fd3-18c0-4b61-a33a-117167533f3d", "Offset":5, "Multiple Offset": 62},
        "Usslak" : {"GUID":"54e67290-5e6a-4d8a-8bf0-bbb8fddf7ddd", "Offset":5, "Multiple Offset": 62},
        "SecretPassage" : {"GUID":"a4b3bb92-b597-441e-b2eb-d18ef6b8cc77", "Offset":175, "Multiple Offset": -100}
        }
