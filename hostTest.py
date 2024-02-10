from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from code.servers.host import hostServer


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        
        base.disableMouse()
        base.cam.set_pos(0,-30,5)
        self.model = loader.loadModel("panda.egg")
        self.model.reparentTo(render)
        self.accept("rot", self.rotModel)
        taskMgr.add(self.speen, "speen", 1)
        
        self.server = hostServer()
        
    def speen(self, task):
        self.model.set_h(self.model, 1)
        self.server.add_message("rot", (self.model.get_h(),))
        return Task.cont
        
    def rotModel(self, deg):
        self.model.set_h(deg)


app = MyApp()
app.run()
