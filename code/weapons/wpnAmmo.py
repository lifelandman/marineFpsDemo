

from .wpnTrgr import trgrWait
class ammoWeapon(trgrWait):
    loadWait = 2
    clipSize = 5
    storageMax = 50
    
    primAmnt = 1
    secAmnt = primAmnt
    
    def __init__(self, **kwargs):
        self._clip = self.clipSize
        self._storage = self.storageMax
        super().__init__(**kwargs)
        

    def fire1(self):
        if self._fireReady:
            if (self._clip - self.primAmnt) <= 0:
                self.trigger_reload()
            else:
                self.primaryFire()
                self._fireReady = False
                self.addTask(self.count_down, "countDownTask", sort = 11, extraArgs=[self.wait,], appendTask=True)
                self._clip -= self.primAmnt
            
            
    def fire2(self):
        if self._fireReady:
            if (self._clip - self.secAmnt) <= 0:
                self.trigger_reload()
            else:
                self.secondaryFire()
                self._fireReady = False
                self.addTask(self.count_down, "countDownTask", sort = 11, extraArgs=[self.subWait,], appendTask=True)
                self._clip -= self.secAmnt
    

    def trigger_reload(self):
        if self._storage <= 0:
            return
        self._fireReady = False
        self.user._reload = True
        self.addTask(self.reload, "reload", sort = 11, extraArgs = [self.loadWait,], appendTask = True)

    def reload(self, goal, taskObj):
        if taskObj.time >= goal:
            if self._storage >= self.clipSize:
                self._clip = self.clipSize
                self._storage -= self.clipSize
            else:
                self._clip = self._storage
                self._storage = 0
            fireReady = True
            return Task.done
        return Task.cont