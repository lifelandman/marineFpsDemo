
lensClamp = lambda val: -1 + (val - 1) if val >= 1 else val

from code.weapons.wpnSlots import slotMgr
from .wpnAmmo import ammoWeapon
from .damageTypes import bulletDamageType, damageTypeBase

from panda3d.core import CollisionRay, CollisionNode, CollisionTraverser
from panda3d.core import BitMask32 as BitMask
from panda3d.core import CollisionHandlerQueue

class bulletWeapon(ammoWeapon):
    maxSpreadX = 30#out of 100
    maxSpreadY = 20
    
    bulletFovX = 60
    bulletFovY = 60
    offsetY = 0.3
    offsetZ = -0.2
    #int((gameSharedRandom * Maximum) >> 31)
    #so basically ((int(gameSharedRandom * maxSpreadX) >> 31) - 0.5*maxSpreadX)/100
    
    numBullets = 3
    
    dmgMulPrime = 1
    dmgMulSec = 1
    falloffPrime = 1
    falloffSec = 1
    
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
        self.user._bulletLens.set_fov(self.bulletFovX, self.bulletFovY)
        

    def raycast(self, damageType: damageTypeBase, mul, falloff):#We accept damageType as a variable for guns like the tranq gun
        x = ((int(base.gameSharedRandom * self.maxSpreadX) >> 31) - 0.5*self.maxSpreadX)/100
        y = ((int(base.gameSharedRandom * self.maxSpreadY) >> 31) - 0.5*self.maxSpreadY)/100
        xover = 0#rockman joke hue hue hue
        yover = 0
        avgX, avgY = 0,0#the number less close to zero determines which overflow variable gets increased.
        for rayNP in self.rays:
            ray = rayNP.node().modify_solid(0)
            
            x = lensClamp(x + xover)
            y = lensClamp(y + yover)
            ray.set_from_lens(self.user._bulletNode, x, y)
            avgX, avgY = x+avgX/2, y+avgY/2#calc new averages.
            if abs(avgX) < abs(avgY):#only change one at a time. A: this lets us ensure more variation, B: it ensures we will never have two bullets on the same point.
                xover += x/3
                if xover >= self.maxSpreadX/100: xover = 0
            else:
                yover += y/3
                if yover >= self.maxSpreadY/100: yover = 0
            x = x + xover
            y = y + yover
            

        self.trav.traverse(base.game_instance.world)
        bulletWeapon.queue.sort_entries()
        
        hit_bullets = []
        for entry in bulletWeapon.queue.get_entries():
            if not entry.collided():
                intoNP = entry.get_into_node_path()
                if entry.get_from_node_path() in hit_bullets:#we can assume that we've gotten past all the first collisions.
                    break
                if intoNP.get_tag("player") == self.user.name:
                    continue
                if base.isHost and intoNP.has_tag("player"):
                    damage = damageType(intoNP.get_tag("player"))
                    damage.calc_from_rayCast(entry, mul = mul, falloff = falloff)
                    damage.apply(intoNP.get_python_tag('entOwner'))
                    damage.serialize()
                base.game_instance.decalMgr.decal_from_bullet_ray(intoNP, entry)
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