
myMsg = [
    ]

valueMsg = {
    }

def initialize_msg_lists():#messages left in here after the rework are probably important enough they can stay.
    global myMsg
    global valueMsg

    myMsg = [
    "exit_session",
    #"disconnecting",#This one's not actually used anyomore.
    #"name request",#ditto.
    "kick",#BE CAREFULL!!
    "gameStart",#Used in a hack in entBase.
    "expectOveride",#Hey, we've detected a potential teleport, when we report your position next, go there or else. kept because this could be multi-entity and playerMgr (primary sender) is not a entity
    ]

    valueMsg = {
        #"name":("string", 1),#player name
        "connect":("string",3),#first value is name, second value is index of player. Indicies are not numbers if local to server. Used in multiple places
        "disconnect":("string", 1),#used in multiple places
        "ready":("u8int", 1),
        "changeTeam":("string",2),#This indicates that teams have been updated, not that an individual has changed.
        }
    messenger.send("server: building msg lists")
initialize_msg_lists()

def add_my_msg(name: str):
    if name in myMsg:
        return
    myMsg.append(name)

def add_value_msg(name:str, valueType: str, numTimes: int):
    if name in valueMsg.keys():
        return
    valueMsg[name] = (valueType, numTimes)

    
def msgFilterStandard(message):
    if message in myMsg:
        return True
    elif msgCut(message) in myMsg:
        return True
    else: return False
    
def msgFilterValue(message):
    newStr = msgCut(message)
        
    ##Above is just a quick filter to remove say, player-IDs from a message.
    if newStr in valueMsg.keys():
        return valueMsg[newStr]
    return False

def msgCut(string):#Moved this code out of valueMsg so we can have player-specific valuless messages.
    newStr = ''
    for char in string:
        if char == "{":
            break
        newStr = newStr + char
    return newStr


##################From here on out we define a bunch of functions that are basically getting a specific data type from the iterator
#And then we have dict grabberTable which we can use to assosiate valmessages with the appropriate grabber function
#This is hacky and could probably be implemented in some other memory-nice way but this just makes the code so much cleaner.
def gFloat64(iterator):
    return iterator.get_float64()
def gBool (iterator):
    return iterator.get_bool()
def gString (iterator):#oops funny name
    return iterator.get_string()
def gu8int (iterator):
    return iterator.get_uint8()
def gu32int (iterator):
    return iterator.get_uint32()
def gPlay (iterator):
    #(player._yMove, _xMove, _wantJump, _wantCrouch, _hRot, _pRot, vX,vY,vZ,h,p,x,y,z,is_airborne)
    return (iterator.get_float64(),#y
            iterator.get_float64(),#x
            iterator.get_bool(),#jump
            iterator.get_bool(),#crouch
            iterator.get_float64(),#hrot
            iterator.get_float64(),#prot
            iterator.get_float64(),#vX
            iterator.get_float64(),#vY
            iterator.get_float64(),#vZ
            iterator.get_float64(),#h
            iterator.get_float64(),#p
            iterator.get_float64(),#x
            iterator.get_float64(),#y
            iterator.get_float64(),#z
            iterator.get_bool(),#is_airborne
            iterator.get_bool(),#_isCrouching
            )
def gID (iterator):#This is untested!! please check!!
    #TODO:: give different logic if is host.
    data = iterator.get_datagram()
    return base.server.connections.index(data.get_connection())

grabberTable = {
    "float64":gFloat64,
    "bool":gBool,
    "string":gString,
    "u8int":gu8int,
    "u32int":gu32int,
    "play":gPlay,
    "connectionId":gID
    }

####################Ditto of above, except for sending.
def sFloat64(datagram, val):
    return datagram.add_float64(val)
def sBool (datagram, val):
    return datagram.add_bool(val)
def sString (datagram, val):#oops funny name
    return datagram.add_string(val)
def su8int (datagram, val):
    return datagram.add_uint8(val)
def su32int (datagram, val):
    return datagram.add_uint32(val)
def sPlay (datagram, val):
    datagram.add_float64(val[0]),#y
    datagram.add_float64(val[1]),#x
    datagram.add_bool(val[2]),#jump
    datagram.add_bool(val[3]),#crouch
    datagram.add_float64(val[4]),#hrot
    datagram.add_float64(val[5]),#prot
    datagram.add_float64(val[6]),#vX
    datagram.add_float64(val[7]),#vY
    datagram.add_float64(val[8]),#vZ
    datagram.add_float64(val[9]),#h
    datagram.add_float64(val[10]),#p
    datagram.add_float64(val[11]),#x
    datagram.add_float64(val[12]),#y
    datagram.add_float64(val[13]),#z
    datagram.add_bool(val[14])#is_airborne
    datagram.add_bool(val[15])#_isCrouching
def do_not_set (datagram, val):
    return True
    

setterTable = {
    "float64":sFloat64,
    "bool":sBool,
    "string":sString,
    "u8int":su8int,
    "u32int":su32int,
    "play":sPlay,
    "connectionId":do_not_set
    }