'''
this file contains the system for "slot weapons".
'''


from .wpnBase import weaponBase


class slotWeapon(weaponBase):
    
    slot = 0
    priority = 10
    
    anim_set = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._isActive = False
    
    def activate(self, mgr):
        self._isActive = True
    
    def de_activate(self, mgr):
        self._isActive = False
    
    def destroy(self):
        if self._isActive: self.de_activate()
        super().destroy()

    #To be overriden, to avoid crashes
    def string_ammo(self):
        return ''
    

from panda3d.core import BitMask16
class slotMgr():
    max_slots = 6

    def __init__(self, playerName: str):
        #slot dictionary
        self._slots = {}
        self._slotMask = BitMask16(0)

        self._activeSlot = 0
        self._subSlot = 0
        
        self.actWpn = None
        
        self._weaponsEnabled = True
        
        self.playerName = playerName#storing this so weapons can set up unique events if need be.
        #Especially important for collisions/ the weapon needs to be able to know what collisions it needs to process.
        

    def add_weapon(self, weapon: slotWeapon):
        slot = weapon.slot
        if not self._slotMask.get_bit(slot):
            self._slots[slot] = []
            self._slotMask.set_bit(slot)
        self._slots[slot].insert(weapon.priority, weapon)
        if not self.actWpn:
            self._activeSlot = weapon.slot
            self._subSlot = self._slots[slot].index(weapon)
            self.first_activate(weapon)
        

    def change_weapon(self, amnt: int):#amnt should be 1 or -1
        if not self._weaponsEnabled: return#Skip the function if we're in a weapons forbidden zone
        
        slotLen = len(self._slots[self._activeSlot]) - 1
        potenSubSlot = self._subSlot + amnt
        if slotLen > 0 and potenSubSlot <= (slotLen):
            if (0 > potenSubSlot):#not pretty, but it gets logic flow right
                if (self._slotMask.get_lowest_on_bit() == self._activeSlot):
                    potenSubSlot = slotLen
                    wpn = self._slots[self._activeSlot][potenSubSlot]
                    self.activate_weapon(wpn)
                    self._subSlot = potenSubSlot
                    return
            else:
                wpn = self._slots[self._activeSlot][potenSubSlot]
                self.activate_weapon(wpn)
                self._subSlot = potenSubSlot
                return
        elif (potenSubSlot > slotLen) and (self._slotMask.get_highest_on_bit() == self._activeSlot):
            potenSubSlot = 0
            wpn = self._slots[self._activeSlot][potenSubSlot]
            self.activate_weapon(wpn)
            self._subSlot = potenSubSlot
            return
        del slotLen
        del potenSubSlot
        

        nAmnt = self._activeSlot + amnt
        if nAmnt < 0: nAmnt = self._slotMask.get_highest_on_bit()
        tries = 0
        while (not self._slotMask.get_bit(nAmnt)) and (tries < 2):
            if nAmnt + amnt < 0: nAmnt, tries = self._slotMask.get_highest_on_bit, tries + 1
            elif nAmnt + amnt > self.max_slots: nAmnt, tries = 0, tries + 1
            else: nAmnt = nAmnt + amnt
        if tries > 2 or nAmnt == self._activeSlot: return#We looped around and there are no other valid slots, do nothing
        del tries
        
        self._subSlot = 0 if amnt > 0 else len(self._slots[nAmnt]) - 1
        self._activeSlot = nAmnt
        wpn = self._slots[self._activeSlot][self._subSlot]
        self.activate_weapon(wpn)
        

    def goto_slot(self, slotNum):#Intended to be used for selecting weapons by number keys
        if not self._weaponsEnabled: return
        if not self._slotMask.get_bit(slotNum): return
        slot = self._slots[slotNum]
        
        if self._activeSlot != slotNum or self._subSlot + 1 > len(slot) - 1:
            self._subSlot = 0
            self._activeSlot = slotNum
        else:
            self._subSlot += 1
        
        wpn = slot[self._subSlot]
        self.activate_weapon(wpn)
        
    def goto_subSlot(self, slotNum, subNum):
        if not self._weaponsEnabled: return False
        if not self._slotMask.get_bit(slotNum): return False
        if slotNum == self._activeSlot and subNum == self._subSlot: return False
        slot = self._slots[slotNum]
        for weapon in slot:
            if weapon.priority == subNum:
                self.activate_weapon(weapon)
                self._activeSlot = slotNum
                self._subSlot = subNum
                return True
        return False
        

    def activate_weapon(self, nWpn: slotWeapon):
        if nWpn is self.actWpn: return
        self.actWpn.de_activate(self)
        self.first_activate(nWpn)
        
    def first_activate(self, wpn: slotWeapon):
        self.actWpn = wpn
        self.actWpn.activate(self)
        
        
    def disable_weapons(self):
        if self._weaponsEnabled:
            self._weaponsEnabled = False
            self.actWpn.de_activate(self)
        
    def enable_weapons(self):
        if not self._weaponsEnabled:
            self._weaponsEnabled = True
            self.actWpn.activate(self)


    def get_slots(self):
        slot = self.actWpn.slot
        priority = self.actWpn.priority#Remember, networked weapon changes occur with goto_subslot!!
        return slot, priority
        

    def destroy(self):
        self.actWpn.de_activate(self)
        for slot in self._slots.values():
            for wpn in slot:
                wpn.destroy()
                slot.pop(slot.index(wpn))
        del self._slots
        del self._slotMask
        del self.actWpn
        del self._activeSlot
        del self._subSlot
        
'''
class clientSlotMgr(slotMgr):
    pass
'''
        