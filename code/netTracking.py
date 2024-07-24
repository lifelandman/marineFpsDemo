from direct.showbase.DirectObject import DirectObject

class netPlayerTracker(DirectObject):
    def __init__ (self):
        self.names = []#Coorispond a player name with connection id
        
        self.teams = {"deathMatch":[],"red":[],"blue":[],"PvE":[]}#Null, Red, Blue
        
        self.ids = []#Player names <-> Functional Id's
        
    def join_player (self, name, index):
        if len(self.names) >=4:
            return False
        if (name not in self.names) and (index not in self.ids):
            self.names.append(name)
            self.ids.append(index)
            self.teams["deathMatch"].append(name)
        else: return False
        return True
    
    def remove_player(self, index):
        pos = self.ids.index(index)
        self.ids.pop(pos)
        self.names.pop(pos)
        
    def pid_2_name(self, index):
        return self.names[self.ids.index(index)]
    
    def get_players(self):#Rewrite code that uses this
        return zip(self.names, self.ids)
    
    def get_id(self, name):
        return self.ids[self.names.index(name)]
    
    def has_player(self, name, playerNum):
        if playerNum in self.ids and name in self.names:
            if self.ids[self.names.index(name)] == playerNum:
                return True
        return False
    
    def has_id(self, pid):
        if isinstance(pid, str) and pid.isdigit():
            index = int(pid)
        else: index = pid
        if index in self.ids:
            return True
        else:
            return False
        
    def ready_test(self, input):
        if len(input) == len(self.ids):
            return True
        else: return False
        
    ##############
    #Team Sorting#
    ##############
    
    def sort_teams_rb(self):
        if not base.isHost: return
        if len(self.teams["deathMatch"]) + len(self.teams["PvE"]) != 0:
            while len(self.teams["deathMatch"]) !=0:
                if len(self.teams["red"]) < len(self.teams["blue"]):
                    self.teams["red"].append(self.teams["deathMatch"][0])
                else:
                    self.teams["blue"].append(self.teams["deathMatch"][0])
                self.teams["deathMatch"].pop(0)
                
            while len(self.teams["PvE"]) !=0:
                if len(self.teams["red"]) < len(self.teams["blue"]):
                    self.teams["red"].append(self.teams["PvE"][0])
                else:
                    self.teams["blue"].append(self.teams["PvE"][0])
                self.teams["PvE"].pop(0)
        
        rlen = len(self.teams["red"])
        blen = len(self.teams["blue"])
        if abs(rlen - blen) >= 2:
            if rlen > blen:
                self.teams["blue"].append(self.teams["red"][-1])
                self.teams["red"].pop(-1)
            else:
                self.teams["red"].append(self.teams["blue"][-1])
                self.teams["blue"].pop(-1)
        self.announce_teams()
                
    def sort_teams_deathmatch(self):
        if not base.isHost: return
        deathMatch = self.teams["deathMatch"]
        for team in self.teams:
            if team == "deathMatch":
                continue
            for player in self.teams[team]:
                if not player in deathMatch:
                    deathMatch.append(player)
                    self.teams[team].remove(player)
            team = []
        self.announce_teams()
            
    def get_team(self, name:str):
        for team in self.teams:
            if name in self.teams[team]:
                return team
        return False
    
    def change_team(self, name:str, toTeam:str):
        fromTeam = self.get_team(name)
        if fromTeam == toTeam: return
        self.teams[toTeam].append(name)
        self.teams[fromTeam].remove(name)
        if base.isHost: base.server.add_message("changeTeam", (name,toTeam))
        
    def announce_teams(self):
        for team in self.teams:
            for player in self.teams[team]:
                base.server.add_message("changeTeam", (player, team))
        base.server.add_message("sortedTeams")
    
    def delete(self):
        self.ignoreAll()
        del self.names
        del self.ids