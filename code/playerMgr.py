from direct.showbase.DirectObject import DirectObject
from direct.task import Task

class playerManager(DirectObject):
    
    colors = (#TODO:: actually cycle through this while assigning player colors
        (0.902, 0.275, 1),
        (0.48, 0.63111, 0.986666),
        (0.98, 0.796, 0.365),
        (0.859, 0.3, 0.3)
        )
    
    def __init__(self):
        pass
            
    def delete(self):
        self.ignoreAll()
                