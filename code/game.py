from direct.showbase.DirectObject import DirectObject


#gravity
from panda3d.physics import ForceNode, LinearVectorForce, PhysicsCollisionHandler
#collision
from panda3d.core import CollisionTraverser
#modelPool for cleanup
from panda3d.core import ModelPool

#our own code
from .playerMgr import playerManager
from .entities.entModels import spinningModel
from .worldLoader import loadWorld

class game_world(DirectObject):#I'll make this a direct object just incase I need it
    def __init__(self, lobby, worldFile = 'models/maps/terrain.egg'):
        self.lobby = lobby

        super().__init__()
        
        #enable physics
        base.enableParticles()

        #Create a universal standard of gravity. TODO:: make it so servers can adjust this
        self.gravity = base.render.attach_new_node(ForceNode("gravitational force"))
        self.gravity.node().add_force(LinearVectorForce(0,0,-10))

        #World's collision management
        base.cTrav = CollisionTraverser()
        #base.cTrav.setRespectPrevTransform(True)
        self.handler = PhysicsCollisionHandler()
        
        self.handler.set_static_friction_coef(0.99)
        self.handler.set_dynamic_friction_coef(1)
        self.handler.set_almost_stationary_speed(0.2)

        self.handler.add_in_pattern('%fn-into')#TODO:: make player collisions more robust, for when we add depth tests for knockback and whatnot.
        self.handler.add_out_pattern('%fn-out')

        #Put world generation code calls here
        loadWorld(self, worldFile)

        #Gamemode logic here:
        #TODO:: write gamemode logic

        #Spawn Player control logic here: TODO::actually write this, or even rewrite this whole file. most of this is carryover from other project.
        self.playerMgr = playerManager(self)
        
        ##TODO:: split off the below into a "game start" function and replace it with code that synchronises the game start once all users have completed the above logic.
        self.playerMgr.round_start()
        
    def destroy(self):
        self.ignoreAll()
        
        self.playerMgr.delete()
        
        base.disableParticles()
        base.cTrav = None
        
        del self.handler
        del self.lobby
        
        self.world.remove_node()##World setup was moved to diffrent file, this is still here for... totally valid reasons.
        ModelPool.garbage_collect()#Remove all models that are not still used.

        base.render.set_shader_off()
        base.render.clearLight()
        self.sunNp.remove_node()
        self.amLNp.remove_node()
        