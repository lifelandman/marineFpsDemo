'''
All the "player" classes.
'''

####Player
###panda3d's:
#General:
from panda3d.core import NodePath
#collision:
from panda3d.core import CollisionNode, CollisionBox, CollisionSphere
from panda3d.core import Point3, Vec3
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
        ##TODO::: assign bitmasks to above collisionNodes
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
        
        #physics
        self.velocity = Vec3(0,0,0)
        self._isAirborne = False
        
        self.wBall.show()
        self.bBox.show()
        
    def spawn(self, sPoint: NodePath):
        self.np.reparent_to(base.render)
        self.np.set_pos(sPoint, 0,0,0)
    
    def de_spawn(self):
        self.np.remove_node()#carefull not to lose the class refrence during this time!
        
    def update(self):        
        ##########Part 1: calculate the half-frame change in velocity
        deltaTime = globalClock.get_dt()
        self.velocity_half_update(deltaTime)
        ##########Part 2: Perform Movement calculations
        self.np.set_pos(self.velocity)
        self.np.set_h(self.np, self._hRot)#TODO:: This is insecure against aimhacking.
        self._rig.set_p(self._rig, self._pRot)
        ##########Part 3: calculate the second-half-frame velocity change
        avgRate = globalClock.get_average_frame_rate()#this is a prediction for how long the next frame will be
        self.velocity_half_update(1/avgRate)#divide 1 by avgRate to get estimated next frame time
        #Easy as that, right?
        
    def velocity_half_update(self, scalar):
        '''
        scalar should be deltatime for first half, average frame rate for second
        '''
        if self._isAirborne:#changing z velocity is a bad idea if we're touching the ground.
            self.velocity.add_z(-((9.3*scalar)/2))#Subtract vertical velocity for half a frame. #TODO:: if you want weight modifiers, add them here.
            
        speedLimit = 20#maximum horizontal speed
        walkAccel = 2#acceleration while walking per second
        airAccel = 0.3#acceleration while in air per second
        #X velosity calculations
        if self._xMove != 0:
            if not self._isAirborne and abs(self.velocity.get_x()) > 20:
                self.velocity.add_x((self._xMove*walkAccel*scalar)/2)
            elif self._isAirborne:#note we don't cap velocity while in air
                self.velocity.add_x((self._xMove*airAccel*scalar)/2)
        if abs(self.velocity.get_x()) > 20:
            val = self.velocity.get_x()
            self.velocity.set_x(20*(val/abs(val)))#cap velocity at abs 20
            del val
        #Y velosity calculations
        if self._yMove != 0:
            if not self._isAirborne and abs(self.velocity.get_y()) > 20:
                self.velocity.add_y((self._yMove*walkAccel*scalar)/2)
            elif self._isAirborne:#note we don't cap velocity while in air
                self.velocity.add_y((self._yMove*airAccel*scalar)/2)
        if abs(self.velocity.get_y()) > 20:
            val = self.velocity.get_y()
            self.velocity.set_y(20*(val/abs(val)))#cap velocity at abs 20
            del val
        
    def interrogate(self):
        pass
        'serialize the variables'


from panda3d.core import ConfigVariableString
class clientPlayer(playerEnt):
    def __init__(self, camera, **kwargs):
        super().__init__(**kwargs)
        self.camera = camera#See spawn and de_spawn below.
        
        
    def spawn(self, sPoint: NodePath):
        super().spawn(sPoint)
        self.camera.reparent_to(self._rig)#If the camera isn't connected to the same node tree as geometry, geometry won't render. It'd be awkward to have even a moment where the camera is rendering a blank, so we detatch it here.
        self.camera.set_pos_hpr(0,0,0,0,0,0)
        self.addTask(self.get_inputs_keys, 'key-input task', sort =5)#it's awkward that we're controlling tasks like this and not through the entity system that was made for this purpose, but because players will spawn and despawn frequently
        self.addTask(self.update, 'client_mover', sort = 10)#We have no choice but to do this so as to lighten the frame-time when the client player isn't spawned.
    
    def de_spawn(self):
        super().de_spawn()
        self.camera.reparent_to(base.render)
        self.removeAllTasks()#NOTE:: If we add tasks that do persist when not spawned, we need to get rid of this and do it manually.
    
    #Defining button inputs as member variables. (same among all instances.)
    #They are then redefined inside a function to update them once the game starts. (if we set the keybind strings in the member declarations, they will be set immediately as the file is imported and unchanged if the user changes the keybinds.)
    #If splitscreen multiplayer ever becomes important for some reason, these need to be changed to instance variables.
    key_for = None
    key_bak = None
    key_left = None
    key_right = None
    key_jump = None
    key_crouch = None
    def update_keybinds(self):
        self.key_for = ConfigVariableString('move-forward', 'w').get_string_value()
        self.key_bak = ConfigVariableString('move-backward', 's').get_string_value()
        self.key_left = ConfigVariableString('move-left', 'arrow_left').get_string_value()
        self.key_right = ConfigVariableString('move-right', 'arrow_right').get_string_value()
        self.key_jump = ConfigVariableString('jump', 'space').get_string_value()
        self.key_crouch = ConfigVariableString('crouch', 'shift').get_string_value()
    
    
    
    def get_inputs_keys(self):#We need a diffrent function if we ever want to add controller support
        poller = base.mouseWatcherNode
        self._xMove = poller.is_button_down(self.key_for) - poller.is_button_down(self.key_bak)
        self._yMove = poller.is_button_down(self.key_right) - poller.is_button_down(self.key_left)
        self._wantJump = poller.is_button_down(self.key_jump)
        self._wantCrouch = poller.is_button_down(self.key_crouch)
        
        if base.mouseWatcherNode.hasMouse():#Get mouse movement
            self._hRot, self._pRot = base.mouseWatcherNode.getMouseX(), base.mouseWatcherNode.getMouseY()
    

class networkedPlayer(playerEnt):
    pass