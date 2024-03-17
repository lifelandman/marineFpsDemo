from .entModels import playerMdlBase

class playerMdl(playerMdlBase):
    parts = {"torso" : (("Diaphram",),("*.thigh",)),
             "legs" : (("R.thigh", "L.thigh"),())}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loop("idle","torso", 1)
        self.loop("LookUp", "torso", 0)
        self.loop("idle", "legs", 1)
        
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
        if not x == 0:
            if x > 0:
                self.loop("strideR", "legs", x/scale)
                self.stop("strideL", "legs")
            else:#No need to run another check, we know this is the case
                self.loop("strideL", "legs", x/scale)
                self.stop("strideR", "legs")
        else:
            if not self.stop("strideR", "legs"):
                self.stop("strideL", "legs")
            
        if not y == 0:
            if y > 0:
                self.loop("run", "legs", y/scale)
                self.stop("backRun", "legs")
            else:#No need to run another check, we know this is the case
                self.loop("backRun", "legs", y/scale)
                self.stop("run", "legs")
        else:
            if not self.stop("run", "legs"):
                self.stop("backRun", "legs")