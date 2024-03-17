from .entModels import playerMdlBase

class playerMdl(playerMdlBase):
    parts = {"torso" : (("Diaphram",),("L.thigh", "L.calf", "L.Foot", "L.lowleg", "R.thigh")),
             "legs" : (("R.thigh", "L.thigh", "L.calf", "L.Foot"),())}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.loop("idle","torso", 1)
        #self.loop("LookUp", "torso", 0)
        #self.loop('backRun', 'legs')
        
    def set_look(self, p: float):
        return
        if p > 0:
            scale = p/85
            self.change_blend("idle", "torso", 1 - scale)
            self.change_blend("LookUp", "torso", scale)
        else:
            self.change_blend("idle", "torso", 1)
            self.change_blend("LookUp", "torso", 0)
            
    def walk(self, x:float, y:float):
        idleTest = 0
        scale = abs(x) + abs(y)
        
        if x == 120:
            if x > 0:
                if self.loop("strideR", "legs", 1.0):
                    self.stop("strideL", "legs")
            else:#No need to run another check, we know this is the case
                if self.loop("strideL", "legs", 1.0):
                    self.stop("strideR", "legs")
                    '''
        else:
            if not self.stop("strideR", "legs"):
                self.stop("strideL", "legs")
            idleTest += 1
            '''
        
        if y != 0:
            if y > 0:
                self.loop("run", "legs", 1.0)
                self.stop("backRun", "legs")
            else:#No need to run another check, we know this is the case
                self.loop("backRun", "legs", 1.0)
                self.stop("run", "legs")
        '''
        else:
            if not self.stop("run", "legs"):
                self.stop("backRun", "legs")
            idleTest += 1
            
        '''
        if idleTest >= 2:
            self.pose("idle", "legs")