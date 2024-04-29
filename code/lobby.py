#from genericpath import samefile#Why did I import this?
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from panda3d.core import ConfigVariableString
from .servers.client import clientServer
from .servers.host import hostServer

from math import ceil
from os import listdir, getcwd

from .netTracking import netPlayerTracker
from .game import game_world

class lobby_ui(DirectObject):
    def __init__(self, pmen, isHost, ipAdress = None):
        super().__init__()
        
        self.gameStart = False
        self.in_menu = True
        
        self.tracker = netPlayerTracker()        

        self.pmen = pmen
        self.isHost = isHost
        base.isHost = isHost

        self.pList = []
        self.oList = []
        self.mapList = []
        
        mapDirList = listdir("models/maps")#Eh... I don't really value this always being updated, players should restart after installing new maps anyways.
        self.mapDirList = []
        for file in mapDirList:
            if (file.endswith(".egg") or file.endswith('.bam')):
                self.mapDirList.append(file)
        self.mapDirList = tuple(self.mapDirList)
        del mapDirList
        
        self.build_menu()
        
        self.accept('disconnect', self.remove_player)
        
        if self.isHost:
            self.server = hostServer()
            base.server = self.server
            self.name = ConfigVariableString('my-name', "player").get_string_value()
            self.memVal = "host"
            self.join_player(self.name, "host")
            self.accept("connect", self.connect_player)
        else:
            self.accept("introduce", self.introduce)
            self.accept("kick", self.delete)
            self.accept("exit_session", self.delete)
            self.accept('hostList', self.recieve_players)
            self.accept('playMap', self.play_map)
            self.server = clientServer(ipAdress)
            base.server = self.server
            if not self.server.success:
                print('deleting')
                self.delete()
        
    
    def connect_player(self, name, pid, version):
        if version != base.version:
            base.server.kick(int(pid))
            return

        if self.tracker.join_player(name, int(pid)):
            base.server.send_direct("alias", int(pid), (name, pid))
        else:#try and find a different name
            newName = name + "<" + str(pid)
            if self.tracker.join_player(newName, int(pid)):
                self.server.send_direct("alias", int(pid), (newName, pid))
            else:
                base.server.kick(int(pid))
                
        x = []
        players = self.tracker.get_players()
        for name, index in players:
            x.append(name)
            x.append(str(index))
        while len(x) < 8:
            x.append('')
        x = tuple(x)
        base.server.add_message('hostList', x)
        
        if self.in_menu:
            self.clear_player_list()
            self.make_player_list()
        
    def join_player(self, name, index = None):
        self.clear_player_list()
        self.tracker.join_player(name, index)
        self.make_player_list()
        
    def remove_player(self, index):
        if index == 'host' or (not self.tracker.has_id(index)):
            return
        self.clear_player_list()
        self.tracker.remove_player(int(index))
        if self.in_menu:
            self.make_player_list()
        
    def introduce(self, memVal):
        self.server.add_message("connect", (ConfigVariableString('my-name', "player").get_string_value(), memVal, base.version))
        self.acceptOnce("alias", self.accept_alias)

    def accept_alias(self, name, memVal):
        self.name = name
        self.memVal = memVal
        
    def recieve_players(self, *args):
        counter = 0
        while counter <7:
            if not ((args[counter] == '') or (self.tracker.has_player(args[counter], args[counter+1]))):
                self.tracker.join_player(args[counter], args[counter+1])
            counter += 2
            continue
        if self.in_menu:
            self.clear_player_list()
            self.make_player_list()
        
    def build_menu(self):
        self.player_frame = DirectFrame(frameSize = (-1.3,0.6,0.96,-0.2), frameColor = (0.3,0.3,0.3,1))
        self.map_frame = DirectFrame(frameSize = (0.65,1.3,0.96,-0.96), frameColor = (0.1,0.1,0.1,1))
        self.disconnect = DirectButton(text="disconnect", scale = 0.1, command= self.delete, pos = (-1, 0, -0.93))
        self.make_player_list()
        if self.isHost:
            self.action_label = DirectLabel(text = "please make a selection", text_scale = 0.09, text_pos = (-0.8, -0.02), frameSize = (-1.3, 0.6, 0.07,-0.07), pos = (0, 0, -0.2))
            self.make_map_list()
        else:
            self.action_label = DirectLabel(text = "waiting on host...", text_scale = 0.09, text_pos = (-0.8, -0.02), frameSize = (-1.3, 0.6, 0.07,-0.07), pos = (0, 0, -0.2))
    
    def clear_menu(self):
        self.clear_player_list()
        self.clear_option_list()
        self.clear_map_list()
        self.player_frame.destroy()
        self.map_frame.destroy()
        self.disconnect.destroy()
        self.action_label.destroy()

    def make_player_list(self):
        self.clear_player_list()
        players = self.tracker.get_players()
        if self.isHost:
            count = 1
            for player, index in players:
                if index == "host":
                    self.pList.append(self.player_label(player, count))
                else:
                    self.pList.append(self.player_button(player, count))
                count +=1
        else:
            count = 1
            for player, index in players:
                name = player.split("<")[0]
                self.pList.append(self.player_label(name, count))
                count +=1
                
    def clear_player_list(self):
        for i in self.pList:
            i.destroy()
        self.pList = []
        
    def clear_option_list(self):
        for i in self.oList:
            i.destroy()
        self.oList = []

    def player_label(self, name, count):
        #Create a label for joining players
        row = ceil(count/2)
        col = count%2
        return DirectLabel(text = name, parent = self.player_frame, text_scale = 0.09, pos = (0.124 - (col * 0.95), 0, 1.02 -(row*0.12)), frameSize = (-0.465, 0.465, -0.05, 0.05), text_pos = (0,-0.02))
        
    def player_button(self, name, count):#create a button for players; for server host
        row = ceil(count/2)
        col = count%2
        ret = DirectButton(text = name, parent = self.player_frame, text_scale = 0.09, pos = (0.124 - (col * 0.95), 0, 1.02 -(row*0.12)), frameSize = (-0.465, 0.465, -0.05, 0.05), text_pos = (0,-0.03), command = self.set_options_player, extraArgs = [name,])
        return ret
        
    def set_options_player(self, name):
        self.clear_option_list()
        self.action_label.setText("managing " + name + ":")
        self.oList = [DirectButton(text = "kick", text_scale = 0.09, pos = (-0.826, 0, -0.35), frameSize = (-0.465, 0.465, -0.05, 0.05), text_pos = (0,-0.03), command = self.kick_player, extraArgs = [name, self.tracker.get_id(name)])
            ]
        
    def set_options_map(self, name):
        self.clear_option_list()
        self.action_label.setText("map: " + name)
        self.oList = [DirectButton(text = "play", text_scale = 0.09, pos = (-0.826, 0, -0.35), frameSize = (-0.465, 0.465, -0.05, 0.05), text_pos = (0,-0.03), command = self.play_map, extraArgs = [name])
            ]
        
    def make_map_list(self):
        self.clear_map_list()
        count = 0
        for file in self.mapDirList:
            if count >4:
                break
            self.mapList.append(DirectButton(text = file, parent = self.map_frame, pos = (0.975, 0, 0.7 - (0.45*count)), text_scale = 0.09, text_pos = (0,-0.03), frameSize = (-0.29, 0.29, -0.2, 0.2),
                                             borderWidth = (0.05,0.05), command = self.set_options_map, extraArgs = [file]))
            count +=1
                
    def clear_map_list(self):
        for i in self.mapList:
            i.destroy()

    def kick_player(self, name, index):
        if self.isHost:
            self.server.kick(index)
            self.remove_player(index)
            self.clear_option_list()
            self.action_label.setText(name + " has been kicked")
            
    def play_map(self, mapfile):
        if self.isHost:
            self.server.add_message('playMap', (mapfile,))
        self.clear_menu()
        self.in_menu = False#tells us if the menu is open
        if self.gameStart:
            self.game.destroy()
        else: self.gameStart = True
        self.game = game_world(self, "maps/" + mapfile)
        self.accept(ConfigVariableString('pause', 'escape').get_string_value(), self.toggle_menu)
        
    def toggle_menu(self):
        if self.in_menu == True:
            self.clear_menu()
            self.in_menu = False
            scSize = base.win.getProperties()
            xSize, ySize = scSize.get_x_size() // 2, scSize.get_y_size() // 2
            base.win.movePointer(0, xSize, ySize)
        elif self.in_menu == False:
            self.build_menu()
            self.in_menu = True

    def delete(self):
        self.clear_menu()
        
        del base.isHost
        
        if self.gameStart:
            self.game.destroy()
            if self.isHost:
                self.server.add_message('exit_session')
        
        del base.server
        self.server.shut_down()
        
        self.pmen.build_menu()
        del self.pmen
        self.ignoreAll()