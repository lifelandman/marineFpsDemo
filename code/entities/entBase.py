from direct.showbase.DirectObject import DirectObject
from direct.task import Task

class entBase(DirectObject):
    
    tasks = (#(task name string, string attribute name of task function, optional: sort)
        )
    
    delayTasks = (#(task name string, string attribute name of task function, delay*NOT OPTIONAL*,  sort)
        )#NOTE:: There is a possibility that we might want to do a task right away and still set a delay... too bad!
    
    events = (#(event name string, string attribute name of event function)
        )
    
    def __init__(self, name: str = '', **kwargs):#we accept kwargs even though we don't use them to catch anything that might fall through
        
        self.name = name
        
        if len(kwargs) > 0:
            print("warning! kwargs len recieved by entBase is ==", str(len(kwargs)))
        #add tasks
        for taskGroup in self.tasks:
            tskName = taskGroup[0].format(name = name)
            if len(taskGroup) <3:
                self.addTask(getattr(self, taskGroup[1]), tskName)
            else:
                self.addTask(getattr(self, taskGroup[1]), tskName, sort = taskGroup[2])
        #add delayed tasks
        for taskGroup in self.delayTasks:
            tskName = taskGroup[0].format(name = name)
            if len(taskGroup) <4:
                self.doMethodLater(taskGroup[2], getattr(self, taskGroup[1]), tskName)
            else:
                self.doMethodLater(taskGroup[2], getattr(self, taskGroup[1]), tskName, sort = taskGroup[3])
        #accept events
        for eventGroup in self.events:
            evntName = eventGroup[0].format(name = name)
            self.accept(evntName, getattr(self, eventGroup[1]))
            
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