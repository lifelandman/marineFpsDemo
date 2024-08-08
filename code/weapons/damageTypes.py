

class damageTypeBase():
    pointDamage = 1#Amount of damage without scaling
    
    def __init__(self, source):#damage target indipendant of calc functions
        self.source = source
    
    def calc_from_rayCast(self, entry, mul: int = 1, **kwargs):
        self.finalDamage = self.pointDamage * mul#Set finalDamage to a zero default to prevent crashes when damage type does not have appropriate calc function
    
    def calc_over_time(self, mul:int = 1, time:float = 1):
        self.finalDamage = mul * time
    
    #TODO:: add other calculation types
    
    def apply(self, targetEnt):#do here so we can apply status effects, etc.
        targetEnt.health -= self.finalDamage
    


class bulletDamageType(damageTypeBase):
    
    pointDamage = 10
    
    def calc_from_rayCast(self, entry, mul: int = 1, falloff: int = 0.5, **kwargs):
        '''
        mul: damage modifier
        falloff: amount of damage lost per unit. for refrence, default player is 2 units tall.
        '''
        #super().calc_from_rayCast(entry, mul, falloff, **kwargs)#This is only here for if we're placed ahead of some other damage type
        self.finalDamage = max((self.pointDamage * mul) - (entry.get_surface_point(entry.get_from_node_path()).length() * falloff), 0)
        


class healingDamageType(damageTypeBase):
    def apply(self, targetEnt):
        if targetEnt.health + self.finalDamage <= targetEnt.maxHealth:
            targetEnt.health += self.finalDamage
        else:
            targetEnt.health = targetEnt.maxHealth