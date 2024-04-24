from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton, DirectEntry

from .lobby import lobby_ui
from .options.option_menu import optionsMenu

class menu_ui(DirectObject):
    
    ip = '::1'
    
    def __init__(self, first_start = False):
        super().__init__()
        
        if first_start:
            self.splash = OnscreenText(text='made with Panda3d', pos=(0, 0), scale=0.09)
            taskMgr.add(self.splashRemoval, 'Splash text removal')
        else:
            self.build_menu()
        
    def build_menu(self):
        self.optionButton = DirectButton(text="options", scale = 0.08, parent= base.aspect2d, command= self.options, pos = (0, 0, 0.3))
        self.hostButton = DirectButton(text="host server", scale = 0.08, parent= base.aspect2d, command= self.host_start, pos = (0, 0, -0.5))
        
        ###Local connection stuff
        self.localConnectionStuff = []
        self.localConnectionStuff.append(DirectEntry(scale = 0.08, parent= base.aspect2d, command= self.set_ip, pos = (-0.4, 0, 0.05)))
        self.localConnectionStuff.append(DirectButton(text="join server", scale = 0.08, parent= base.aspect2d, command= self.client_start, pos = (0, 0, -0.05)))
        
    def set_ip(self, ip):
        self.ip = ip
        
    def delete(self):
        self.optionButton.destroy()
        self.hostButton.destroy()
        #Delete variables
        del self.optionButton
        del self.hostButton  

        for i in self.localConnectionStuff:
            i.destroy()
        del self.localConnectionStuff
        
        self.ignoreAll()
        
    def host_start(self):
        self.delete()
        lobby_ui(self, True)
        
    def client_start(self):
        self.delete()
        lobby_ui(self, False, self.ip)
        
    def playtest(self):
        from .game import game_world
        self.delete()
        game_world()
    
    def options(self):
        self.delete()
        optionsMenu(self)
        
    def splashRemoval(self, task):
        if task.time > 1.5 or base.mouseWatcherNode.is_button_down("space"):
            self.splash.destroy()
            self.build_menu()
            return Task.done
        else:
            return Task.cont

def menu_start(sb):

    #create a panda text splash. TODO::make this fancy
    splash = OnscreenText(text='made with Panda3d', pos=(0, 0), scale=0.09)
    taskMgr.add(splashRemoval, 'Splash text removal', extraArgs=[splash], appendTask=True)
