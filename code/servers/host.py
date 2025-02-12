from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader, ConnectionWriter
from panda3d.core import PointerToConnection, NetAddress, NetDatagram
from panda3d.core import NetDatagram, DatagramIterator
from direct.task import Task
from .commonMsg import msgFilterStandard, msgFilterValue, grabberTable, setterTable


class hostServer():
    def __init__(self):
        #Define class variables needed elsewhere
        self.availableSlots = []#List of indecies of disconnected players. instead of immediately deleting dissconected players and shifting references, keep the slots full until a new player connects.
        self.connections = []
        self.addresses= []
        rendezvous = 20560
        backlog = 100
        #Outgoing message-related variables
        self.outBox = []#List of all events that need to be sent to the clients
        self.valBox = []#List of message values where nessicary
        
        
        #create connection host
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        
        self.tcpSocket = self.cManager.open_TCP_server_rendezvous(rendezvous,backlog)
        self.cListener.add_connection(self.tcpSocket)
        #TASKS
        taskMgr.add(self.listener_poll, "listenerPoll")
        taskMgr.add(self.reader_poll, "readerPoll", 1)
        taskMgr.add(self.send_messages, "sendPoll", 101)

        taskMgr.doMethodLater(3, self.disconnect_check, "disconnectPoll")
        
    '''
    def set_need_update(self, val):
        if val:
            taskMgr.doMethodLater(5, self.disconnect_check, "disconnectPoll")
        elif not val:
            taskMgr.remove("disconnectPoll")
    '''
        
    ##RECIEVING
    def disconnect_check(self, task):
        if self.cManager.reset_connection_available():
            disconnected = PointerToConnection()
            if self.cManager.get_reset_connection(disconnected):
                try:
                    index = self.connections.index(disconnected.p())
                    self.availableSlots.append(index)
                    self.cReader.remove_connection(self.connections[index])
                    messenger.send("disconnect", [str(index),])
                    return Task.cont
                except:
                    print("server Error: unknown disconnect")
                    #messenger.send("serverError")
                    self.shut_down()
                    return Task.done
                    
                
        return Task.again
    
    def kick(self, kickid):
        self.send_direct("kick", kickid)#you have been kicked       

        kickcon = self.connections[kickid]
        self.cReader.remove_connection(kickcon)
        self.availableSlots.append(kickid)
        self.add_message("disconnect", (str(kickid),))
                
    def listener_poll(self, task):
        if self.cListener.new_connection_available():
            #print("got connection")
            rSock = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()

            if self.cListener.get_new_connection(rSock,netAddress,newConnection):
                newConnection = newConnection.p()
                if len(self.availableSlots) >= 1:#We have a slot from a disconnected player
                    self.addresses[self.availableSlots[0]] = netAddress
                    self.connections[self.availableSlots[0]] = newConnection
                    self.availableSlots.pop(0)
                else:#no available slot, creating new one
                    self.addresses.append(netAddress)
                    self.connections.append(newConnection)
                self.cReader.add_connection(newConnection)
                #Let the client know their number
                newAddress = self.addresses.index(netAddress)
                self.send_direct("introduce", newAddress, (str(newAddress),))
        return Task.cont
    
    def reader_poll(self, task):
        err = False
        while self.cReader.dataAvailable() and not err:
            err= self.proc_data()
        return task.cont

    def proc_data(self):
        datagram = NetDatagram()
            
        if self.cReader.getData(datagram):
            #try:
            iterator = DatagramIterator(datagram)
            #Begin processing commands
            commands = iterator.getString().split(";")
            for com in commands:
                if com == "":
                    continue
                if msgFilterStandard(com):
                    messenger.send(com)
                            
                comInfo = msgFilterValue(com)#Either False or a tuple containing the type of data for this message and how much of it we need
                if comInfo:
                    count = 0
                    target = comInfo[1]
                    param = []
                    while count < target:
                        param.append(grabberTable[comInfo[0]](iterator))
                        count += 1
                    messenger.send(com, param)
                    '''
            except:#Something is seriously wrong, no way to fix. have to shut down server.
                self.shut_down()
                messenger.send("serverError")
                print("Massive server error: unindexed address")
                return True
            '''    
                                        
        else:
            print("data grab fail")
            return False
    
    ##SENDING
    def add_message(self, mesg, val = None):
        '''
        mesg: event to send to connections.
        val: values of said event. should be enclosed in a tuple.
        '''
        if val:
            if msgFilterValue(mesg):
                self.outBox.append(mesg)
                self.valBox.append(val)
        else:
            if msgFilterStandard(mesg):
                self.outBox.append(mesg)
            

    def send_messages(self, task):
        if len(self.outBox) > 0:
            newDatagram = NetDatagram()

            msgString = ""
            for message in self.outBox:
                msgString += message
                msgString += ";"
            newDatagram.add_string(msgString)
            
            for message in self.outBox:#Similar to above, but we have to send the command string before all values, so this is it's own loop.
                comInfo = msgFilterValue(message)
                if comInfo:
                    vals = self.valBox[0]
                    count = 0
                    for val in vals:
                        setterTable[comInfo[0]](newDatagram, val)
                        count += 1
                        if count >= comInfo[1]:
                            break
                    self.valBox.pop(0)
        
            for i in self.connections:
                if self.connections.index(i) not in self.availableSlots:
                    self.cWriter.send(newDatagram, i)
            self.outBox.clear()
            self.valBox.clear()#just to be safe
        return Task.cont
    

    def send_direct(self, message, index, vals = None):
        '''
        Send a message to a single player. properties:
        message:string, vals:tuple, index:string
        '''
        newDatagram = NetDatagram()
        
        if vals:
            comInfo = msgFilterValue(message)
            if not comInfo: return False
            
            newDatagram.add_string(message)
            
            count = 0
            for val in vals:
                setterTable[comInfo[0]](newDatagram, val)
                count += 1
                if count >= comInfo[1]:
                    break
                

        elif msgFilterStandard(message):
            newDatagram.add_string(message)
        else: return False
            
        if int(index) not in self.availableSlots:
            '''newDatagram.set_connection(self.connections[int(index)])#These are probably unnessisary.
            newDatagram.set_address(self.addresses[int(index)])'''#I'm hoping that these values are set by the end connection reader, but I'm making this code ret2go just in case.
            if not self.cWriter.send(newDatagram, self.connections[int(index)]):
                pass    
                #print('send failed')
                    
            return True
        return False#We were trying to send to a free address
    
    def send_exclude(self, message, index, vals = None):#send a message to everyone but the given id.
        count = 0
        intIndex = int(index)
        for connection in self.connections:
            thisId = self.connections.index(connection)
            if (thisId in self.availableSlots) or (thisId == intIndex):
                continue
            else:
                self.send_direct(message, thisId, vals)
        

    ##ADMINISTRATIVE
    
    def disconnect_all(self):
        #print('disconnecting all')
        for client in self.connections:
            self.cReader.remove_connection(client)
        self.connections = []
        self.cManager.close_connection(self.tcpSocket)
        
    def shut_down (self):
        #self.send_messages(None)
        self.disconnect_all()
        taskMgr.remove("listenerPoll")
        taskMgr.remove("readerPoll")
        taskMgr.remove("disconnectPoll")
        taskMgr.remove("sendPoll")