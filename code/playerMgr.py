from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from .entities.playerEnts import clientPlayer, networkedPlayer

class playerManager(DirectObject):
    
    colors = (#TODO:: actually cycle through this while assigning player colors
        (0.902, 0.275, 1),
        (0.48, 0.63111, 0.986666),
        (0.98, 0.796, 0.365),
        (0.859, 0.3, 0.3)
        )
    
    def __init__(self, gameObj):
        self.gameObj = gameObj
        self.playerEnts = []
        
    def build_players(self):
        players = self.gameObj.lobby.tracker.get_players().keys()#Note:: if we change how the netTracker works, we need to change this as well.
        knownPlayerNames = [player.name for player in self.playerEnts]
        
        for playerName in players:
            if playerName in knownPlayerNames:
                continue
            else: self.add_player()
            
    def add_player(self, name):
        if name == self.gameObj.lobby.tracker.pid_2_name(self.gameObj.lobby.memVal):#We're the local player. ALSO:: Another thing that needs to change with a rework of netTracker
            newP = clientPlayer(name = name, camera = base.camera)
            self.playerEnts.append(newP)
        else:
            self.playerEnts.append(networkedPlayer(name = name))
            
    def round_start(self):
        pass
            
    def delete(self):
        self.ignoreAll()
        base.camera.reparent_to(base.render)
        #TODO:: along with the netTracker rework, it would be good to make some functionality for players to rejoin a game if they dissconnect,
        #so we'd tell netTracker that it's okay to flush disconnected players.
        del self.gameObj#gameObj won't garbage collect if we don't delete
                