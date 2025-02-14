'''
All the "player" classes.
'''

####Player
###panda3d's:
#General:
from os import name
from panda3d.core import NodePath
#collision:
from panda3d.core import CollisionNode, CollisionBox, CollisionSphere, CollisionCapsule
from panda3d.core import Point3, Vec3, Vec2, Mat4
from panda3d.core import BitMask32
#Bullet raytracing:
#from panda3d.core import LensNode, PerspectiveLens
#from panda3d.fx import FisheyeLens
#Rotation
from panda3d.core import Quat
#Tasks:
from direct.task import Task
###Math:
from math import copysign, isclose
###ours:
from .npEnt import npEnt
from .playerModel import playerMdl
from ..weapons.wpnSlots import slotMgr, slotWeapon
from ..weapons.as_wpns import as_default
#from ..weapons.bulletBase import bulletWeapon
from ..weapons.damageTypes import damageTypeBase

class playerEnt(npEnt):
    
    skipAccept = True#we don't accept geometry.
    
    ##Player Member Variables:
    maxHealth = 100#We should find a better amount later and have UI translate that to 100 or maybe not
    

    events = (("{name}-into-ground", "tangible_collide_into_event"),("{name}-out-ground", "tangible_collide_out_event"),("{name}-again-ground", "tangible_collide_again_event"),
              ("{name}-into-water", "water_collide_into_event"),("{name}-out-water", "water_collide_out_event"),("{name}-again-water", "water_collide_again_event"),
              )

    net_commands = (("reload"), ("removeRide"),
                    ("playData", "play", 1),
                    ("fire", "u8int", 1),
                    ("changeWpn", "u8int", 2),
                    ("playerHealthChange", "float64", 1),
                    ("addRide", "string", 1),
        )
    host_net_commands = ("playerHealthChange"
        )
    
    ##################
    #Creation Methods#
    ##################
    def __init__(self, team = 0, isHost = False, **kwargs):
        super().__init__(**kwargs)#make self.np
        #self.np.set_collide_mask(BitMask32(0b0010000))
        self.np.set_tag('player', self.name)
        
        self.team = team
        
        self.isHostPlayer = isHost#We're the host's clientPlayer, we can skip stuff for networking

        #Create bounding box
        cNode = CollisionNode(self.name + '_bounding_box')
        self.bBSolids = (CollisionCapsule(0,0,-1, 0,0,1, 1.15), CollisionCapsule(0,0,-1, 0,0,0, 1.15))#Diffrent collisionSolids for cNode, 0=normal, 1=crouch, 2=fastSwm
        cNode.add_solid(self.bBSolids[0])
        match team:
            case 0: mask = BitMask32(0b1010101)#deathmatch
            case 1: mask = BitMask32(0b1000101)#Red
            case 2: mask = BitMask32(0b1010001)#Blue
            case _: mask = BitMask32(0b1000101)#PVE
        cNode.set_from_collide_mask(mask)
        match team:
            case 0: mask = BitMask32(0b0010100)#deathmatch
            case 1: mask = BitMask32(0b0010000)#Red
            case 2: mask = BitMask32(0b0000100)#Blue
            case _: mask = BitMask32(0b0010000)#PVE
        cNode.set_into_collide_mask(mask)
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
        cNode.set_into_collide_mask(BitMask32(0b0000000))#No into collisions
        self.wBall = self.np.attach_new_node(cNode)
        self.wBall.set_tag("waterBal", "t")
        del cNode
        ##TODO::: assign bitmasks to above collisionNodes
        
        #Create Model
        self.model = playerMdl(np = self.np, pos = (0,0,-2), collision_mode = team)
        self.model.np.set_h(180)#I'm doing some alterations here because I'm testing with a model not made for this project
        
        #######WEAPONS#######
        #Create bullet LensNode.
        '''
        Panda3d let's you extrude vectors from a lens based on coordinates. we can use this to calculate bullet raycasting vectors. 
        '''
        self._rig = NodePath(self.name + "_rig")#this is the axis of pitch rotation for both the raycast LensNode and the camera. We don't just parent the camera to the LensNode because we might want an offset for the bullet origin.
        self._rig.reparent_to(self.np)
        self._rig.set_z(1.55)
        #'''
        m = loader.loadModel('jack')
        m.reparent_to(self._rig)
        m.set_scale(0.23)
        #'''

        #self._bulletNode = LensNode(self.name + "_bulletLens", PerspectiveLens())#Weapons will modify these properties when they're set active.
        #self._bulletLens = self._bulletNode.get_lens()
        #self._bulletLens.set_near(0.0)
        self._bulletNP = self._rig.attach_new_node(self.name +'bulletNP')
        #self._bulletNP.set_p(-90)
        
        #Create wpnManager
        self.wpnMgr = slotMgr(self.name)
        self.add_weapon(as_default, user = self)
        
        #Accept events
        self.add_network_events()
        
        #weapon variables
        self._wpnFire = 0#This tells the interogate function if we've fired on this frame and which fire func we used. Also tells clientPlayer to fire
        self._changeWpn = False#Tells interogate function that it needs to serialize a change in selected weapon
        self._reload = False#We've started a reload. This is actually changed by the weapon.
        
        ################Create all instance variables##############
        
        ##Administrative/anti-cheat
        ##self.teleportOk = False#Set this to true if and whenever velosity's big enough or we're teleporting somewhere. If not this and this player moved too far, it's possible that client is trying to lie about present location.
        self._isSpawned = False
        
        ##Movement
        self._xMove = 0.0 #float for relatively left/right movement.
        self._yMove = 0.0 #ditto, but for forward/back
        
        self._wantJump = False#does this player object want to jump whenever such an action is valid?
        self._wantCrouch = False#will we even use this right away?
        
        self._hRot = 0.0 #amount of heading rotation. If we're doing mouse/keys, this is how far along the x axis from the center user has moved cursor.
        self._pRot = 0.0 #pitch rotation. (looking up/down.)
        
        self._collidingNps = []
        
        ##physics
        self.velocity = Vec3(0,0,0)
        self._isAirborne = False
        self._isSwim = False
        
        self.wBall.show()
        self.bBox.show()
        
        #Rideables
        self.riding = None
        self.timeOffRide = 0
        self.isRiding = False
        self.touchingRide = False
        
        #Ladders
        self.onLadder = False
        self.ladder = None
        self.ladderH = 0
        self.ladderXAxis = False
        
        ##bBox
        self._inCrouch = False#Are we doing the crouching animation?
        self._isCrouched = False
        self._swmFst = False
        
        ##Gameplay
        #Health
        self.health = self.maxHealth
        self.health_changed = False
        
    
    def add_colliders(self, trav, handler):
        trav.add_collider(self.bBox, handler)
        handler.add_collider(self.bBox, self.np)
        trav.add_collider(self.wBall, handler)
        handler.add_collider(self.wBall, self.np)
        
    def add_network_events(self):#split off for clarity's sake
        if not base.isHost:
            self.accept("addRide{" + self.name, self.add_ride_network)
            self.accept("removeRide{" + self.name, self.remove_ride)
            self.accept("playerWpn access change{" + self.name, self.change_wpn_access)
        
    ##########
    #Spawning#
    ##########
        
    def spawn(self, sPoint: NodePath):
        #print(sPoint.get_name())
        self.np.reparent_to(base.game_instance.world)
        self.np.set_pos(sPoint, 0,0,0)
        self.np.set_h(sPoint, 0)
        self._isAirborne = True
        self.health = self.maxHealth
        self._isSpawned = True
    
    def de_spawn(self):
        self.remove_ride()
        self.np.detach_node()#carefull not to lose the class refrence during this time!
        self._collidingNps = []
        self._isSpawned = False
        self.exit_ladder()
        
    ##################
    #Movement Methods#
    ##################
    
    upVec = Vec3(0,0,1)#standard up vector
        
    def update(self, task = None):
        ##########Part 1: calculate the half-frame change in velocity
        deltaTime = globalClock.get_dt()
        if not (self._isSwim or self.onLadder): self.velocity_half_update(deltaTime)
        elif self.onLadder: self.ladder_half_update(deltaTime)
        else: self.swim_half_update(deltaTime)
        ##########Part 2: Perform Movement calculations
        #Riding
        if base.isHost and self.isRiding:
            if self.touchingRide:
                if self.timeOffRide != 0: self.timeOffRide = 0
            elif self.timeOffRide >= 0.2:#Max number of seconds before we're sure we're no longer touching the ride
                self.remove_ride()
            else: self.timeOffRide += deltaTime
            

        if self.velocity.length(): self.np.set_fluid_pos(self.np.get_pos() + self.velocity * deltaTime)
        #print(self.velocity)
        
        ##Calculate rotation
        self.np.set_h(self.np, self._hRot)#TODO:: This is insecure against aimhacking.
        #print(self.np.get_h())
        #Rotate velocity

        #Calculate pitch
        if self._pRot != 0 and (abs(self._rig.get_p() + self._pRot) <= 85):
            self._rig.set_p(self._rig, self._pRot)
            
        ##Crouch
        if self._wantCrouch and not (self._isCrouched or self._inCrouch):
            if self._isAirborne:
                self.crouch()
            else:
                self.addTask(self.inCrouchTask, "crouchTask")
                self._inCrouch = True
        elif self._isCrouched:
            if not self._wantCrouch or self._isSwim:
                self.uncrouch()
        
        
        #animations
        self.model.set_look(self._rig.get_p())
        self.model.walk(self._xMove, self._yMove)
        
        ##########Part 3: calculate the second-half-frame velocity change
        avgRate = globalClock.get_average_frame_rate()#this is a prediction for how long the next frame will be
        if not (self._isSwim or self.onLadder): self.velocity_half_update(1/avgRate)#divide 1 by avgRate to get estimated next frame time
        elif self.onLadder: self.ladder_half_update(1/avgRate)
        else: self.swim_half_update(1/avgRate)
        #Easy as that, right?
        if task:
            return Task.cont
        
        
    def velocity_half_update(self, scalar):
        '''
        scalar should be deltatime for first half, average frame rate for second
        '''
        if self._isAirborne:#changing z velocity is a bad idea if we're touching the ground.
            self.velocity.add_z(-((97.3*scalar)/2))#Subtract vertical velocity for half a frame. #TODO:: if you want weight modifiers, add them here.#4 is gravity
        elif self._wantJump:
            zOffset = self.velocity.get_z() if self.velocity.get_z() > 0 else 0
            self.velocity.add_z(21.920 - zOffset/2)
            
        ##Begin xy velocity
        velo2d = abs(self.velocity.get_xy().length())
            
        speedLimit = 55.5#maximum horizontal speed
        speedToLimit = speedLimit - velo2d
        absoluteLimit = 100
        walkAccel = speedLimit if ((speedToLimit/speedLimit) <= 0.02) else speedLimit * 4
        airAccel = 25#acceleration while in air per second
        friction = 49.58#deceleration/acceleration resistance per second. If velocity in a direction is less than this, velocity is stopped in a short period of time
        
        ##Adjust values
        if (not (self._yMove or self._xMove)): friction *= 2
        elif self.velocity.length() > speedLimit: friction *= 4
        notExceedSpeedLimit = velo2d < speedLimit
        

        ##Velocity Calculations
        #Y velosity calculations
        normVector = self.velocity.get_xy().normalized()
        newVelocity = Vec3(0,0,0)

        if self._yMove:
            if not self._isAirborne and notExceedSpeedLimit:
                dVector = self.np.get_parent().get_relative_vector(self.np, Vec3(0,1,0))#directional vector
                if abs((self.velocity.get_xy() + (dVector * self._yMove).get_xy()).length()) < velo2d:
                    newVelocity.add_y(copysign(min(abs(self.velocity.get_y()), speedLimit), self._yMove)/2)#instantly reverse momentum
                else:#If y isnt too much bigger than x
                    change = (( self._yMove * walkAccel ) * scalar)/2
                    newVelocity.add_y(change)
                    del change
            elif self._isAirborne:#note we don't cap velocity while in air
                newVelocity.add_y((self._yMove*airAccel*scalar) /2)
                
        #X velosity calculations
        if self._xMove:
            if not self._isAirborne and notExceedSpeedLimit:
                dVector = self.np.get_parent().get_relative_vector(self.np, Vec3(1,0,0))#directional vector
                if abs((self.velocity.get_xy() + (dVector * self._xMove).get_xy()).length()) < velo2d:
                    newVelocity.add_x(copysign(min(abs(self.velocity.get_x()), speedLimit), self._xMove)/2)
                else:
                    change = (( self._xMove * walkAccel ) * scalar)/2
                    newVelocity.add_x(change)
                    del change
            elif self._isAirborne:#note we don't cap velocity while in air
                newVelocity.add_x((self._xMove*airAccel*scalar)/2)
        
        self.velocity += self.np.get_parent().get_relative_vector(self.np, newVelocity)
        
        #Velocity Cap
        if self.velocity.get_xy().length() > absoluteLimit:
            self.velocity.set_y((normVector * absoluteLimit).get_y())
            self.velocity.set_x((normVector * absoluteLimit).get_x())
        

        ##Friction
        newVelocity = Vec3(0,0,0)    
        if not self._isAirborne:#extra stuff for only on the ground
            dVector = self.np.get_relative_vector(self.np.get_parent(), self.velocity)
            #Y
            if abs(dVector.get_y()) > 0.2 and not (self._yMove and (abs(dVector.get_x()) > abs(dVector.get_y()) + 12)):#if we're moving y but x is bigger, we skip friction on y to catch-up
                newVelocity.add_y(-copysign(friction, dVector.get_y())*scalar / 2)#^We disable friction to give axis a boost to catch up in velocity
            #X
            if abs(dVector.get_x()) > 0.2 and not (self._xMove and (abs(dVector.get_y()) > abs(dVector.get_x()) + 6)):
                newVelocity.add_x(-copysign(friction, dVector.get_x())*scalar / 2)
                
            self.velocity += self.np.get_parent().get_relative_vector(self.np, newVelocity)
            
            if not self._xMove and not self._yMove and self.velocity.get_xy().length() < 1:
                self.velocity.set_x(0)
                self.velocity.set_y(0)
                
            

    def swim_half_update(self, scalar):##TODO:: see if this can be put back into main half update. this is kinda a stupid hack.            
        speedLimit = 100#maximum horizontal speed
        swimAccel = 83.12#acceleration while walking per second
        friction = 28.39#deceleration/acceleration resistance per second. If velocity in a direction is less than this, velocity is stopped in a short period of time
        
        if self._wantJump:
            if self.velocity.get_z() <= 40:
                self.velocity.add_z(((50*scalar)/2))
            else: self.velocity.set_z(40)
        elif self.velocity.get_z() > -30:
            self.velocity.add_z(-((0.35*scalar)/2))
            if self.velocity.get_z() < -30:
                self.velocity.set_z(-30)
        
        rigRelative = Vec3(0,0,0)
        ##Adjust values
        if not (self._yMove or self._xMove): friction *= 2
        notExceedControlSpeed = self.velocity.get_xy().length() <= speedLimit
        
        ##Y velosity calculations
        if self._yMove:
            if notExceedControlSpeed:
                rigRelative.add_y((self._yMove*swimAccel*scalar)/2)
                    
        #apply rigRelative to self.velocity
        self.velocity += self.np.get_parent().get_relative_vector(self._rig, rigRelative)            
                
        ##X velosity calculations
        if self._xMove:
            if notExceedControlSpeed:
                dVec = self.np.get_quat(self.np.get_parent()).get_right()
                self.velocity += dVec * self._xMove*swimAccel*scalar /2
                
        ##Velocity-capping and friction
                    
        if self.velocity.get_xy().length() > speedLimit:
            normVector = self.velocity.get_xy().normalized()
            self.velocity.set_y((normVector * speedLimit).get_y())
            self.velocity.set_x((normVector * speedLimit).get_x())
        
        #friction
        if abs(self.velocity.get_y()) > 0.2:#Add friction Y
            self.velocity.add_y(-copysign(friction, self.velocity.get_y())*scalar / 2)
        elif not self._yMove and self.velocity.get_y():
            self.velocity.set_y(0)
            
        if abs(self.velocity.get_x()) > 0.2:#Add friction X
            self.velocity.add_x(-copysign(friction, self.velocity.get_x())*scalar / 2)
        elif not self._xMove and self.velocity.get_x() != 0:
            self.velocity.set_x(0)
            
    
    def ladder_half_update(self, scalar):
        
        #While player is on ladder we need to quickly slow velocity, so this is first
        ladderAccel = 1
        ladderMax = 7
        
        if self.velocity.length():
            if abs(self.velocity.length()) < 1:
                    self.velocity.set(0,0,0)
            else:
                self.velocity.add_x(-copysign(scalar*ladderAccel/2, self.velocity.get_x()))
                self.velocity.add_y(-copysign(scalar*ladderAccel/2, self.velocity.get_y()))
                self.velocity.add_z(-copysign(scalar*ladderAccel/2, self.velocity.get_z()))
                if abs(self.velocity.length()) < 0.05: self.velocity.set(0, 0, 0)

        npH = self.np.get_h(base.game_instance.world)#Need to correct this for sides
        
        ladderSide = self.ladder.get_x(self.np) > 0#True if to the right of our nodepath
        amntNotFacing = abs(180 - abs(self.ladderH - npH))#The number of degrees by which the nodepath is not facing the ladder
        #print(amntNotFacing)
        
        if amntNotFacing < 45 or amntNotFacing > 135:#ladder in front/behind
            if self._rig.get_p() >= 0:
                climbMove = self._yMove
                slideMove = self._xMove
            elif amntNotFacing > 135:#Ladder Behind and looking down
                climbMove = -self._yMove
                slideMove = - -self._xMove
            else:#looking front down
                climbMove = -self._yMove
                slideMove = self._xMove
        elif ladderSide:#Ladder to right
            climbMove = self._xMove
            slideMove = -self._yMove
        else:#Ladder to left or error
            climbMove = -self._xMove
            slideMove = self._yMove
        slideMove *= copysign(1, self.ladderH)
        
        '''
        axisCalc = Quat()
        axisCalc.set_from_axis_angle(self.ladderH, self.upVec)
        axisCalc.normalize()
        slideAxis = axisCalc.get_right()
        slideAxis.normalize()
        '''
        
        if climbMove:
            self.np.set_z(self.np, climbMove * ladderMax * scalar / 2)
        

        if slideMove:
            #slideVelocity = slideAxis * slideMove * ladderMax * scalar / 2
            if self.ladderXAxis:#TODO:: This doesn't account for what side of the ladder we're on
                self.np.set_x(self.ladder, self.np.get_x(self.ladder) + (slideMove * ladderMax * scalar/2))
            else:
                self.np.set_y(self.ladder, self.np.get_y(self.ladder) + (slideMove * ladderMax * scalar/2))
            

        if self._wantJump:
            if amntNotFacing > 90:
                self.velocity.add_y(0.5/2)#Forgot that velocity is player relative
                self.velocity.add_z(2/2)
            else:#Jump in direction we're looking
                self.velocity.add_y(-0.5/2)
                self.velocity.add_z(2/2)
            self.exit_ladder()
            
    def exit_ladder(self):#Defined here so we can access it ourselves if need be
        #print('exiting ladder')
        if not self.onLadder: return
        self.ladder.get_net_python_tag("entOwner").remove_player(self)
        self.ladder = None
        self.onLadder = False
        self.ladderH = False#Technically a number if we need it, but saves memory by not creating a new number
        

    ########
    #Riding#
    ########
    
    def add_ride(self, ride):
        if ride != self.riding:
            self.velocity = ride.np.get_relative_vector(self.np.get_parent(), self.velocity)
            self.np.wrt_reparent_to(ride.np)
        #self.np.set_pos(self.np.get_pos(ride.np))
        #self.np.reparent_to(ride.np)

        self.riding = ride
        self.isRiding = True
        
        self.touchingRide = True

        self.timeOffRides = 0
        
        if self.velocity.length() > 0.3:
            self.velocity -= ride.pseudoVelocity
            '''
            rideTransformMat = self.np.get_mat(ride.np)
            self.velocity -= rideTransformMat.xformVec(ride.pseudoVelocity)
            '''
        if base.isHost:
            base.server.add_message("addRide{" + self.name, (ride.name,))

    def add_ride_network(self, rideName):
        ride = base.game_instance.entityMgr.get_entity(rideName)
        if ride and ride != self.riding: self.add_ride(ride)
    
    def remove_ride(self):
        self.np.wrt_reparent_to(base.game_instance.world)
        
        if self.riding == None: return
        '''
        rideTransformMat = self.np.get_mat(self.riding.np)
        self.velocity += rideTransformMat.xformVec(self.riding.pseudoVelocity)
        '''
        self.velocity += self.np.get_relative_vector(self.riding.np, self.riding.pseudoVelocity)
        
        self.riding = None
        self.isRiding = False
        
        if base.isHost:
            base.server.add_message("removeRide{" + self.name)
                
    ##############
    #BBox changes#
    ##############
    
    def inCrouchTask(self, taskobj):
        time = taskobj.time
        if self._isAirborne or self._isCrouched or time >= 0.3:
            self._inCrouch = False
            self.crouch()
            return Task.done
        elif not self._wantCrouch:
            self.uncrouch()
            self._inCrouch = False
            return Task.done
        self._rig.set_z(0.6 + (0.95- (time/0.3)))
        return Task.cont
        
    
    def crouch(self):
        self.bBox.node().set_solid(0,self.bBSolids[1])
        self._rig.set_z(0.6)
        if self._isAirborne:
            self.np.set_z(self.np, 1)
        self._isCrouched = True
            
    def uncrouch(self):
        self.bBox.node().set_solid(0,self.bBSolids[0])
        self._rig.set_z(1.55)
        if self._isAirborne:
            self.np.set_z(self.np, -1)
        self._isCrouched = False
            
    ########
    #Events#
    ########
            
    def tangible_collide_into_event(self, entry):
        vector = entry.get_surface_normal(self.np.get_parent())#This is relative to our parent(usually world) because velocity is parent-relative
        vector = vector.normalized()
        point = entry.get_surface_point(self.np)
        if vector.get_z() > 0.6:#(Above comment is copied from code from other project.)
            self._isAirborne = False
            self._collidingNps.append(entry.get_from_node_path())
        elif (not vector.get_z() < 0) and point.z + 1 <= 0.03 and point.z < 0:
            self.np.set_z(self.np, point.z+1)
        if abs(point.get_z()) <= 2.15: self.bend_velocity(vector)#only bend velocity if the point is within reach of the top or bottom
        
    def tangible_collide_again_event(self, entry):
        vector = entry.get_surface_normal(self.np.get_parent())
        vector = vector.normalized()
        if self._isAirborne:
            if vector.get_z() > 0.6:
                self._isAirborne = False
        self.bend_velocity(vector)
                
    def bend_velocity(self, vector):
        if self.velocity.length() <= 0.01:
            return
        veloVec = self.velocity.normalized()
        angle = veloVec.angle_deg(vector)
        if vector.get_z() > 0.83 and self.velocity.get_z() <= 3:
            self.velocity.set_z(0)
            zSet = True
        else: zSet = False
        if angle >= 1:
            norDot = vector.dot(self.velocity)
            mod = Vec3(vector)
            mod *= norDot
            self.velocity -= mod
        if zSet:#Run this a second time to be safe
            self.velocity.set_z(0)
    
    def tangible_collide_out_event(self, entry):
        np = entry.get_from_node_path()
        #vector = entry.get_surface_normal(np)
        if np in self._collidingNps:
            self._collidingNps.remove(np)
        if len(self._collidingNps) == 0: self._isAirborne = True
        

    def water_collide_into_event(self, entry):
        self._isSwim = True
        
    def water_collide_again_event(self, entry):
        self._isSwim = True
        
    def water_collide_out_event(self, entry):
        self._isSwim = False
        if (self._wantJump and self._yMove > 0) and self._rig.get_p() > 30:
            self.velocity.add_z(0.1)
        elif self._wantJump and self.velocity.get_z() > 0.1:
            self.velocity.add_z(-0.05)#Slow down velocity so we can try and 'float'
        

    def fire(self, fireVal):
        if fireVal == 1: messenger.send(self.name + "-fire1")
        elif fireVal == 2: messenger.send(self.name + "-fire2")#Inconsistent with elsewhere, but we arn't checking if fireVal is 0 here.
    

    ####################
    ######Gameplay######
    ####################
    
    def change_health(self, val):
        self.health = val
    
    def take_damage(self, damage : damageTypeBase):
        if not self._isSpawned:
            return
        damage.apply(self)#We do this here for reasons...
        if base.isHost:
            if self.health <= 0:#Host tells us when to die, we don't decide that for ourselves.
                self.die(damage.source)
            #self.health_changed =True
            base.server.add_message("playerHealthChange{" + self.name, (self.health,))
    
    def die(self, cause):#TODO:: add code for "dropping weapons"
        self.de_spawn()
        messenger.send("death", [self.name, cause])
        
    def add_weapon(self, wpnType, **kwargs):#See clientPlayer for why we might want to override this
        self.wpnMgr.add_weapon(wpnType(**kwargs))
        
    def change_wpn_access(self, accessVal):
        if accessVal: self.wpnMgr.enable_weapons()
        else: self.wpnMgr.disable_weapons()
        
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
            slot, subSlot = self.wpnMgr.get_slots()
            server.add_message("changeWpn{" + self.name, (slot, subSlot,))
            self._changeWpn = False
            
        if self._reload:
            server.add_message("reload{" + self.name)
            self._reload = False
        elif self._wpnFire:#Simplify datagram
            server.add_message("fire{" + self.name, (self._wpnFire,))
            self._wpnFire = 0#This is a double redundancy for clientPlayer, but we need this here for hostNetPlayer, or else it won't get serialized to clients
        '''
        if self.health_changed:
            server.add_message("playerHealthChange{" + self.name, (self.health,))
            self.health_changed = False
            '''
    

    def destroy(self):
        self.de_spawn()
        
        self.model.destroy()
        self.wpnMgr.destroy()
        
        if self.isRiding: self.remove_ride()
        
        del self.velocity
        super().destroy()
        

    