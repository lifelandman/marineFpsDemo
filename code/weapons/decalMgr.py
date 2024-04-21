
from panda3d.core import CardMaker, NodePath, DepthOffsetAttrib

class decalMgr():
    maxDecals = 35
    
    def __init__(self):
        cm = CardMaker('bulletDecal')
        atrib = DepthOffsetAttrib.make(1)

        cm.set_frame(-0.1,0.1,-0.1,0.1)
        self.bulletDecal = cm.generate()
        self.bulletDecal.set_attrib(atrib)
        DecalBaseNP = NodePath(self.bulletDecal)
        
        self.decals = []
        for i in range(self.maxDecals):
            if i == self.maxDecals:
                break
            decal = NodePath("Decal Instance")
            DecalBaseNP.instance_to(decal)
            #decal.show()
            #decal.set_two_sided(True)
            self.decals.append(decal)
        self._active_decal = 0#this value indicates the next decal we should manipulate. if is bigger than maxDecals, loop back around.
        

    def decal_from_bullet_ray(self, target, entry):
        decal = self.decals[self._active_decal]
        decal.reparent_to(target)
        decal.set_pos(entry.get_surface_point(target))
        normal = entry.get_surface_normal(target)
        decal.set_hpr(0,0,0)#Reset rotation since we're doing a relative transformation
        decal.look_at(decal, -normal)
        decal.show_through()

        self._active_decal += 1
        if self._active_decal == self.maxDecals: self._active_decal = 0
        #render.ls()
        

    def destroy(self):
        for decal in self.decals:
            decal.remove_node()
        del self.bulletDecal