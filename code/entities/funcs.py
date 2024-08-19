'''
Superlong document with all 'func' entities, for now.
directory:
-movement funcs
--funcSpin
'''

from .npEnt import *

from direct.task import Task

from math import copysign, degrees
######################MOVEMENT FUNCS#######################

class funcSpin(npEnt):
    
    def spin(self, task):#TODO:: why is task object not being given to us?? why??? :(((
        deltaTime = globalClock.get_average_frame_rate()#TODO:: we'll have to see if getting deltaTime in all appropriate func entities causes a performance inpact. Too bad!
        self.np.set_h(self.np, self.turn/deltaTime)
        return Task.cont
    
    tasks = (('spinNp', 'spin'),
             )#if npEnt had any tasks, we would put 'x for x in npEnt.tasks' here.
    
    turn = 100#how many units to turn per second on average
    


from math import atan2
from panda3d.core import headsUp, Quat
class funcLadder(npEnt):
    acceptCollisions = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if self.np.node().is_collision_node():
            cbox = self.np.node().get_solid(0)
        else: cbox = self.np.find('**/+CollisionNode').node().get_solid(0)
        
        dimensions = cbox.get_dimensions()
        self._zDist = dimensions.get_z()/2#z distance from center
        self._xSideDist = dimensions.get_x()/2
        self._ySideDist = dimensions.get_y()/2
        
        self._climbingPlayers = []
        #print(self.name)
        
    events = (("player-in-{name}", "in_player"),)
    tasks = (("{name}-check_players", "check_players"),)
    
    def in_player(self, entry):
        #print("in ladder")
        #Calc angle
        player = entry.get_from_node_path().get_net_python_tag("entOwner")
        if player.onLadder: return#Skip everything, player's already on a ladder
        
        player.onLadder = True
        player.ladder = self.np
        
        #calc ladderH
        norm = entry.get_surface_normal(self.np)
        if abs(norm.get_y()) > abs(norm.get_x()):
            if norm.get_y() < 0:
                offset = 0
            else:
                offset = 180
            xSide = False
            player.ladderXAxis = True
        else:
            if norm.get_x() > 0:
                offset = 90
            else:
                offset = -90
            xSide = True
            player.ladderXAxis = False
        ladderH = offset + self.np.get_h(base.game_instance.world)
        if abs(ladderH) > 180: ladderH = -copysign(180 - abs(ladderH - copysign(180, ladderH)), ladderH)
        #print(ladderH)
        player.ladderH = ladderH
        
        #Do stuff that this entity needs
        self.acceptOnce(player.name +"-into-ground", self.player_ground)
        self._climbingPlayers.append([player, xSide])
        '''
        quat = Quat()
        headsUp(quat, entry.get_surface_normal(self.np))
        player.ladderH = quat.get_hpr().get_x()#assuming x = h here
        '''
        

    def check_players(self, taskobj):
        for playerGroup in self._climbingPlayers:
            player = playerGroup[0]
            if abs(player.np.get_z(self.np) - 1) > self._zDist:
                player.exit_ladder()
            else:
                if playerGroup[1]:
                    if abs(player.np.get_y(self.np)) > self._ySideDist: player.exit_ladder()
                elif abs(player.np.get_x(self.np)) > self._xSideDist: player.exit_ladder()
                

    def remove_player(self, player):
        for pGroup in self._climbingPlayers:
            if pGroup[0] is player: self._climbingPlayers.remove(pGroup)
            

    def player_ground(self, entry):
        player = entry.get_from_node_path().get_net_python_tag("entOwner")
        vector = entry.get_surface_normal(entry.get_from_node_path())
        if vector.get_z() > 0.6 and player.onLadder and player.ladder == self.np:
            player.exit_ladder()
        else:
            self.acceptOnce(player.name +"-into-ground", self.player_ground)


from ..weapons.damageTypes import healingDamageType
from panda3d.core import BitMask32
class funcHealing(npEnt):
    acceptCollisions = True
    
    events = (("player-again-{name}", "heal"),)
    
    def __init__(self, healAmnt = 3, **kwargs):
        super().__init__(**kwargs)
        
        cNodePaths= self.np.find_all_matches("**/+CollisionNode")
        for cNodePath in cNodePaths:
            node = cNodePath.node()
            if node.get_solid(0).is_tangible():
                node.set_into_collide_mask(BitMask32(0b0100001))#Change bitmask so player bBox can collide
                
        if self.np.node().is_collision_node:
            self.np.node().set_into_collide_mask(BitMask32(0b0100001))
        
        self.healAmnt = healAmnt#Amount to heal per second
    
    def heal(self, entry):
        dt = globalClock.get_dt()
        if entry.get_from_node_path().has_net_python_tag("entOwner"):
            player = entry.get_from_node_path().get_net_python_tag("entOwner")
            heal = healingDamageType(self.name)
            heal.calc_over_time(self.healAmnt, dt)
            player.take_damage(heal)
    

