'''
Author: JAMS
This file contains the base class for theoretically all weapons.
'''


'''
weaponBase: this class is the base for everything. it stores the weapon user, automatically calls the pick_up function, and calls the copy function if there is anything to copy.
'''
class weaponBase():
    
    def __init__(self, user = None, copy = None, **kwargs):
        self.user = user
        
        self.pick_up()
        
        if copy:
            self.copy(copy)
    
    def pick_up(self):#called automatically when user gets weapon
        pass
    
    def copy(self, other):#copy attributes from another weapon(I.E. ammo, eyelander heads)
        pass
    
    def destroy(self):
        del self.user