from direct.showbase.DirectObject import DirectObject
from direct.showbase.Audio3DManager import Audio3DManager
from direct.task import Task
from panda3d.core import AudioManager

from .subAudio import audioTrgrBullet

class audioTrgrGlobal(DirectObject):
    def __init__(self):
        self.audioTrgrs = []
        self.audioTrgrs.append(audioTrgrBullet())
        
        self.audio3DList = []
        self.audioMgrList = []
        
        self.entSounds = {}
        
        self.add_task(self.updateMgrs, "updateAudio")
        

    def register_sound_source(self, name, np, *args:str):
        '''
        np acts as the "source" of the 3d audio,
        args is the names of all the sfx the user wants to access
        '''
        manager = AudioManager.create_AudioManager()#I don't even know how interrogate would handle this.
        self.audioMgrList.append(manager)
        manager3d = Audio3DManager(manager, base.camera)
        self.audio3DList.append(manager3d)
        manager3d.set_listener_velocity_auto()
        
        self.entSounds[name] = {}
        soundDict = self.entSounds[name]
        
        i = 0
        for arg in args:
            if i > 15:
                break
            for trgr in self.audioTrgrs:
                if arg in trgr.sounds.keys():
                    soundDict[arg] = trgr.register(manager3d, np, arg)
                    i +=1
                    break
        return self.audioMgrList.index(manager)
        

    def play(self, name, soundName):
        soundDict = self.entSounds[name]
        if soundName in soundDict:
            soundDict[soundName].play()
            return True
        return False
    

    def updateMgrs(self, taskobj):
        for mgr in self.audioMgrList:
            mgr.update()
        return Task.cont