'''
This file should contain all entity classes relating purely to models and operations therof. (actors tbd)

is is advised to avoid using pure model entities outside of subclassing, as there is a potential performance loss when using them instead of a 'func' entity or applying effects directly onto a modelNode nodePath.
'''

from .npEnt import npEnt

class modelEnt (npEnt):
    '''
    this is the worst option to use instead of just a modelNode.
    All this does is extend npEnt's behavior to give an entity a refrence to a model. That model WILL be put into the scene graph at the np argument.
    so in the rare instance you need a model but not for geometry purposes, make your own damn class.
    edit: I guess this bugfix changes that, so.... when the np parameter isn't provided, we just hold onto the np without a parent...
    WARNING WARNING WARNING: we cannot safely unload models from within entities, so be sure to call panda3d.core.ModelPool.garbage_collect() elsewhere when nessisary!!!!! (scene transitions, closing game world class)
    '''
    npOursOverrideable = True
    
    modelPath = 'box'
    
    
    def __init__(self, np, pos = (0,0,0), **kwargs):
        mnp = loader.loadModel(self.modelPath)
        if np != None:
            mnp.reparent_to(np)#We hijack the np parameter and use it as our parent
        mnp.set_pos(*pos)
        kwargs['np'] = mnp
        super().__init__(**kwargs)#Trick npEnt into holding the root of our model
        


class modelInstanceEnt (npEnt):
    '''
    ditto to above, but for entities that can share a single instance of a model amongst themselves, and actually doesn't function if np is None.
    TODO:: see if this actually works with inheritance. we might need to add the model and refCount members with each derivative.
    '''
    npOursOverrideable = True
    
    modelPath = 'box'
    model = None#We may have to put new model and refCount member variables for each derivative of this.
    refCount = 0#it's only two lines, but it's annoying.
    
    def __init__(self, np, pos = (0,0,0), **kwargs):
        if np == None:
            return
        
        if self.model == None:#Load the model only when it's in use
            self.model = loader.loadModel(self.modelPath)
        mnp = self.model.instance_to(np)
        mnp.set_pos(*pos)
        self.refCount += 1
        super().__init__(np = mnp, **kwargs)#Trick npEnt into holding the root of our model
        
    def destroy(self):
        self.refCount -= 1
        if self.refCount <= 0:#
            self.refCount = 0
            self.model = None
        super().destroy()
        

from .funcs import funcSpin
class spinningModel(modelInstanceEnt, funcSpin):
    pass


##BIIG STUFF. BIG BIG BIG!!!

