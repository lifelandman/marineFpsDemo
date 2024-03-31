'''
this file contains the system for "slot weapons".
'''


from .wpnBase import weaponBase


class slotWeapon(weaponBase):
    
    slot = 0
    priority = 10
    
    anim_set = ""
    
    def activate(self, mgr):
        pass
    
    def de_activate(self, mgr):
        pass



from panda3d.core import BitMask16
class slotMgr():
    def __init__(self):
        #slot dictionary
        self._slots = {}
        self._slotMask = BitMask16(0)

        self._activeSlot = 0
        self._subSlot = 0
        
    def add_weapon(self, weapon):
        slot = weapon.slot
        if not self._slotMask.get_bit(slot):
            self._slots[slot] = []
            self._slotMast.set_bit(slot)
        self._slots[slot].insert(weapon.priority, weapon)