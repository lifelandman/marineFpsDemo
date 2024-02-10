'''
Superlong document with all 'func' entities, for now.
directory:
-movement funcs
--funcSpin
'''

from .npEnt import *
from direct.task import Task
######################MOVEMENT FUNCS#######################

class funcSpin(npEnt):
    
    def spin(self, task):#TODO:: why is task object not being given to us?? why??? :(((
        deltaTime = globalClock.get_average_frame_rate()#TODO:: we'll have to see if getting deltaTime in all appropriate func entities causes a performance inpact. Too bad!
        self.np.set_h(self.np, self.turn/deltaTime)
        return Task.cont
    
    tasks = (('spinNp', 'spin'),
             )#if npEnt had any tasks, we would put 'x for x in npEnt.tasks' here.
    
    turn = 100#how many units to turn per second on average
    
