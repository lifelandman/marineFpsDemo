
import builtins
from panda3d.core import Mersenne as rng#max 2,147,483,647
from direct.task import Task
from direct.showbase.DirectObject import DirectObject

class randomGen(DirectObject):
    samePeriod = 3#number of frames until we need to generate a new number
    def __init__(self):
        self.rng = rng(6062002)
        self.rngCount = 0

        self.updated = False
        self.update = 0
        builtins.gameSharedRandom = 0
        self.add_task(self.randomize, 'randomizer', sort =2)
        self.accept("rng", self.accept_update)
        
    def randomize(self, taskobj):
        if not isHost and self.updated:
            self.rng = rng(self.update)
            builtins.gameSharedRandom = self.update
            self.updated = False
            self.rngCount = 0
            return Task.cont
        
        if self.rngCount >= randomGen.samePeriod:
            self.rngCount = 0
            builtins.gameSharedRandom = self.rng.get_uint31()
            if isHost:
                gameServer.add_message("rng", (gameSharedRandom,))#send new rng value to all clients
        
        else: self.rngCount += 1

        return Task.cont
    
    def accept_update(self, val):
        self.updated = True
        self.update = val
        
    def delete(self):
        taskMgr.remove('randomizer')
        del builtins.gameSharedRandom