class funcDisableWeapons(npEnt):
    acceptCollisions = True
    events = (("player-in-{name}", "disable"),
              ("player-out-{name}", "enable")
              )
    
    
    def disable(self, entry):
        player = entry.get_from_node_path().get_net_python_tag("entOwner")
        player.wpnMgr.disable_weapons()
        if base.isHost:
            base.server.add_message("playerWpn access change{" + player.name, (False,))
            
    def enable(self, entry):
        player = entry.get_from_node_path().get_net_python_tag("entOwner")
        player.wpnMgr.enable_weapons()
        if base.isHost:
            base.server.add_message("playerWpn access change{" + player.name, (True,))


from panda3d.core import Vec3
class funcRideable(npEnt):
    
    acceptCollisions = True
    
    events = (("player-in-{name}", "ride"),
              ("player-out-{name}", "stop_ride"))
    
    tasks = (("{name}-ridable update", "update"),)
    
    def __init__(self, **kwargs):
        self.pseudoVelocity = Vec3(0,0,0)
        
        
        self.isGone = False#a variable to alert players that this entity has been destroyed and to remove it from memory.
        super().__init__(**kwargs)
        
    def ride(self, entry):
        player = entry.get_from_node_path().get_net_python_tag("entOwner")
        if base.isHost and player.riding == None and (entry.get_surface_normal(entry.get_from_node_path()).get_z() > 0.5):
            player.add_ride(self)
        elif self is player.riding:
            player.touchingRide = True
            
    
    def stop_ride(self, entry):
        player = entry.get_from_node_path().get_net_python_tag("entOwner")
        if self is player.riding:
            player.touchingRide = False
    
    def update(self, taskObj = None):
        return Task.cont
        
    def destroy(self):
        self.isGone = True
        return super().destroy()
    

from math import pi, cos, sin, radians, atan2
from panda3d.core import Vec2
class funcRotateAroundTarget(funcRideable):
    
    def __init__(self, target:NodePath, speed:float = 2.0, **kwargs):
        super().__init__(**kwargs)
        
        self._target = target
        
        self._speed = speed
        self._radius = self.np.get_pos(target).length()
        self._unitDegreeConversion = pi*(self._radius * 2) / 360
        #self._offset = self.np.get_h(self._target)
        
        self.got_match = False#If true, we can skip update because we got info from host
        if not base.isHost: self.accept("funcRAT set dist{" + self.name, self.match_host)
        
        self._distanceDegrees = degrees( atan2(self.np.get_y(target), self.np.get_x(target)) )
        #self.update()
        self.pseudoVelocity = Vec3(0, self._speed, 0)
        
        
    def update(self, taskObj=None):
        #Client-only skip
        if self.got_match:
            self.got_match = False
            return super().update(taskObj)
        #Move the np
        dt = globalClock.get_dt()
        
        frameDistance = self._speed * dt
        self._distanceDegrees += frameDistance * self._unitDegreeConversion
        if self._distanceDegrees > 360: self._distanceDegrees -= 360
        distanceRad = radians(self._distanceDegrees)

        distancesFromTarget = Vec2(cos(distanceRad), sin(distanceRad))
        distancesFromTarget *= self._radius
        self.np.set_pos(self._target, distancesFromTarget.get_x(), distancesFromTarget.get_y(), 0)
        self.np.set_h(self._target, self._distanceDegrees)
        
        #self.pseudoVelocity = Vec3(-sin(distanceRad), cos(distanceRad), 0) * self._speed#set the pseudoVelocity to tangent of the circle * speed# Trying new method that has static pseudoVelocity
        
        if base.isHost: base.server.add_message("funcRAT set dist{" + self.name, (self._distanceDegrees,))

        return super().update(taskObj)
    
    def match_host(self, dist):
        self._distanceDegrees = dist
        self.got_match = True

    def destroy(self):
        del self._target
        return super().destroy()