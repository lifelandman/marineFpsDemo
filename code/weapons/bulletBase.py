


def bulletWeapon():
    maxSpreadX = 30#out of 100
    maxSpreadY = 20
    
    weaponFov = 75
    #int((gameSharedRandom * Maximum) >> 31)
    #so basically ((int(gameSharedRandom * maxSpreadX) >> 31) - 0.5*maxSpreadX)/100
    
    num_bullets = 1
    
