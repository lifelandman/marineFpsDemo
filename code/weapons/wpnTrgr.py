
from direct.showbase.DirectObject import DirectObject

from .wpnSlots import slotWeapon, slotMgr


class trgrWeapon(slotWeapon, DirectObject):#Can't think of a way to not split the planned trgrWeapon into two classes.
    
    def activate(self, mgr: slotMgr):
        self.accept(mgr.playerName + "-fire1", self.fire1)
        self.accept(mgr.playerName + "-fire2", self.fire2)
        super().activate
        
    def de_activate(self, mgr: slotMgr):
        self.ignore(mgr.playerName + "-fire1")
        self.ignore(mgr.playerName + "-fire2")
        super().de_activate
    
    def fire1(self):
        pass
    
    def fire2(self):
        pass
    

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