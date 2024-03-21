from .entModels import playerMdlBase

class playerMdl(playerMdlBase):
    parts = {"torso" : (("Diaphram",),("*.thigh",)),
             "legs" : (("R.thigh", "L.thigh"),())}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pose("idle","torso", 1)
        self.pose("LookUp", "torso", 0)
        self.loop('backRun', 'legs')
        
        #Variables
        self.stepFrame = 0
        self.carryOverStp = False
        
    def set_look(self, p: float):
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
        gotFrame = False
        
        if y != 0:
            if y > 0:
                if self.carryOverStp:
                    self.pose("run", "legs", 1, self.stepFrame)
                    self.stop('backRun', 'legs')
                else:
                    if self.loop("run", "legs", 1.0):
                        self.stop("backRun", "legs")
                        self.stepFrame = self.get_frame('run', 'legs')
                        self.gotFrame = True
            else:#No need to run another check, we know this is the case
                if self.carryOverStp:
                    self.pose("backRun", "legs", 1, self.stepFrame)
                    self.stop("run", "legs")
                else:
                    if self.loop("backRun", "legs", 1.0):
                        self.stop("run", "legs")
                        self.stepFrame = self.get_frame('backRun', 'legs')
                        self.gotFrame = True

        else:
            if not self.stop("run", "legs"):
                self.stop("backRun", "legs")
            idleTest += 1
            

        if self.carryOverStp: self.carryOverStp = False

        
        if x != 0:
            if x > 0:
                if gotFrame:
                    self.pose('strideR', 'legs', 1, self.stepFrame)
                    self.stop("strideL", "legs")
                else:
                    if self.loop("strideR", "legs", 1.0):
                        self.stop("strideL", "legs")
                        self.stepFrame = self.get_frame('strideR', 'legs')
                        self.carryOverStp = True
            else:#No need to run another check, we know this is the case
                if gotFrame:
                    self.pose('strideL', 'legs', 1, self.stepFrame)
                    self.stop("strideR", "legs")
                else:
                    if self.loop("strideL", "legs", 1.0):
                        self.stop("strideR", "legs")
                        self.stepFrame = self.get_frame('strideL', 'legs')
                        self.carryOverStp = True
                    
        else:
            if not self.stop("strideR", "legs"):
                self.stop("strideL", "legs")
            idleTest += 1            


        if idleTest >= 2:
            self.loop("idle", "legs")
            self.stepFrame = 0
        else:
            self.stop('idle', 'legs')