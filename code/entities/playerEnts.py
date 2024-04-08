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
from panda3d.core import BitMask32
#Bullet raytracing:
from panda3d.core import LensNode, PerspectiveLens
#Rotation
from panda3d.core import Quat
#Tasks:
from direct.task import Task
###Math:
from math import copysign, sqrt, isclose
###ours:
from .npEnt import npEnt
from .playerModel import playerMdl
from ..weapons.wpnSlots import slotMgr
from ..weapons.wpnTrgr import trgrTest, waitTest

class playerEnt(npEnt):
    
    skipAccept = True#we don't accept geometry.
    
    ##################
    #Creation Methods#
    ##################
    def __init__(self, **kwargs):
        super().__init__(**kwargs)#make self.np
        self.np.set_collide_mask(BitMask32(0b0010000))
        self.np.set_tag('player', self.name)
        #accept collision events
        self.accept(self.name + "-into-ground", self.tangible_collide_into_event)
        self.accept(self.name + "-out-ground", self.tangible_collide_out_event)
        self.accept(self.name + "-again-ground", self.tangible_collide_again_event)

        #Create bounding box
        cNode = CollisionNode(self.name + '_bounding_box')
        self.bBSolids = (CollisionBox(Point3(0,0,0), 1,1,2), CollisionBox(Point3(0,0,-1), 1,1,1))#Diffrent collisionSolids for cNode, 0=normal, 1=crouch, 2=fastSwm
        cNode.add_solid(self.bBSolids[0])
        cNode.set_from_collide_mask(BitMask32(0b1010101))#TODO:: change this later to have team collision setting
        self.bBox = self.np.attach_new_node(cNode)
        self.bBox.set_tag('bBox', 't')
        del cNode
        
        #Create water ball
        cNode = CollisionNode(self.name + '_water_ball')
        orb = CollisionSphere(0,0,0,0.2)
        orb.set_tangible(False)#For some reason python complains when we set tangible after adding orb as a solid
        cNode.add_solid(orb)
        del orb
        cNode.set_from_collide_mask(BitMask32(0b0100000))
        self.wBall = self.np.attach_new_node(cNode)
        self.wBall.set_collide_mask(BitMask32(0b0000000))#No into collisions
        del cNode
        ##TODO::: assign bitmasks to above collisionNodes
        
        #Create Model
        self.model = playerMdl(np = self.np, pos = (0,0,-2))
        self.model.np.set_h(180)#I'm doing some alterations here because I'm testing with a model not made for this project
        
        #######WEAPONS#######
        #Create bullet LensNode.
        '''
        Panda3d let's you extrude vectors from a lens based on coordinates. we can use this to calculate bullet raycasting vectors. 
        '''
        self._rig = NodePath(self.name + "_rig")#this is the axis of pitch rotation for both the raycast LensNode and the camera. We don't just parent the camera to the LensNode because we might want an offset for the bullet origin.
        self._rig.reparent_to(self.np)
        self._rig.set_z(0.9)
        m = loader.loadModel('jack')
        m.reparent_to(self._rig)
        m.set_scale(0.5)

        self._bulletNode = LensNode(self.name + "_bulletLens", PerspectiveLens())#Weapons will modify these properties when they're set active.
        self._bulletLens = self._bulletNode.get_lens()
        
        #Create wpnManager
        self.wpnMgr = slotMgr(self.name)
        self.wpnMgr.add_weapon(trgrTest(user = self))
        self.wpnMgr.add_weapon(waitTest(user = self))
        
        #weapon variables
        self._wpnFire = 0#This tells the interogate function if we've fired on this frame and which fire func we used. Also tells clientPlayer to fire
        self._changeWpn = False#Tells interogate function that it needs to serialize a change in selected weapon
        
        ################Create all instance variables##############
        
        #Administrative/anti-cheat
        #self.teleportOk = False#Set this to true if and whenever velosity's big enough or we're teleporting somewhere. If not this and this player moved too far, it's possible that client is trying to lie about present location.
        
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
        #self.bBox.show()
        
        #bBox
        self._inCrouch = False#Are we doing the crouching animation?
        self._isCrouched = False
        self._swmFst = False
    
    def add_colliders(self, trav, handler):
        trav.add_collider(self.bBox, handler)
        handler.add_collider(self.bBox, self.np)
        trav.add_collider(self.wBall, handler)
        handler.add_collider(self.wBall, self.np)
        
    ##########
    #Spawning#
    ##########
        
    def spawn(self, sPoint: NodePath):
        self.np.reparent_to(base.render)
        self.np.set_pos(sPoint, 0,0,0)
        self.np.set_h(sPoint, 0)
        self._isAirborne = True
    
    def de_spawn(self):
        self.np.detach_node()#carefull not to lose the class refrence during this time!
        
    ##################
    #Movement Methods#
    ##################
    
    upVec = Vec3(0,0,1)#standard up vector
        
    def update(self, task = None):
        ##########Part 1: calculate the half-frame change in velocity
        deltaTime = globalClock.get_dt()
        self.velocity_half_update(deltaTime)
        ##########Part 2: Perform Movement calculations
        self.np.set_pos(self.np, self.velocity)
        
        ##Calculate rotation
        self.np.set_h(self.np, self._hRot)#TODO:: This is insecure against aimhacking.
        #Rotate velocity
        turn = Quat()
        turn.set_from_axis_angle(-self._hRot, self.upVec)
        self.velocity = Vec3(turn.xform(self.velocity))
        #Calculate pitch
        if (self._pRot != 0) and (abs(self._rig.get_p() + self._pRot) <= 85):
            self._rig.set_p(self._rig, self._pRot)
            
        ##Crouch
        if self._wantCrouch and not (self._isCrouched or self._inCrouch):
            if self._isAirborne:
                self.crouch()
            else:
                self.addTask(self.inCrouchTask, "crouchTask")
                self._inCrouch = True
        elif self._isCrouched and not self._wantCrouch:
            self.uncrouch()
        
        
        #animations
        self.model.set_look(self._rig.get_p())
        self.model.walk(self._xMove, self._yMove)
        
        ##########Part 3: calculate the second-half-frame velocity change
        avgRate = globalClock.get_average_frame_rate()#this is a prediction for how long the next frame will be
        self.velocity_half_update(1/avgRate)#divide 1 by avgRate to get estimated next frame time
        #Easy as that, right?
        if task:
            return Task.cont
        
        
    def velocity_half_update(self, scalar):
        '''
        scalar should be deltatime for first half, average frame rate for second
        '''
        if self._isAirborne:#changing z velocity is a bad idea if we're touching the ground.
            self.velocity.add_z(-((8*scalar)/2))#Subtract vertical velocity for half a frame. #TODO:: if you want weight modifiers, add them here.#8 is gravity
        elif self._wantJump:
            self.velocity.add_z(sqrt(3)/2)
            
        speedLimit = 20#maximum horizontal speed
        walkAccel = 2#acceleration while walking per second
        airAccel = 0.5#acceleration while in air per second
        friction = 0.85#deceleration/acceleration resistance per second. If velocity in a direction is less than this, velocity is stopped in a short period of time
        
        ##Adjust values
        if not (self._yMove or self._xMove): friction *= 2
        exceedControlSpeed = self.velocity.get_xy().length() < 10
        #Y velosity calculations
        if self._yMove != 0:
            if not self._isAirborne and exceedControlSpeed:
                if abs(self.velocity.get_y() + self._yMove) < abs(self.velocity.get_y()):
                    self.velocity.add_y(copysign(min(abs(self.velocity.get_y()), 10), self._yMove)/2)#instantly reverse momentum
                else:
                    self.velocity.add_y((self._yMove*walkAccel*scalar)/2)
            elif self._isAirborne:#note we don't cap velocity while in air
                self.velocity.add_y((self._yMove*airAccel*scalar)/2)
        if abs(self.velocity.get_y()) > 20:
            val = self.velocity.get_y()
            self.velocity.set_y(copysign(20, val))#cap velocity at abs 20
            del val
        if not self._isAirborne:#extra stuff for only on the ground
            if abs(self.velocity.get_y()) > 0.2:#Add friction
                self.velocity.add_y(-copysign(friction, self.velocity.get_y())*scalar / 2)
            elif not self._yMove and self.velocity.get_y() != 0:
                self.velocity.set_y(0)
                
        #X velosity calculations
        if self._xMove != 0:
            if not self._isAirborne and exceedControlSpeed:
                if abs(self.velocity.get_x() + self._xMove) < abs(self.velocity.get_x()):
                    self.velocity.add_x(copysign(min(abs(self.velocity.get_x()), 10), self._xMove)/2)
                else:
                    self.velocity.add_x((self._xMove*walkAccel*scalar)/2)
            elif self._isAirborne:#note we don't cap velocity while in air
                self.velocity.add_x((self._xMove*airAccel*scalar)/2)
        if abs(self.velocity.get_x()) > 20:
            val = self.velocity.get_x()
            self.velocity.set_x(copysign(20, val))#cap velocity at abs 20
            del val
        if not self._isAirborne:#extra stuff for only on the ground
            if abs(self.velocity.get_x()) > 0.2:#Add friction
                self.velocity.add_x(-copysign(friction, self.velocity.get_x())*scalar / 2)
            elif not self._xMove and self.velocity.get_x() != 0:
                self.velocity.set_x(0)
                
    ##############
    #BBox changes#
    ##############
    
    def inCrouchTask(self, taskobj):
        time = taskobj.time
        if self._isAirborne or self._isCrouched or time >= 0.35:
            self._inCrouch = False
            self.crouch()
            return Task.done
        elif not self._wantCrouch:
            self.uncrouch()
            self._inCrouch = False
            return Task.done
        self._rig.set_z(-0.1 + (1- (time/0.35)))
        return Task.cont
        
    
    def crouch(self):
        self.bBox.node().set_solid(0,self.bBSolids[1])
        self._rig.set_z(-0.1)
        if self._isAirborne:
            self.np.set_z(self.np, 1)
        self._isCrouched = True
            
    def uncrouch(self):
        self.bBox.node().set_solid(0,self.bBSolids[0])
        self._rig.set_z(0.9)
        if self._isAirborne:
            self.np.set_z(self.np, -1)
        self._isCrouched = False
            
    ########
    #Events#
    ########
            
    def tangible_collide_into_event(self, entry):
        vector = entry.get_surface_normal(entry.get_from_node_path())#WARNING!! Unapplied rotation transforms like to fuck with this!#TODO:: Figure out what I meant from this.
        if vector.get_z() > 0.6:#(Above comment is copied from code from other project.)
            self._isAirborne = False
        #TODO:: negate velocity if we run into a wall.
        
    def tangible_collide_again_event(self, entry):
        vector = entry.get_surface_normal(entry.get_from_node_path())
        if self._isAirborne:
            if vector.get_z() > 0.6:
                self._isAirborne = False
        self.bend_velocity(vector)
                
    def bend_velocity(self, vector):
        if self.velocity.length() <= 0.0001:
            return
        veloVec = self.velocity.normalized()
        angle = veloVec.angle_deg(vector)
        if vector.get_z() > 0.93:
            self.velocity.set_z(0)
        if angle >= 1:
            norDot = vector.dot(self.velocity)
            mod = Vec3(vector)
            mod *= norDot
            self.velocity -= mod
    
    def tangible_collide_out_event(self, entry):
        self._isAirborne = True
        
    def fire(self, fireVal):
        if fireVal == 1: messenger.send(self.name + "-fire1")
        elif fireVal == 2: messenger.send(self.name + "-fire2")#Inconsistent with elsewhere, but we arn't checking if fireVal is 0 here.
        
    ####################
    #Management Methods#
    ####################        
        
    def interrogate(self, server):
        server.add_message("playData{" + self.name, ((self._yMove, self._xMove,
                                          self._wantJump, self._wantCrouch,
                                          self._hRot, self._pRot,
                                          self.velocity.get_x(), self.velocity.get_y(), self.velocity.get_z(),
                                          self.np.get_h(), self._rig.get_p(), self.np.get_x(), self.np.get_y(), self.np.get_z(),
                                          self._isAirborne, self._isCrouched),))
        
        if self._changeWpn:
            slot = 0
            subSlot = 0
            self.wpnMgr.get_slots(slot, subSlot)
            #print(slot)
            server.add_message("changeWpn{" + self.name, (slot, subSlot,))
            self._changeWpn = False
        
        if self._wpnFire:
            server.add_message("fire{" + self.name, (self._wpnFire,))
            self._wpnFire = 0#This is a double redundancy for clientPlayer, but we need this here for hostNetPlayer, or else it won't get serialized to clients
    

    def destroy(self):
        self.de_spawn()
        self.model.destroy()
        super().destroy()


