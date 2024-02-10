
myMsg = [
    "exit_session",
    "disconnecting",
    "name request",
    "kick",#BE CAREFULL!!
    
    ]

valueMsg = {
    "name":("string", 1),#player name
    "hostList":("string", 8),#Alternate player name and id
    "introduce":("string", 1),#yourself. TODO:: add int message support
    "connect":("string",2),#first value is name, second value is index of player. Indicies are not numbers if local to server.
    "alias":("string", 2),#ofical name and id.
    "disconnect":("string", 1),
    "playMap":("string", 1)
    }

    
def msgFilterStandard(message):
    if message in myMsg:
        return True
    else: return False
    
def msgFilterValue(message):
    newStr = ''
    endMess = False
    for char in message:
        if char == "{":
            break
        newStr = newStr + char
        
    ##Above is just a quick filter to remove say, player-IDs from a message.
    if newStr in valueMsg.keys():
        return valueMsg[newStr]
    return False


##################From here on out we define a bunch of functions that are basically getting a specific data type from the iterator
#And then we have dict grabberTable which we can use to assosiate valmessages with the appropriate grabber function
#This is hacky and could probably be implemented in some other memory-nice way but this just makes the code so much cleaner.
def gFloat64(iterator):
    return iterator.getFloat64()
def gBool (iterator):
    return iterator.getBool()
def gString (iterator):#oops funny name
    return iterator.getString()

grabberTable = {
    "float64":gFloat64,
    "bool":gBool,
    "string":gString
    }

####################Ditto of above, except for sending.
def sFloat64(datagram, val):
    return datagram.addFloat64(val)
def sBool (datagram, val):
    return datagram.addBool(val)
def sString (datagram, val):#oops funny name
    return datagram.addString(val)

setterTable = {
    "float64":sFloat64,
    "bool":sBool,
    "string":sString
    }