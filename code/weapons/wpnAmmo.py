from direct.task import Task

from code.weapons.wpnSlots import slotMgr

from .wpnTrgr import trgrWait
class ammoWeapon(trgrWait):
    loadWait = 2
    clipSize = 5
    storageMax = 50
    
    primAmnt = 1
    secAmnt = primAmnt
    
    manual_reload = True#False if this can only reload on empty clip, like DODS m1
    
    def __init__(self, **kwargs):
        self._clip = self.clipSize
        self._storage = self.storageMax
        self._is_reloading = False
        super().__init__(**kwargs)
        
    def activate(self, mgr: slotMgr):
        if self.manual_reload: self.accept('reload{' + mgr.playerName, self.trigger_reload)
        super().activate(mgr)
        
    def de_activate(self, mgr: slotMgr):
        if self.manual_reload: self.ignore('reload{' + mgr.playerName)
        super().de_activate(mgr)
        

    def fire1(self):
        if self._fireReady:
            if (self._clip) <= 0:
                self.trigger_reload()
            else:
                self.primaryFire()
                self._fireReady = False
                self.addTask(self.count_down, "countDownTask", sort = 11, extraArgs=[self.wait,], appendTask=True)
                self._clip -= self.primAmnt
            
            
    def fire2(self):
        if self._fireReady:
            if (self._clip) <= 0:
                self.trigger_reload()
            else:
                self.secondaryFire()
                self._fireReady = False
                self.addTask(self.count_down, "countDownTask", sort = 11, extraArgs=[self.subWait,], appendTask=True)
                self._clip -= self.secAmnt
    

    def trigger_reload(self):
        if self._is_reloading or self._storage <= 0 or self._clip == self.clipSize:
            return
        self._is_reloading = True
        self._fireReady = False
        self.user._reload = True
        self.addTask(self.clip_change, "reload", sort = 11, extraArgs = [self.loadWait,], appendTask = True)

    def clip_change(self, goal, taskObj):#can't call this reload since it seems that name is taken
        if taskObj.time >= goal:
            if self._storage >= self.clipSize:
                self._storage -= self.clipSize - self._clip
                self._clip = self.clipSize
            else:
                self._clip = self._storage
                self._storage = 0
            self._fireReady = True
            self._is_reloading = False
            return Task.done
        return Task.cont
    
    def copy(self, other):
        self._clip = other._clip
        self._storage = other._storage
        super().copy()
        
    def destroy(self):
        del self._is_reloading
        del self._clip
        del self._storage
        super().destroy()
        

class ammoTest(ammoWeapon):
    
    def primaryFire(self):
        print(self._clip, self._storage)
    
    def clip_change(self, goal, taskObj):
        if taskObj.time >= goal: print('reloaded')
        return super().clip_change(goal, taskObj)