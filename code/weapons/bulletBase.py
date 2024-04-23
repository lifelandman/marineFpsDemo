
lensClamp = lambda val: -1 + (val - 1) if val >= 1 else val

from code.weapons.wpnSlots import slotMgr
from .wpnAmmo import ammoWeapon
from .damageTypes import bulletDamageType, damageTypeBase

from panda3d.core import CollisionRay, CollisionNode, CollisionTraverser
from panda3d.core import BitMask32 as BitMask
from panda3d.core import CollisionHandlerQueue
from panda3d.core import Mersenne as rng#max 2,147,483,647

class bulletWeapon(ammoWeapon):
    maxSpreadX = 4#In degrees
    maxSpreadY = 2.5
    
    bulletSpreadAngs = [(0,1.4),#A list of base rotations for bullets to cycle through. can be bigger than num bullets
                       (-1.2,0),(0,0),(1.2,0),
                       (0,-1.4)]
    
    offsetY = 0.5
    offsetZ = 0.2
    #int((gameSharedRandom * Maximum) >> 31)
    #so basically ((int(gameSharedRandom * maxSpreadX) >> 31) - 0.5*maxSpreadX)/100
    
    numBullets = 4
    
    dmgMulPrime = 1
    dmgMulSec = 1
    falloffPrime = 0.5
    falloffSec = 0.5
    
    queue = CollisionHandlerQueue()
    
    hasAltFire = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        #create casting rays
        self.rays = []
        count = 0
        while count < self.numBullets:
            cNode = CollisionNode("rayCast")
            cNode.add_solid(CollisionRay(0,0,0,0,1,0))
            self.rays.append(self.user._bulletNP.attach_new_node(cNode))
            cNode.set_from_collide_mask(BitMask(0b1001010))
            cNode.set_into_collide_mask(BitMask(0))
            count += 1
        self.trav = CollisionTraverser(self.user.name +"weapon traverser")
        for rayNP in self.rays:
            self.trav.add_collider(rayNP, bulletWeapon.queue)
            rayNP.show()
        

    def activate(self, mgr: slotMgr):
        super().activate(mgr)
        ##Move bulletNP
        self.user._bulletNP.set_y(self.offsetY)
        self.user._bulletNP.set_z(self.offsetZ)
    
        
    def raycast(self, damageType: damageTypeBase, mul, falloff):#We accept damageType as a variable for guns like the tranq gun
        maxBases = len(self.bulletSpreadAngs)
        subRng = rng(base.gameSharedRandom)
        subSeed = base.gameSharedRandom
        newOffSet = lambda spread: ((int(subSeed * spread) >> 31) - 0.5*spread)
        xOffSet = newOffSet(self.maxSpreadX)
        yOffSet = newOffSet(self.maxSpreadY)
        bulletAngCount = int(maxBases * subSeed) >> 31
        for rayNP in self.rays:            
            baseAngle = self.bulletSpreadAngs[bulletAngCount]
            x = baseAngle[0] + xOffSet
            y = baseAngle[1] + yOffSet
            bulletAngCount = bulletAngCount + 1 if bulletAngCount < maxBases - 1 else 0
            subSeed = subRng.get_uint31()
            xOffSet = newOffSet(self.maxSpreadX)
            yOffSet = newOffSet(self.maxSpreadY)
            
            rayNP.set_h(x)
            rayNP.set_p(y)
            
        self.trav.traverse(base.game_instance.world)
        bulletWeapon.queue.sort_entries()
        
        hit_bullets = []
        for entry in bulletWeapon.queue.get_entries():
            if not entry.collided():
                intoNP = entry.get_into_node_path()
                if entry.get_from_node_path() in hit_bullets:#we can assume that we've gotten past all the first collisions.
                    #break
                    pass
                if intoNP.has_net_tag("player"):
                    if intoNP.get_net_tag("player") == self.user.name:
                        continue
                    damage = damageType(intoNP.get_net_tag("player"), self.user.name)
                    damage.calc_from_rayCast(entry, mul = mul, falloff = falloff)
                    intoNP.find_net_tag("player").get_net_python_tag('entOwner').take_damage(damage)
                else: base.game_instance.decalMgr.decal_from_bullet_ray(intoNP, entry)
            hit_bullets.append(entry.get_from_node_path())
        

    def primaryFire(self):
        self.raycast(bulletDamageType, self.dmgMulPrime, self.falloffPrime)
        
    def secondaryFire(self):#this isn't accesible by default
        self.raycast(bulletDamageType, self.dmgMulSec, self.falloffSec)


    def destroy(self):
        super().destroy()
        self.trav.clear_colliders()
        for ray in self.rays:
            ray.remove_node()
        del self.trav