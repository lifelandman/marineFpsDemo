

from .bulletBase import bulletWeapon
from .wpnAmmo import ammoWeapon

class as_default(bulletWeapon, ammoWeapon):
    ##TriggerWait
    wait = 0.2
    
    ##ammo:
    loadWait = 0.45
    clipSize = 10
    storageMax = 120
    
    primAmnt = 1
    bufferTime = 0.3
    
    ##Raycasting
    maxSpreadX = 1
    maxSpreadY = 2
    bulletSpreadAngs = ((0,0), (0.2, 0), (0, 0.2))
    
    #TODO:: offsets
    
    numBullets = 1
    dmgMulPrime = 0.7
    falloffPrime = 0.3
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        base.game_instance.audio.register_sound_source(self.user.name + "as_default", self.user.np, "reload", "defaultShot")
    
    def primaryFire(self):
        super().primaryFire()
        base.game_instance.audio.play(self.user.name + "as_default", "defaultShot")
    
    def trigger_reload(self):
        if not (self._isReloading or self._counting or self._storage <= 0 or self._clip == self.clipSize):
            base.game_instance.audio.play(self.user.name +"as_default", "reload")
        super().trigger_reload()