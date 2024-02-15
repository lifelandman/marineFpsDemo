'''
All the "player" classes.
'''

####Player
#panda3d's:
from panda3d.core import CollisionNode, CollisionBox, CollisionSphere
from panda3d.core import Point3
#ours:
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
        
        self.wBall.show()
        self.bBox.show()
        "we create some instance variables used to calculate movement"
        
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