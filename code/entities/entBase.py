from direct.showbase.DirectObject import DirectObject
from direct.task import Task

class entBase(DirectObject):
    
    tasks = (#(task name string, task function, sort)
        )
    
    delayTasks = (#(task name string, task function, delay*NOT OPTIONAL*,  sort)
        )#NOTE:: There is a possibility that we might want to do a task right away and still set a delay... too bad!
    
    events = (#(event name string, event function)
        )
    
    def __init__(self, **kwargs):#we accept kwargs even though we don't use them to catch anything that might fall through
        if len(kwargs) > 0:
            print("warning! kwargs len recieved by entBase is ==", str(len(kwargs)))
        #add tasks
        for taskGroup in self.tasks:
            if len(taskGroup) <3:
                self.addTask(taskGroup[1], taskGroup[0])
            else:
                self.addTask(taskGroup[1], taskGroup[0], sort = taskGroup[2])
        #add delayed tasks
        for taskGroup in self.delayTasks:
            if len(taskGroup) <4:
                self.doMethodLater(taskGroup[2], taskGroup[1], taskGroup[0])
            else:
                self.doMethodLater(taskGroup[2], taskGroup[1], taskGroup[0], sort = taskGroup[3])
        #accept events
        for eventGroup in self.events:
            self.accept(eventGroup[0], eventGroup[1])
            
    def destroy(self):
        self.ignoreAll()
        self.removeAllTasks()
        self.detectLeaks()
        

class entNamable(entBase):#since a lot of things would likely need a 'name' attribute, I'm defining this in this file as well.
    def __init__(self, name = 'name', **kwargs):
        self.name = name
        super().__init__(kwargs)#super gives us a handle to a parent class
        
    def destroy(self):#kind of redundant since instance variables usually get cleaned up automatically whenever a instance falls out of all scopes,
        del self.name#but usefull for illustrating how you HAVE to call super if you don't want to manually pick and call elements from parent classes.
        super().__init__()