from panda3d.core import ConfigVariableString
from panda3d.core import WindowProperties
class clientPlayer(playerEnt):
    
    over = False#cheap hack to save a logic check in playerMgr

    def __init__(self, camera, **kwargs):
        super().__init__(**kwargs)
        self.camera = camera#See spawn and de_spawn below.
        self._inputActive = False
        self.accept(self.key_pause, self.toggle_inputs)#GRahhh! should player classes even be entities?
        self.accept("expectOveride", self.oRTrig)
        
        #unique graphical stuff
        self.model.np.hide()
        
    def oRTrig(self):#override trigger
        self.acceptOnce('playData{' + self.name, self.storeProps)
        
    def storeProps(self, val):
        self.velocity.set_x(val[6])
        self.velocity.set_y(val[7])
        self.velocity.set_z(val[8])
        if not isclose(self._rig.get_h(), val[9], rel_tol = 1) :self.np.set_h(val[9])
        if not isclose(self._rig.get_p(), val[10], rel_tol = 1) :self._rig.set_p(val[10])
        self.np.set_pos(val[11],val[12],val[13],)
        self._isAirborne = val[14]
        self._isCrouched = val[15]
        
    def toggle_inputs(self):
        if self._inputActive:
             self.removeTask('key-input task')
             
             props = WindowProperties()
             props.set_cursor_hidden(False)
             '''
             props.set_mouse_mode(WindowProperties.M_relative)#These don't work on windows. TODO:: detect if we're on a os that can do this, and use these instead.
             '''
             base.win.requestProperties(props)
             

             self.ignore(self.key_wpnUp)
             self.ignore(self.key_wpnDown)
             
             
             self._inputActive = False
        else:
            self.addTask(self.get_inputs_keys, 'key-input task', sort =5)#it's awkward that we're controlling tasks like this and not through the entity system that was made for this purpose, but because players will spawn and despawn frequently
            
            props = WindowProperties()#See above.
            props.set_cursor_hidden(True)
            '''
            props.set_mouse_mode(WindowProperties.M_absolute)#see above.
            '''
            base.win.requestProperties(props)
            
            self.accept(self.key_wpnUp, self.changeWpn, [1,])
            self.accept(self.key_wpnDown, self.changeWpn, [-1,])
            
            
            self._inputActive = True
    
    def spawn(self, sPoint: NodePath):
        super().spawn(sPoint)
        self.camera.reparent_to(self._rig)#If the camera isn't connected to the same node tree as geometry, geometry won't render. It'd be awkward to have even a moment where the camera is rendering a blank, so we detatch it here.
        self.camera.set_pos_hpr(0,0,0,0,0,0)
        self.addTask(self.update, 'client_mover', sort = 10)#We have no choice but to do this so as to lighten the frame-time when the client player isn't spawned.
        self.toggle_inputs()
        
    
    def de_spawn(self):
        super().de_spawn()
        self.camera.reparent_to(base.render)
        self.removeAllTasks()#Carefull!
    
    #Defining button inputs as member variables. (same among all instances.)
    #They are then redefined inside a function to update them once the game starts. (if we set the keybind strings in the member declarations, they will be set immediately as the file is imported and unchanged if the user changes the keybinds.)
    #If splitscreen multiplayer ever becomes important for some reason, these need to be changed to instance variables.
    key_for = None
    key_bak = None
    key_left = None
    key_right = None
    
    key_jump = None
    key_crouch = None
    
    key_pause = None
    
    key_fire1 = None
    key_fire2 = None
    
    key_wpnUp = None
    key_wpnDown = None
    def update_keybinds(self):
        self.key_for = ConfigVariableString('move-forward', 'w').get_string_value()
        self.key_bak = ConfigVariableString('move-backward', 's').get_string_value()
        self.key_left = ConfigVariableString('move-left', 'a').get_string_value()
        self.key_right = ConfigVariableString('move-right', 'd').get_string_value()
        
        self.key_jump = ConfigVariableString('jump', 'space').get_string_value()
        self.key_crouch = ConfigVariableString('crouch', 'shift').get_string_value()
        
        self.key_pause = ConfigVariableString('pause', 'escape').get_string_value()
        
        self.key_fire1 = ConfigVariableString('fire1', 'mouse1').get_string_value()
        self.key_fire2 = ConfigVariableString('fire2', 'mouse3').get_string_value()
        
        self.key_wpnUp = ConfigVariableString('changeWpn-up', 'wheel_up').get_string_value()
        self.key_wpnDown = ConfigVariableString('changeWpn-down', 'wheel_down').get_string_value()
    
    
    
    def get_inputs_keys(self, task):#We need a diffrent function if we ever want to add controller support
        poller = base.mouseWatcherNode
        self._yMove = poller.is_button_down(self.key_for) - poller.is_button_down(self.key_bak)
        self._xMove = poller.is_button_down(self.key_right) - poller.is_button_down(self.key_left)
        self._wantJump = poller.is_button_down(self.key_jump)
        self._wantCrouch = poller.is_button_down(self.key_crouch)
        
        if poller.is_button_down(self.key_fire1): self._wpnFire = 1
        elif poller.is_button_down(self.key_fire2): self._wpnFire = 2
        else: self._wpnFire = 0
        
        if poller.is_button_down(self.key_wpnUp):
            self.wpnMgr.change_weapon(1)
            self._changeWpn = True
        elif poller.is_button_down(self.key_wpnDown):
            self.wpnMgr.change_weapon(-1)
            self._changeWpn = True
        
        pointer = base.win.get_pointer(0)
        if pointer.get_in_window():#Get mouse movement
            scSize = base.win.getProperties()
            xSize, ySize = scSize.get_x_size() // 2, scSize.get_y_size() // 2
            self._hRot, self._pRot = -((pointer.get_x() - xSize) // 3) * 0.7, -((pointer.get_y() - ySize) // 3) * 0.7
            base.win.movePointer(0, xSize, ySize)
        else: self._hRot, self._pRot = 0,0
        return Task.cont
    

    def changeWpn(self, val):
        self.wpnMgr.change_weapon(val)
        self._changeWpn = True
        
    
    def update(self, task = None):#TODO:: add a function inside slotMgr that checks if active weapon is a triggerWpn
        if self._wpnFire:
            self.fire(self._wpnFire)
        return super().update(task)
    
    def destroy(self):
        if self._inputActive:
            self.toggle_inputs()
        #self.ignoreAll()
        super().destroy()
    

class hostNetPlayer(playerEnt):#(player._yMove, _xMove, _wantJump, _wantCrouch, _hRot, _pRot, vX,vY,vZ,h,p,x,y,z,is_airborne)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.addTask(self.checkMove, self.name + 'check movement', sort = 10)
        self.accept('playData{' + self.name, self.storePDat)
        self.accept('fire{' + self.name, self.fire)
        self.accept('changeWpn{' + self.name, self.set_weapon)
        self.pDat = None
        self.over = False
        
    def storePDat(self, val):
        self.pDat = val
        
    def checkMove(self, taskobj):
        if self.pDat:
            self._yMove = self.pDat[0]
            self._xMove = self.pDat[1]
            self._wantJump = self.pDat[2]
            self._wantCrouch = self.pDat[3]
            self._hRot = self.pDat[4]
            self._pRot = self.pDat[5]
            
            self.update()
            if (self._isAirborne == self.pDat[14]) and (self._isCrouched == self.pDat[15]) and self.np.get_pos().almost_equal(Point3(self.pDat[11],self.pDat[12],self.pDat[13]), 0.05) and isclose(self.pDat[9], self.np.get_h(), rel_tol = 1) and isclose(self.pDat[10], self._rig.get_p(), rel_tol = 1):
                if self.velocity.almost_equal(Point3(self.pDat[6], self.pDat[7], self.pDat[8]), 0.05):
                    self.velocity.set_x(self.pDat[6])
                    self.velocity.set_y(self.pDat[7])
                    self.velocity.set_z(self.pDat[8])
                self.np.set_h(self.pDat[9])
                self._rig.set_p(self.pDat[10])
                self.model.set_look(self._rig.get_p())
                self.np.set_pos(self.pDat[11],self.pDat[12],self.pDat[13],)
                self._isAirborne = self.pDat[14]
                if self._isCrouched != self.pDat[15]:
                    if self._isCrouched:
                        self.uncrouch()
                    else:
                        self.crouch
            else:
                self.over = True#Force client into accurate position

            self.pDat = None
        else: self.update()
        return Task.cont

    '''#Function for testing causes of networking bumpiness
    def checkOver(self):
        print(self._isAirborne == self.pDat[14])
        print(self.np.get_pos().almost_equal(Point3(self.pDat[11],self.pDat[12],self.pDat[13])), 0.05)
        print(isclose(self.pDat[9], self.np.get_h(), rel_tol = 1))
        print(isclose(self.pDat[10], self._rig.get_p(), rel_tol = 1))
        print(self._pRot)
        print('next Frame')
    '''
    
    def fire(self, fireVal):
        self._wpnFire = fireVal
        super().fire(fireVal)
        
    def set_weapon(self, slot, priority):
        self.wpnMgr.goto_subSlot(slot, priority)
    
class clientNetPlayer(playerEnt):#This one doesn't check to see if movement seems legit nor sends out instructions.
    over = False#This might not be nessisary???
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.addTask(self.Move, self.name + 'move', sort = 10)
        self.accept('playData{' + self.name, self.storePDat)
        self.accept('fire{' + self.name, self.fire)
        self.accept('changeWpn{' + self.name, self.set_weapon)
        self.pDat = None
        
    def storePDat(self, val):
        self.pDat = val
        
    def Move(self, taskobj):
        if self.pDat:
            self._yMove = self.pDat[0]
            self._xMove = self.pDat[1]
            self.model.walk(self._xMove, self._yMove)
            
            self._wantJump = self.pDat[2]
            self._wantCrouch = self.pDat[3]
            
            self._hRot = self.pDat[4]
            self._pRot = self.pDat[5]
            
            self.velocity.set_x(self.pDat[6])
            self.velocity.set_y(self.pDat[7])
            self.velocity.set_z(self.pDat[8])
            
            self.np.set_h(self.pDat[9])
            self._rig.set_p(self.pDat[10])
            self.model.set_look(self._rig.get_p())
            
            self.np.set_pos(self.pDat[11],self.pDat[12],self.pDat[13])
            self._isAirborne = (self.pDat[14])
            if self._isCrouched != self.pDat[15]:
                if self._isCrouched:
                    self.uncrouch()
                else:
                    self.crouch

            self.pDat = None
        else:self.update()
        return Task.cont
    

    def set_weapon(self, slot, priority):
        self.wpnMgr.goto_subSlot(slot, priority)
    