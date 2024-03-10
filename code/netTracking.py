from direct.showbase.DirectObject import DirectObject

class netPlayerTracker(DirectObject):
    def __init__ (self):
        self.names = []#Coorispond a player name with connection id
        
        self.ids = []#Player names <-> Functional Id's
        
    def join_player (self, name, index):
        if len(self.names) >=4:
            return False
        if (name not in self.names) and (index not in self.ids):
            self.names.append(name)
            self.ids.append(index)
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
    
    def delete(self):
        self.ignoreAll()
        del self.names
        del self.ids