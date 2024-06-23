from .entModels import playerMdlBase

class playerMdl(playerMdlBase):
    parts = {"torso" : (("base",),("*.hip",)),
             "legs" : (("base",),("abdomen",)),
             "l.arm" : (("l.shoulder",),()),
             "r.arm" : (("r.shoulder",),()),
             "weapon" : (("weapon",),())
             }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        ##Variables
        #Running
        self.stepFrame = 0
        self.carryOverStp = False
        #looking
        self.lookVertical = True#False/0: no animations for looking up or down
        #Animation name holders
        self.idle = None
        self.idleUp = None
        self.idleDown = None
        
        #Initialize animations
        self.set_anim_set("default")
        
    def set_look(self, p: float):
        if self.lookVertical:
            if p > 0:
                scale = p/85
                self.change_blend(self.idle, "torso", 1 - scale)
                self.change_blend(self.idleUp, "torso", scale)
            elif p < 0:
                scale = abs(p/85)
                self.change_blend(self.idle, "torso",  1 - scale)
                self.change_blend(self.idleDown, "torso", scale)
            else:
                self.change_blend(self.idle, "torso", 1)
                self.change_blend(self.idleUp, "torso", 0)
                self.change_blend(self.idleDown, "torso", 0)
            
    def walk(self, x:float, y:float):
        #TODO:: only cause syncwalk at end of function once
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
            

    anim_sets = {
        "default" : {"idle": ("idleDefault","idleDefaultUp","idleDefaultDown"), "run": ("defaultrun",)}
        }
    
    def set_anim_set(self, anim_set):
        self.clear_anim_set()
        animDict = self.anim_sets[anim_set]
        #Idle animations
        if "idle" in animDict.keys():
            if len(animDict["idle"]) == 3:
                self.lookVertical = True
                self.idle = animDict["idle"][0]
                self.idleUp = animDict["idle"][1]
                self.idleDown = animDict["idle"][2]
                first = True
                for anim in animDict["idle"]:
                    self.loop(anim, "torso", 1 if first else 0)
                    first = False
                del first
            elif len(animDict["idle"]) == 1:#We just have one idle with no looking up or down
                self.lookVertical = False
                self.idle = animDict["idle"][0]
                
    def clear_anim_set(self):
        #Idle animations
        if self.idle:
            self.stop(self.idle, "torso")
            self.idle = None
        if self.idleUp:#Can't have idleUp without idleDown, so we do just one check
            self.stop(self.idleUp, "torso")
            self.idleUp = None
            self.stop(self.idleDown, "torso")
            self.idleDown = None