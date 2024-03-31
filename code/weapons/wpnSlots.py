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
    max_slots = 6

    def __init__(self):
        #slot dictionary
        self._slots = {}
        self._slotMask = BitMask16(0)

        self._activeSlot = 0
        self._subSlot = 0
        

    def add_weapon(self, weapon: slotWeapon):
        slot = weapon.slot
        if not self._slotMask.get_bit(slot):
            self._slots[slot] = []
            self._slotMast.set_bit(slot)
        self._slots[slot].insert(weapon.priority, weapon)
        

    def change_weapon(self, amnt: int):#amnt should be 1 or -1
        slotLen = len(self.slots[self._activeSlot])
        if slotLen > 1 and (self._subSlot + amnt) <= (slotLen - 1):
            wpn = self._slots[self.activeSlot][self._subSlot + amnt]
            self.activate_weapon(wpn)
            self._subSlot += amnt
            return
        del slotLen
        
        nAmnt = self._activeSlot + amnt
        tries = 0
        while (not self._slotMask.get_bit(nAmnt)) and (tries < 2):
            if nAmnt + amnt < 0: nAmnt, tries = self.max_slots, tries + 1
            elif nAmnt + amnt > self.max_slots: nAmnt, tries = 0, tries + 1
            else: nAmnt = nAmnt + amnt
        if tries > 2 or nAmnt == self._activeSlot: return#We looped around and there are no other valid slots, do nothing
        del tries
        
        self._subSlot = 0 if amnt > 0 else len(self._slots[nAmnt]) - 1
        self._activeSlot = nAmnt
        wpn = self._slots[self._activeSlot][self._subSlot]
        self.activate_weapon(wpn)
        

    def goto_slot(self, slotNum):
        if not self._slotMask.get_bit(slot): return
        slot = self._slots[slotNum]
        
        if self._activeSlot != slotNum or self._subSlot + 1 > len(slot) - 1:
            self._subSlot = 0
            self._activeSlot = slotNum
        else:
            self._subSlot += 1
        
        wpn = slot[self._subSlot]
        self.activate_weapon(wpn)
        

    def activate_weapon(self, nWpn: slotWeapon):
        if nWpn is self.actWpn: return
        self.actWpn.de_activate(self)
        self.actWpn = nWpn
        self.actWpn.activate(self)
        

    def destroy(self):
        del self._slots
        del self._slotMask
        del self.actWpn
        del self._activeSlot
        del self._subSlot