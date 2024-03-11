
'''
This file contains an entity class that serves to hold a refrence to a nodePath.
If we are not given a nodePath, then we create one ourselves.
we create and destroy a pythonTag on that nodePath to maintain a link to our entity for things such as collision logic. (i.e. source engines 'use', so that if use hits a valid object we trigger ent.use or something like that)

at the time of writing, this is in it's own file because it is reasonable to believe that this can be split down 'func' entities that enact an operation on a standard nodePath and model entities.
'''

from panda3d.core import NodePath
from .entBase import entNamable

class npEnt (entNamable):
    
    npOursOverrideable = False#does a subclass of this expect to pass down actually recieved level geometry or a configured model?
    skipAccept = False#Do we even care about any nodepath we were given?
    
    def __init__ (self, np: NodePath = None, **kwargs):
        super().__init__(**kwargs)
        
        if (not self.skipAccept) and np != None:
            self.np = np
            self.npOurs = self.npOursOverrideable#Do we own the np or was it given to us
        else:
            self.np = NodePath(self.name)
            self.npOurs = True#elaborating on above, if this isn't ours it must belong to level geometry or something like that.
            
        self.np.set_python_tag('entOwner', self)#NOTE!!! we cannot have multiple npEnts acting on one np!!!
        

    def destroy(self):
        super().destroy()
        self.np.clear_python_tag('entOwner')
        if self.npOurs:
            self.np.remove_node()
        