from panda3d.core import LoaderOptions, Character, PartSubset, AnimControlCollection, BitMask32
'''
Okay, here's a refrence of stuff:
Character: the node that holds the geometry, and updates the animation
PartSubset: we can use this to define part of the character we want to control independantly
AnimControl: The class that controlls the animation.
auto_bind: creates AnimControls for all parts for all visible animations inside the egg file
'''
class playerMdlBase(npEnt):
    modelLoadOps = LoaderOptions(LoaderOptions.LF_search | LoaderOptions.LF_report_errors | LoaderOptions.LF_convert_skeleton)
    
    parts = {}#partname: ((include part names), (exclude part names))
    
    blendMode = 1#BT_normalized_linear
    
    npOursOverrideable = True
    
    modelPath = 'newplayer'
    
    def __init__(self, np, pos = (0,0,0), **kwargs):
        mnp = loader.loadModel(self.modelPath, self.modelLoadOps)
        if np != None:
            mnp.reparent_to(np)#We hijack the np parameter and use it as our parent
        self.character = mnp.find("**/+Character")
        self.bundle = self.character.node().get_bundle(0)
        self.bundle.set_blend_type(self.blendMode)
        self.bundle.set_anim_blend_flag(True)
        self.bundle.set_frame_blend_flag(True)
        mnp.set_pos(*pos)
        super().__init__(np = mnp, **kwargs)#Trick npEnt into holding the root of our model
        
        #Character stuff
        self.controls = {"modelRoot" : AnimControlCollection()}
        for anim in self.np.find_all_matches("**/+AnimBundleNode"):
            self.controls["modelRoot"].store_anim(self.bundle.bind_anim(anim.node().get_bundle(), 0x01 | 0x02 | 0x04), anim.node().get_bundle().get_name())
        

        if len(self.parts) >= 1:#Are there subparts? if so, we need to make controls for those.
            for part in self.parts.keys():
                partCont = AnimControlCollection()
                for anim in self.np.find_all_matches("**/+AnimBundleNode"):
                    sPart = PartSubset()
                    for include in self.parts[part][0]:
                        sPart.add_include_joint(include)
                    for exclude in self.parts[part][1]:
                        sPart.add_exclude_joint(exclude)
                    partCont.store_anim(self.bundle.bind_anim(anim.node().get_bundle(), 0x01 | 0x02 | 0x04, sPart), anim.node().get_bundle().get_name())
                self.controls[part] = partCont#Store the new animControlCollection under the name of the part
                

        self.boneBoxes = []
        for nodeP in self.np.find_all_matches("**/+CollisionNode"):
            nodeP.show()
            if nodeP.has_tag("boneBox"):
                joint = self.character.node().find_joint(nodeP.get_tag("boneBox"))
                if joint:
                    joint.add_net_transform(nodeP.node())
                    nodeP.set_p(90)
                nodeP.node().set_from_collide_mask(BitMask32(0b0000000))
                nodeP.node().set_into_collide_mask(BitMask32(0b0001000))
                nodeP.node().modify_solid(0).set_tangible(False)
                del joint
                self.boneBoxes.append(nodeP.node())


    def play(self, name:str, part:str = "modelRoot", blend:float = 1, start:int = None):
        control = self.controls[part].find_anim(name)
        if not control.is_playing():
            if not start:
                control.play()
            else:
                control.play(start, control.get_num_frames()-1)
            self.check_blend(control, blend)
            return True
        elif not self.check_blend(control, blend):
            return False
        return True
    
    def loop(self, name:str, part:str = "modelRoot", blend:float = 1, start:int = None):
        control = self.controls[part].find_anim(name)
        if not control.is_playing():
            if not start:
                control.loop(True)
            else:
                control.pose(start)
                control.loop(False)
            self.check_blend(control, blend)
            return True
        elif not self.check_blend(control, blend):
            return False
        return True
    
    def stop(self, name:str, part:str = "modelRoot"):
        control = self.controls[part].find_anim(name)
        if control.is_playing() or control.get_num_frames() == 1:
            control.stop()
            self.bundle.set_control_effect(control, 0)
            return True
        else: return False
        
    def pose(self, name:str, part:str = "modelRoot", blend:float = 1.0, frame:float = 0.0):
        control = self.controls[part].find_anim(name)
        if control.is_playing():
            control.stop()
        control.pose(frame)
        self.check_blend(control, blend)
        return True
    
    def stop_all(self):
        for animConCol in self.controls.items():
            animConCol.stop_all()
            
    def change_blend(self, name:str, part:str, blend:float):
        control = self.controls[part].find_anim(name)
        return self.check_blend(control, blend)
            
    def check_blend(self, control, blend):
        if blend != self.bundle.get_control_effect(control):
            self.bundle.set_control_effect(control, blend)
            return True
        return False
    
    def get_frame(self, name:str, part:str):
        control = self.controls[part].find_anim(name)
        return control.get_frame()
    
    def get_available_frame(self, part:str, *animNames):
        val = 0
        for animName in animNames:
            if self.is_playing(animName, part):
                val = self.get_frame(animName, part)
                break
        return val
    
    def is_playing(self, name:str, part:str):#this is for higher level animation code
        control = self.controls[part].find_anim(name)
        return control.is_playing()
    

    def destroy(self):
        for key in self.controls.keys():
            cont = self.controls[key]
            cont.stop_all()
        del self.controls
        
        for node in self.boneBoxes:
            node.clear_effects()
        del self.boneBoxes
        
        self.character.remove_node()
        super().destroy()