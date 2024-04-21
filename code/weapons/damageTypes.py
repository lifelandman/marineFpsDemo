

class damageTypeBase():
    pointDamage = 1#Amount of damage without scaling
    
    def __init__(self, name):#damage target indipendant of calc functions
        self.targetName = name
    
    def calc_from_rayCast(self, entry, mul: int = 1, **kwargs):
        self.finalDamage = self.pointDamage * mul#Set finalDamage to a zero default to prevent crashes when damage type does not have appropriate calc function
    
    #TODO:: add other calculation types
    
    def apply(self, targetEnt):#do here so we can apply status effects, etc.
        targetEnt.health -= self.finalDamage
    
    def serialize(self):#This should only be called from within the 
        if self.finalDamage > 0: base.server.add_message("playerDamageAdd{" + self.targetName, (-self.finalDamage,))



class bulletDamageType(damageTypeBase):
    
    def calc_from_rayCast(self, entry, mul: int = 1, falloff: int = 1, **kwargs):
        '''
        mul: damage modifier
        falloff: amount of damage lost per unit. for refrence, default player is 2 units tall.
        '''
        #super().calc_from_rayCast(entry, mul, falloff, **kwargs)#This is only here for if we're placed ahead of some other damage type
        self.finalDamage = min((self.pointDamage * mul) - (entry.get_interior_point(entry.get_from_node_path()).length() * falloff), 0)