from direct.showbase.DirectObject import DirectObject

#lighting imports
from panda3d.core import DirectionalLight, AmbientLight
#gravity
from panda3d.physics import ForceNode, LinearVectorForce, PhysicsCollisionHandler
#collision
from panda3d.core import CollisionTraverser, BitMask32, CollisionBox, LPoint3f, CollisionNode

#our own code
from code.playerMgr import playerManager

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
        self.world = base.loader.load_model(worldFile)
        self.world.reparent_to(base.render)
        
        collisionNodes = self.world.find_all_matches('**/+CollisionNode')
        if collisionNodes.get_num_paths() <= 0:
            self.world.set_collide_mask(BitMask32(0b00001))
        else:
            for nodeP in collisionNodes:
                nodeP.set_collide_mask(BitMask32(0b00001))
        del collisionNodes
        #TODO:: add plane for falling out of the world
        

        #set up lighting
        base.render.set_shader_auto()
        sun = DirectionalLight("sun")
        sun.setColor((0.8, 0.77, 0.8, 1))
        self.sunNp = base.render.attach_new_node(sun)
        self.sunNp.setHpr(-30, -60, 0)
        base.render.set_light(self.sunNp)
        
        sun = AmbientLight("ambient Light")
        sun.setColor((0.2, 0.2, 0.2, 1))
        self.amLNp = base.render.attach_new_node(sun)
        base.render.set_light(self.amLNp)
        del sun

        #Gamemode logic here:
        #TODO:: write gamemode logic

        #Spawn Player control logic here: TODO::actually write this, or even rewrite this whole file. most of this is carryover from other project.
        self.playerMgr = playerManager()
        
    def destroy(self):
        self.ignoreAll()
        
        self.playerMgr.delete()
        base.disableParticles()
        base.cTrav = None
        del self.handler
        del self.lobby
        self.world.remove_node()
        base.render.set_shader_off()
        base.render.clearLight()
        self.sunNp.remove_node()
        self.amLNp.remove_node()
        