

from .bulletBase import bulletWeapon
from .wpnAmmo import ammoWeapon

class as_default(bulletWeapon, ammoWeapon):
    ##TriggerWait
    wait = 0.2
    
    ##ammo:
    loadWait = 1.5
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
    