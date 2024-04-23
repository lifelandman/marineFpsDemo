from direct.task import Task

from code.weapons.wpnSlots import slotMgr

from .wpnTrgr import trgrWait
class ammoWeapon(trgrWait):
    loadWait = 2
    clipSize = 5
    storageMax = 50
    
    primAmnt = 1
    secAmnt = primAmnt
    bufferTime = 0.7
    
    manual_reload = True#False if this can only reload on empty clip, like DODS m1
    
    def __init__(self, **kwargs):
        self._clip = self.clipSize
        self._storage = self.storageMax
        
        self._isReloading = False
        
        self._fireBuffer = 0.0
        self._isBuffering = False
        self._bufferType = False
        
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
                self.begin_count(self.wait)
                self._clip -= self.primAmnt
        elif self._isReloading:
            self.queue_fire_buffer(False)
            
            
    def fire2(self):
        if self._fireReady:
            if (self._clip) <= 0:
                self.trigger_reload()
            else:
                self.secondaryFire()
                self._fireReady = False
                self.begin_count(self.subWait)
                self._clip -= self.secAmnt
        elif self._isReloading:
            self.queue_fire_buffer(True)
    
    def queue_fire_buffer(self, bType):
        self._isBuffering = True
        self._bufferType = bType
        self._fireBuffer = self.bufferTime

    def trigger_reload(self):
        if self._isReloading or self._counting or self._storage <= 0 or self._clip == self.clipSize:
            return
        self._isReloading = True
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
            self._isReloading = False
            if self._fireBuffer and self._isBuffering:
                if not self._bufferType: self.fire1()
                else: self.fire2()
                self._isBuffering = False
            return Task.done
        
        if self._fireBuffer:
            self._fireBuffer -= globalClock.get_dt()
            if self._fireBuffer < 0:
                self._fireBuffer = 0
                self._isBuffering = False
        return Task.cont
    
    def copy(self, other):
        self._clip = other._clip
        self._storage = other._storage
        super().copy()
        
    def destroy(self):
        del self._isReloading
        del self._clip
        del self._storage
        super().destroy()
        

class ammoTest(ammoWeapon):
    
    secAmnt = 0
    
    def primaryFire(self):
        print(self._clip, self._storage)
        
    def secondaryFire(self):
        print('secFire')
    
    def clip_change(self, goal, taskObj):
        if taskObj.time >= goal: print('reloaded')
        return super().clip_change(goal, taskObj)