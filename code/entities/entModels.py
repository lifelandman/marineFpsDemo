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