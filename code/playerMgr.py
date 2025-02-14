from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from panda3d.core import NodePath

from .entities.playerNet import clientPlayer, hostNetPlayer, clientNetPlayer

class playerManager(DirectObject):
    
    colors = (#TODO:: actually cycle through this while assigning player colors
        (0.902, 0.275, 1),
        (0.48, 0.63111, 0.986666),
        (0.98, 0.796, 0.365),
        (0.859, 0.3, 0.3)
        )
    
    def __init__(self):
        clientPlayer.update_keybinds(clientPlayer)
        self.gameObj = base.game_instance
        self.playerEnts = []
        self.clientEnt = None#if we ever add split-screen multiplayer, make this a list.
        self.build_players()
        
    def build_players(self):
        players = self.gameObj.lobby.tracker.get_players()
        knownPlayerNames = [player.name for player in self.playerEnts]#I think I'm checking this in case we update our list of players when someone new joins
        
        for playername, pid in players:
            if playername in knownPlayerNames:
                continue
            else:
                match self.gameObj.lobby.tracker.get_team(playername):
                    case "deathMatch": team = 0
                    case "red": team = 1
                    case "blue": team = 2
                    case _: team = 3
                self.add_player(playername, team = team)
            
    def add_player(self, name, team):
        if name == base.game_instance.lobby.tracker.pid_2_name(self.gameObj.lobby.memVal):#We're the local player. ALSO:: Another thing that needs to change with a rework of netTracker
            newP = clientPlayer(name = name, camera = base.camera, team = team, isHost = (base.game_instance.lobby.tracker.get_id(name) == "host"))
            newP.add_colliders(base.cTrav, self.gameObj.handler)
            self.clientEnt = newP
            self.playerEnts.append(newP)
            base.game_instance.hudMgr.register_player(newP)
        else:
            newP = hostNetPlayer(name = name, team = team, netControllableBy = (base.game_instance.lobby.tracker.get_id(name),) ) if base.isHost else clientNetPlayer(name = name, team = team)
            newP.add_colliders(base.cTrav, self.gameObj.handler)
            self.playerEnts.append(newP)
            
    def round_start(self):
        self.spawn_wave()
        self.addTask(self.distribute_players, "distribute players", 100)#his should be right before sending, THE last task.
            
    def spawn_wave(self):
        spawnPoints = self.gameObj.world.find_all_matches('**/=spawnPoint')#TODO:: dynamically add =a or =d
        
        stdPoint = NodePath('fakes')#for emergencies.
        stdPoint.reparent_to(base.render)
        stdPoint.set_z(100)
        
        numPaths = spawnPoints.get_num_paths()
        if numPaths <= 0: defaultPos = True
        else: defaultPos = False
        
        i = 0
        for player in self.playerEnts:
            if player._isSpawned:
                continue
            if defaultPos or i >= numPaths:
                player.spawn(stdPoint)
            else:
                point = spawnPoints.get_path(i)
                player.spawn(point)
            i += 1
        stdPoint.remove_node()
        
    def distribute_players(self, task):
        server = base.server
        if base.isHost:
            for player in self.playerEnts:
                if player.over:
                    if not server.send_direct("expectOveride", self.gameObj.lobby.tracker.get_id(player.name)):
                        continue#something went wrong here. Potentially flag playerEnt rebuild
                    player.over = False
                    if player.isRiding: server.add_message("addRide{" + player.name, (player.riding.name,))#ensure that the player we're overriding is on same page about their parent
                player.interrogate(server)
        else:
            self.clientEnt.interrogate(server)
        return Task.cont
            
    def clear_players(self):
        for ent in self.playerEnts:
            ent.destroy()
        self.playerEnts = []
        self.clientEnt = None
        
    def delete(self):
        self.ignoreAll()
        self.removeAllTasks()
        self.clear_players()
        base.camera.reparent_to(base.render)
        base.camera.set_pos(0,0,0)
        #TODO:: along with the netTracker rework, it would be good to make some functionality for players to rejoin a game if they dissconnect,
        #so we'd tell netTracker that it's okay to flush disconnected players.
        del self.gameObj#gameObj won't garbage collect if we don't delete
                