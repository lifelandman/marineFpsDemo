from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from enum import Enum

class entBase(DirectObject):
    #......................................................................................................................................
    tasks = (#(task name string, string attribute name of task function, optional: sort)
        )
    
    delayTasks = (#(task name string, string attribute name of task function, delay*NOT OPTIONAL*,  sort)
        )#NOTE:: There is a possibility that we might want to do a task right away and still set a delay... too bad!
    
    events = (#(event name string, string attribute name of event function)
        )

    excludedInheritedBehavior = (#String of any events/tasks you want to be excluded from behavior in a base class.
        )
    #``````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    
    def __init__(self, name: str = '', netControllableBy: tuple = (), **kwargs):#we accept kwargs even though we don't use them to catch anything that might fall through
        
        self.name = name
        
        if len(kwargs) > 0:
            print("warning! kwargs len recieved by entBase is ==", str(len(kwargs)))
            
        self.acceptOnce("gameStart", self.start_interactivity)#Wait until the game starts so all players can have better synchronization

        self.accept("server: building msg lists", self.announce_net_commands)
        self.announce_net_commands(netControllableBy)
        

    def start_interactivity(self):
        name = self.name

        #build exclusion list
        exclusions = []
        for ent in self.__class__.__mro__:
            if not issubclass(ent, entBase): continue#Stupid hack
            exclusions += ent.excludedInheritedBehavior

        #add tasks
        for ent in self.__class__.__mro__:#This should contain ourselves and all parents, so we automatically get access to parent tasks/events
            if not issubclass(ent, entBase): continue#Stupid hack

            for taskGroup in ent.tasks:
                tskName = taskGroup[0].format(name = name)
                if tskName in exclusions: continue#Skip if we specifically don't want this parent behavior
                if len(taskGroup) <3:
                    self.addTask(getattr(self, taskGroup[1]), tskName)
                else:
                    self.addTask(getattr(self, taskGroup[1]), tskName, sort = taskGroup[2])
            #add delayed tasks
            for taskGroup in ent.delayTasks:
                tskName = taskGroup[0].format(name = name)
                if tskName in exclusions: continue
                if len(taskGroup) <4:
                    self.doMethodLater(taskGroup[2], getattr(self, taskGroup[1]), tskName)
                else:
                    self.doMethodLater(taskGroup[2], getattr(self, taskGroup[1]), tskName, sort = taskGroup[3])
            #accept events
            for eventGroup in ent.events:
                evntName = eventGroup[0].format(name = name)
                if evntName in exclusions: continue
                self.accept(evntName, getattr(self, eventGroup[1]))

    net_commands = (#(command name, optional, but need both:: type, number of times to gather information)
        )
    host_net_commands = (#just command name
        )
    def announce_net_commands(self, controllableBy: tuple):#Tells commonMsg what sorts of commands we'll use, and ensures incorrect connections can't control us.
        if base.isHost:
            for control in controllableBy:
                base.server.grant_access(self.name, control)

        for ent in self.__class__.__mro__:
            if not issubclass(ent, entBase): continue#Stupid hack

            for command in ent.net_commands:
                if len(command) ==1:
                    base.server.add_command(command[0])
                else:
                    base.server.add_command_value(command[0], command[1], command[2])

            if base.isHost:
                for command in ent.host_net_commands:
                    base.server.add_host_filter(command)
            
    def destroy(self):
        self.ignoreAll()
        self.removeAllTasks()
        self.detectLeaks()
        del self.name
        

'''#DEPRICATED
#Now entBase stores names so it can put entity name into accepted events if need be
#Before this highly engineered auto-accept system was underused because it wasn't flexible enough
class entNamable(entBase):#since a lot of things would likely need a 'name' attribute, I'm defining this in this file as well.
    def __init__(self, name: str = '', **kwargs):
        self.name = name
        super().__init__(*kwargs)#super gives us a handle to a parent class
        
    def destroy(self):#kind of redundant since instance variables usually get cleaned up automatically whenever a instance falls out of all scopes,
        del self.name#but usefull for illustrating how you HAVE to call super if you don't want to manually pick and call elements from parent classes.
        super().destroy()
'''