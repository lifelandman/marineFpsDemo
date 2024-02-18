'''
All the "player" classes.
'''

####Player
###panda3d's:
#General:
from panda3d.core import NodePath
#collision:
from panda3d.core import CollisionNode, CollisionBox, CollisionSphere
from panda3d.core import Point3
#Bullet raytracing:
from panda3d.core import LensNode, PerspectiveLens
###ours:
from .npEnt import npEnt

class playerEnt(npEnt):
    
    skipAccept = True#we don't accept geometry.
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)#make self.np
        
        #Create bounding box
        cNode = CollisionNode(self.name + '_bounding_box')
        cNode.add_solid(CollisionBox(Point3(0,0,0), 1,1,2))
        self.bBox = self.np.attach_new_node(cNode)
        del cNode
        
        #Create water ball
        cNode = CollisionNode(self.name + '_water_ball')
        cNode.add_solid(CollisionSphere(0,0,0,0.2))
        self.wBall = self.np.attach_new_node(cNode)
        del cNode
        
        #Create bullet LensNode.
        '''
        Panda3d let's you extrude vectors from a lens based on coordinates. we can use this to calculate bullet raycasting vectors. 
        '''
        self._rig = NodePath(self.name + "_rig")#this is the axis of pitch rotation for both the raycast LensNode and the camera. We don't just parent the camera to the LensNode because we might want an offset for the bullet origin.
        self._rig.reparent_to(self.np)
        self._rig.set_z(0.9)

        self._bulletNode = LensNode(self.name + "_bulletLens", PerspectiveLens())#Weapons will modify these properties when they're set active.
        self._bulletLens = self._bulletNode.get_lens()
        
        ################Create all instance variables##############
        
        #Administrative/anti-cheat
        self.teleportOk = False#Set this to true if and whenever velosity's big enough or we're teleporting somewhere. If not this and this player moved too far, it's possible that client is trying to lie about present location.
        
        #Movement
        self._xMove = 0.0 #float for relatively left/right movement.
        self._yMove = 0.0 #ditto, but for forward/back
        
        self._wantJump = False#does this player object want to jump whenever such an action is valid?
        self._wantCrouch = False#will we even use this right away?
        
        self._hRot = 0.0 #amount of heading rotation. If we're doing mouse/keys, this is how far along the x axis from the center user has moved cursor.
        self._pRot = 0.0 #pitch rotation. (looking up/down.)
        
        self.wBall.show()
        self.bBox.show()
        
    def spawn(self, sPoint: NodePath):
        self.np.reparent_to(base.render)
        self.np.set_pos(sPoint, 0,0,0)
    
    def de_spawn(self):
        self.np.remove_node()#carefull not to lose the class refrence during this time!
        
    def update(self):
        pass
        'move the nodepath'
        
    def interrogate(self):
        pass
        'serialize the variables'



'''
class clientPlayer():
    tasks = (('update'),
             ('calcMoveVariabes'))
    'write those two functions'
    

class networkedPlayer():
    events = ('...')#update the variables
    def updateVariable(self):
        #update variable
        self.recievedVariable = True
        
    def update(self):
        if self.recievedVariable:
            pass#teleport
        else:
            super().update()
'''