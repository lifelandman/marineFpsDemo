'''
I've moved all inital processing on a loaded map file to this python file to make game.py easier to read.
World management might be split between this and a more "gameplay-oriented" file later on. In that case,
this file prioritises actually transforming nodepaths to accomedate the model format not supporting a feature. (e.g. water, lights for egg files)
'''
#lighting imports
from panda3d.core import DirectionalLight, AmbientLight
#collision
from panda3d.core import BitMask32
#water
from panda3d.core import CardMaker
from panda3d.core import Shader

def loadWorld(game, worldFile):
    game.world = base.loader.load_model(worldFile)
    game.world.reparent_to(base.render)
        

    collisionNodes = game.world.find_all_matches('**/+CollisionNode')
    if collisionNodes.get_num_paths() <= 0:
        game.world.set_collide_mask(BitMask32(0b1000000))
    else:
        for nodeP in collisionNodes:
            if not nodeP.has_tag("isWater"):
                nodeP.set_collide_mask(BitMask32(0b1000000))
    del collisionNodes
    #TODO:: add plane for falling out of the world
    
    waterNodes = game.world.find_all_matches("**/=isWater")
    print(waterNodes)
    cm = CardMaker('waterSurface')
    shader = Shader.load(Shader.SL_GLSL, vertex = 'shaders/dayWaterVert.vert', fragment = 'shaders/dayWaterFrag.frag')
    waterTex = loader.loadTexture('images/waterNormal.jpg')

    for nodeP in waterNodes:
        if not nodeP.node().is_collision_node():
            continue
        solid = nodeP.node().get_solid(0)
        center = solid.get_center()
        dimensions = solid.get_dimensions()
        hori = dimensions.x/2
        verti = dimensions.y/2
        cm.set_frame(-hori, hori, -verti, verti)
        surface = nodeP.attach_new_node(cm.generate())
        
        surface.set_pos(center.x, center.y, center.z + dimensions.z/2)
        surface.set_p(-90)
        surface.show_through()
        
        surface.set_texture(waterTex)
        surface.set_shader(shader)

    #set up lighting
    base.render.set_shader_auto()
    sun = DirectionalLight("sun")
    sun.setColor((0.8, 0.77, 0.8, 1))
    game.sunNp = base.render.attach_new_node(sun)
    game.sunNp.setHpr(-30, -60, 0)
    base.render.set_light(game.sunNp)
        
    sun = AmbientLight("ambient Light")
    sun.setColor((0.2, 0.2, 0.2, 1))
    game.amLNp = base.render.attach_new_node(sun)
    base.render.set_light(game.amLNp)
    del sun