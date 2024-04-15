import random
from direct.showbase.DirectObject import DirectObject


#collision
from panda3d.core import CollisionHandlerPusher, CollisionTraverser
#modelPool for cleanup
from panda3d.core import ModelPool

#our own code
from .playerMgr import playerManager
from .rng import randomGen
from .entities.entModels import spinningModel
from .worldLoader import loadWorld

class game_world(DirectObject):#I'll make this a direct object just incase I need it
    def __init__(self, lobby, worldFile = 'models/maps/terrain.egg'):
        self.lobby = lobby
        base.game_instance = self

        super().__init__()
        
        #enable physics
        #base.enableParticles()

        #Create a universal standard of gravity. TODO:: make it so servers can adjust this
        #self.gravity = 0.983

        #World's collision management
        base.cTrav = CollisionTraverser()
        #base.cTrav.setRespectPrevTransform(True)
        self.handler = CollisionHandlerPusher()
        #Add event patterns
        self.handler.add_in_pattern("%(player)fh%(bBox)fh%(player)ft-into-ground%(water)ix%(trigger)ix")
        self.handler.add_out_pattern("%(player)fh%(bBox)fh%(player)ft-out-ground%(water)ix%(trigger)ix")
        self.handler.add_again_pattern("%(player)fh%(bBox)fh%(player)ft-again-ground%(water)ix%(trigger)ix")
        
        '''
        self.handler.set_static_friction_coef(0.99)
        self.handler.set_dynamic_friction_coef(1)
        self.handler.set_almost_stationary_speed(0.2)
        '''

        self.handler.add_in_pattern('%fn-into')#TODO:: make player collisions more robust, for when we add depth tests for knockback and whatnot.
        self.handler.add_out_pattern('%fn-out')

        #Put world generation code calls here
        loadWorld(self, worldFile)

        #Gamemode logic here:
        #TODO:: write gamemode logic

        #Spawn Player control logic here:
        self.playerMgr = playerManager(self)
        
        #rng manager
        self.rngMgr = randomGen()
        
        #logic for syncing game start
        if base.isHost:
            self.readyTester = []
            self.accept('ready', self.ready_recieve)
            self.ready_recieve('host')
        else:
            self.accept('gameStart', self.game_start)
            self.lobby.server.add_message("ready", (int(self.lobby.memVal),))
        
        
    def ready_recieve(self, num):
        self.readyTester.append(num)
        if self.lobby.tracker.ready_test(self.readyTester):
            self.ignore('ready')
            del self.readyTester
            self.game_start()
    
    def game_start(self):
        if self.lobby.isHost:
            self.lobby.server.add_message('gameStart')
        else:
            self.ignore('gameStart')
        self.playerMgr.round_start()
        
    def destroy(self):
        self.ignoreAll()
        del base.game_instance
        
        self.playerMgr.delete()
        self.rngMgr.delete()
        
        base.disableParticles()
        
        base.cTrav.clear_colliders()
        base.cTrav = None
        
        self.handler.clear_colliders()
        del self.handler
        del self.lobby
        
        self.world.remove_node()##World setup was moved to diffrent file, this is still here for... totally valid reasons.
        ModelPool.garbage_collect()#Remove all models that are not still used.

        base.render.set_shader_off()
        base.render.clearLight()
        self.sunNp.remove_node()
        self.amLNp.remove_node()
        