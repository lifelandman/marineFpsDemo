from .entModels import playerMdlBase

class playerMdl(playerMdlBase):
    parts = {"torso" : (("base",),("*.hip", "*.ikfoot")),
             "legs" : (("base","*.toes", "*.ikfoot"),("abdomen","weapon")),
             "l.arm" : (("l.shoulder",),()),
             "r.arm" : (("r.shoulder","weapon"),()),
             "weapon" : (("weapon",),())
             }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        ##Variables
        #Running
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
        
        scaleX = abs(x)
        scaleY = abs(y)
        totScale = scaleX+scaleY
        if totScale > 1:
            scaleX = scaleX/totScale
            scaleY = scaleY/totScale
        del totScale
        
        gotFrame = False
        
        if y != 0:
            if y > 0:
                if self.loop("run", "legs", scaleY):
                    self.stop("backrun", "legs")
                    self.stepFrame = self.get_frame('run', 'legs')
            else:#No need to run another check, we know this is the case
                if self.loop("backrun", "legs", scaleY):
                    self.stop("run", "legs")

        else:
            if not self.stop("run", "legs"):
                self.stop("backrun", "legs")
            idleTest += 1
            
        
        if x != 0:
            if x > 0:
                if self.is_playing("run", "legs") or self.is_playing("backrun", "legs"):
                    self.loop('strafeR', 'legs', scaleX, self.get_available_frame("legs", "run", "backrun"))
                    self.stop("strafeL", "legs")
                else:
                    if self.loop("strafeR", "legs", scaleX):
                        self.stop("strafeL", "legs")
            else:#No need to run another check, we know this is the case
                if self.is_playing("run", "legs") or self.is_playing("backrun", "legs"):
                    self.loop('strafeL', 'legs', scaleX, self.get_available_frame("legs", "run", "backrun"))
                    self.stop("strafeR", "legs")
                else:
                    if self.loop("strafeL", "legs", scaleX):
                        self.stop("strafeR", "legs")
                    
        else:
            if not self.stop("strafeR", "legs"):
                self.stop("strafeL", "legs")
            idleTest += 1            


        if idleTest >= 2:
            self.loop("idleDefault", "legs")
        else:
            self.stop('idleDefault', 'legs')
            

    anim_sets = {
        "default" : {"idle": ("idleDefault","idleDefaultUp","idleDefaultDown"), "run": ("defaultrun","defaultbackrun")}
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