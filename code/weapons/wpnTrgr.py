
from direct.showbase.DirectObject import DirectObject

from .wpnSlots import slotWeapon, slotMgr


class trgrWeapon(slotWeapon, DirectObject):#Can't think of a way to not split the planned trgrWeapon into two classes.
    hasAltFire = True
    
    def activate(self, mgr: slotMgr):
        self.accept(mgr.playerName + "-fire1", self.fire1)
        if self.hasAltFire: self.accept(mgr.playerName + "-fire2", self.fire2)
        super().activate
        
    def de_activate(self, mgr: slotMgr):
        self.ignore(mgr.playerName + "-fire1")
        if self.hasAltFire: self.ignore(mgr.playerName + "-fire2")
        super().de_activate
    
    def fire1(self):
        self.primaryFire()
    
    def fire2(self):
        self.secondaryFire()
    

    def primaryFire(self):##These two functions can be ignored in a child class, but this makes it easier to 
        pass##              Define weapons with unique trigger behavior
    ##In particular, weapons that don't endlessly fire every frame (almost all of them) have some delat
    #And the propellerpack has diffrent behavior above and below water.
    def secondaryFire(self):
        pass
    

from direct.task import Task
class trgrWait(trgrWeapon):
    '''
    time1 and time2 have a limit so that they can only be called so often
    '''
    
    wait = 0.5
    subWait = wait
    
    def __init__(self, **kwargs):
        self._fireReady = True
        self._counting = False
        super().__init__(**kwargs)

    def fire1(self):
        if self._fireReady:
            self.primaryFire()
            self._fireReady = False
            self.begin_count(self.wait)
            
    def fire2(self):
        if self._fireReady:
            self.secondaryFire()
            self._fireReady = False
            self.begin_count(self.subWait)
            
    def begin_count(self, amnt):
        if not self._counting:
            self.addTask(self.count_down, "countDownTask", sort = 11, extraArgs=[amnt,], appendTask=True)
            self._counting = True

    def count_down(self, goal, taskObj):
        if taskObj.time >= goal:
            self._fireReady = True
            self._counting = False
            return Task.done
        return Task.cont

class trgrTest(trgrWeapon):
    
    slot = 0
    priority = 1
    
    def activate(self, mgr : slotMgr):
        super().activate(mgr)
        print('activated')
    
    def fire1(self):
        print('fire1')
        
    def fire2(self):
        print('fire2')
        

class waitTest(trgrWait):
    slot = 1
    priority = 0
    
    def activate(self, mgr : slotMgr):
        super().activate(mgr)
        print('timeAct')
    
    def primaryFire(self):
        print('timeFire!')
        
    def secondaryFire(self):
        print('IKU ZE!!!!')