from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader, ConnectionWriter
from panda3d.core import PointerToConnection, NetAddress, NetDatagram
from panda3d.core import NetDatagram, DatagramIterator
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from .commonMsg import msgFilterStandard, msgFilterValue, grabberTable, setterTable, add_my_msg, add_value_msg, initialize_msg_lists

class clientServer(DirectObject):
    def __init__(self, ip):
        initialize_msg_lists()
        #Define class variables needed elsewhere
        self.address= ip
        rendezvous = 20560
        #Outgoing message-related variables
        self.outBox = []#List of all events that need to be sent to the server
        self.valBox = []#List of message values where nessicary
        
        
        #create connection host
        self.cManager = QueuedConnectionManager()
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        
        #self.connection = self.cManager.open_UDP_connection(ip, rendezvous, False)
        self.connection = self.cManager.open_TCP_client_connection(ip, rendezvous, 3000)##TODO::add check if this connection fails
        if self.connection is None:#check if we found a connection
            self.success = False
            return
        self.cReader.add_connection(self.connection)
        self.success = True
        
        self.address = self.connection.get_address()
        
        #TASKS
        taskMgr.add(self.reader_poll, "readerPoll", 1)
        taskMgr.add(self.send_messages, "sendPoll", 101)
        taskMgr.doMethodLater(3, self.disconnect_check, "disconnectPoll")
        
        #Shut down when kicked
        self.accept("kick", self.shut_down)
    '''  
    def set_need_update(self, val):
        if val:
            
        elif not val:
            taskMgr.remove("disconnectPoll")
    '''
    ##RECIEVING
    def disconnect_check(self, task):
        if self.cManager.reset_connection_available():
            disconnected = PointerToConnection()
            if self.cManager.get_reset_connection(disconnected):
                messenger.send("exit_session")
                self.shut_down()
                return Task.done
        return Task.again
                
    
    def reader_poll(self, task):
        err = False
        count = 0#this allows for natural rubberbanding... and also for us to not be eternally stuck if the host has a much higher framerate.
        while self.cReader.dataAvailable() and not err and count <6:
            err= self.proc_data()
            count += 1
        return task.cont

    def proc_data(self):
        datagram = NetDatagram()
            
        if self.cReader.getData(datagram):
            #try:
            iterator = DatagramIterator(datagram)
            #Begin processing commands
            commands = iterator.getString().split(";")
            for com in commands:
                splitCom = com.split("{")
                comBase = splitCom[0]
                del splitCom

                if com == "":
                    continue
                if msgFilterStandard(comBase):
                    messenger.send(com)
                    continue
                            
                comInfo = msgFilterValue(comBase)#Either False or a tuple containing the type of data for this message and how much of it we need
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
                print("Massive server error while recieving messages!")
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
        #TODO:: add test make sure this is valid send event
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
        
            self.cWriter.send(newDatagram, self.connection)
            self.outBox.clear()
            self.valBox.clear()#just to be safe
        return Task.cont
    
    def send_direct(self, message, vals = None, i = "0"):#this exists to avoid crashes if we don't check if we're the host before trying to use this.
        print("warning! client is attempting to send direct!")
    
    def send_exclude(self, *args):#ditto
        pass
        

    ##ADMINISTRATIVE


    def shut_down (self):
        if self.success:
            self.cManager.close_connection(self.connection)
        taskMgr.remove("readerPoll")
        taskMgr.remove("disconnectPoll")
        taskMgr.remove("sendPoll")
        self.ignoreAll()

    def grant_access(self, name: str, controllableBy: int):
        pass

    def clear_access(self):
        pass
    
    def add_command(self, name):
        add_my_msg(name)

    def add_command_value(self, name: str, valueType: str, numTimes: int):
        add_value_msg(name, valueType, numTimes)