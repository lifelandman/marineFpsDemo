

from direct.showbase.DirectObject import DirectObject
from direct.task import Task

class deathMatchLogic(DirectObject):
    spawnWaveLen = 20

    def __init__(self):
        self.accept("death", self.reap)
        self._spawnCounting = False
        
    def reap(self, dead: str, killer: str):#HELL YEAH FINALLY I CAN CALL A FUNCTION THIS
        if not self._spawnCounting:
            self.do_method_later(self.spawnWaveLen, self.spawnWave_trigger, "spawnWave, activate")
            self._spawnCounting = True
            
    def spawnWave_trigger(self, taskObj):
        base.game_instance.playerMgr.spawn_wave()
        self._spawnCounting = False
        return Task.done