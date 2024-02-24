from direct.showbase.DirectObject import DirectObject

class netPlayerTracker(DirectObject):#TODO:: indecies are not used outside of a handfull of circumstances, usually by the host. this and lobby should be rewritten for better memory usage.
    def __init__ (self):#ALTERNATIVELY:: Just rewrite this to be more legible/usefull. Ids can be used for shortening datagram strings sent over a network, after all.
        #actualRef might not even be neccisary, but unless I can confirm everything
        #can be written without needing some hacky index correction for the host player, it stays.
        #AFTERTHOUGHT: maybe I can get away with the host's index being something like -1? as a kind of psudo-index.
        #FINALE: host player should consistantly be player host. Now, to figure out how to go about giving clients their own numbers...
        self.names2ids = {}#Coorispond a player name with connection id
        
        self.ids2names = {}#Player names <-> Functional Id's
    
        
    def join_player (self, name, index):
        if len(self.ids2names) >=4:
            return False
        if (name not in self.ids2names.values()) and (index not in self.ids2names.keys()):
            self.names2ids[name] = index
            self.ids2names[index] = name
        else: return False
        return True
    
    def remove_player(self, index):
        name = self.ids2names[index]
        self.ids2names.pop(index)
        self.names2ids.pop(name)
        
    def check_order(self, namme, index, pos):
        pass
        
    
    def pid_2_name(self, index):
        return self.names2ids[index]
    
    
    def get_names_minus_host(self):
        l = []
        for i, k in self.ids2names:
            if str(i) == "host":
                continue
            l.append(k)
        return l
    
    def get_players(self):
        return self.names2ids
    
    def get_id(self, name):
        return self.names2ids[name]
    
    def has_player(self, name, playerNum):
        if playerNum in self.ids2names and name in self.names2ids:
            if self.names2ids[name] == playerNum:
                if self.names2ids[name] == playerNum:
                    return True
        return False
    
    def has_id(self, pid):
        if isinstance(pid, str) and pid.isdigit():
            index = int(pid)
        else: index = pid
        if index in self.ids2names.keys():
            return True
        else:
            return False
    
    def delete(self):
        self.ignoreAll()
        del self.names2ids
        del self.ids2names