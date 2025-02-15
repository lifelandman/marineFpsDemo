'''
This file contains functions that create subclasses of the playerEnt class in order to make networking work.
The reason these subclasses are defined in functions is so that they can be derived from another subclass of playerent down the line
without using multiple inheritance or redefining them for every new subclass.

To give an example of where this is nessicary, say you were making a game similar to Team Fortress 2. To implement every class's different sizes and traits,
you create a subclass of playerEnt. Then, you can simply create networking variants of these subclasses with

engineerClientPlayer = make_client_player_class(engineer)
'''


###panda3d's:
from panda3d.core import NodePath
from panda3d.core import Point3
#Tasks:
from direct.task import Task
###Math:
from math import isclose
from ..weapons.damageTypes import damageTypeBase

##Ours
from .playerEnts import playerEnt

######################\
#####client player#####
######################/      


from panda3d.core import ConfigVariableString
from panda3d.core import WindowProperties

class clientPlayer(playerEnt):
    
    over = False#cheap hack to save a logic check in playerMgr


        

    def __init__(self, camera, **kwargs):
        super().__init__(**kwargs)
        self.camera = camera#See spawn and de_spawn below.
        self._inputActive = False
        self.accept(self.key_pause, self.toggle_inputs)#GRahhh! should player classes even be entities?
        
        if not base.isHost:
            self.accept("expectOveride", self.oRTrig)
            self.accept("kill{" + self.name, self.die)
            self.accept("playerHealthChange{" + self.name, self.change_health)
        
        #unique graphical stuff
        self.model.np.hide()
        
    def oRTrig(self):#override trigger
        self.acceptOnce('playData{' + self.name, self.storeProps)
        
    def storeProps(self, val):
        self.velocity.set_x(val[6])
        self.velocity.set_y(val[7])
        self.velocity.set_z(val[8])
        if not isclose(self._rig.get_h(), val[9], rel_tol = 1) :self.np.set_h(val[9])
        if not isclose(self._rig.get_p(), val[10], rel_tol = 1) :self._rig.set_p(val[10])
        self.np.set_pos(val[11],val[12],val[13],)
        self._isAirborne = val[14]
        self._isCrouched = val[15]
        
    def toggle_inputs(self):
        if self._inputActive:
                self.removeTask('key-input task')
             
                props = WindowProperties()
                props.set_cursor_hidden(False)
                '''
                props.set_mouse_mode(WindowProperties.M_relative)#These don't work on windows. TODO:: detect if we're on a os that can do this, and use these instead.
                '''
                base.win.requestProperties(props)
             

                self.ignore(self.key_wpnUp)
                self.ignore(self.key_wpnDown)
             
             
                self._inputActive = False
        else:
            self.addTask(self.get_inputs_keys, 'key-input task', sort =5)#it's awkward that we're controlling tasks like this and not through the entity system that was made for this purpose, but because players will spawn and despawn frequently
            
            props = WindowProperties()#See above.
            props.set_cursor_hidden(True)
            #reset mouse pos
            pointer = base.win.get_pointer(0)
            if pointer.get_in_window():
                scSize = base.win.getProperties()
                xSize, ySize = scSize.get_x_size() // 2, scSize.get_y_size() // 2
                base.win.movePointer(0, xSize, ySize)
            '''
            props.set_mouse_mode(WindowProperties.M_absolute)#see above.
            '''
            base.win.requestProperties(props)
            
            self.accept(self.key_wpnUp, self.changeWpn, [1,])
            self.accept(self.key_wpnDown, self.changeWpn, [-1,])
            
            
            self._inputActive = True
    
    def spawn(self, sPoint: NodePath):
        super().spawn(sPoint)
        self.camera.reparent_to(self._rig)#If the camera isn't connected to the same node tree as geometry, geometry won't render. It'd be awkward to have even a moment where the camera is rendering a blank, so we detatch it here.
        self.camera.set_pos_hpr(0,0,0,0,0,0)
        self.addTask(self.update, 'client_mover', sort = 10)#We have no choice but to do this so as to lighten the frame-time when the client player isn't spawned.
        self.toggle_inputs()
        
    
    def de_spawn(self):
        super().de_spawn()
        self.camera.reparent_to(base.render)
        if self._inputActive:
            self.toggle_inputs()
        self.removeAllTasks()#Carefull!
    
    #Defining button inputs as member variables. (same among all instances.)
    #They are then redefined inside a function to update them once the game starts. (if we set the keybind strings in the member declarations, they will be set immediately as the file is imported and unchanged if the user changes the keybinds.)
    #If splitscreen multiplayer ever becomes important for some reason, these need to be changed to instance variables.
    key_for = None
    key_bak = None
    key_left = None
    key_right = None
    
    key_jump = None
    key_crouch = None
    
    key_pause = None
    
    key_fire1 = None
    key_fire2 = None
    key_reload = None
    
    key_wpnUp = None
    key_wpnDown = None
    def update_keybinds(self):
        clientPlayer.key_for = ConfigVariableString('move-forward', 'w').get_string_value()
        clientPlayer.key_bak = ConfigVariableString('move-backward', 's').get_string_value()
        clientPlayer.key_left = ConfigVariableString('move-left', 'a').get_string_value()
        clientPlayer.key_right = ConfigVariableString('move-right', 'd').get_string_value()
        
        clientPlayer.key_jump = ConfigVariableString('jump', 'space').get_string_value()
        clientPlayer.key_crouch = ConfigVariableString('crouch', 'shift').get_string_value()
        
        clientPlayer.key_pause = ConfigVariableString('pause', 'escape').get_string_value()
        
        clientPlayer.key_fire1 = ConfigVariableString('fire1', 'mouse1').get_string_value()
        clientPlayer.key_fire2 = ConfigVariableString('fire2', 'mouse3').get_string_value()
        clientPlayer.key_reload = ConfigVariableString('reload', 'r').get_string_value()
        
        clientPlayer.key_wpnUp = ConfigVariableString('changeWpn-up', 'wheel_up').get_string_value()
        clientPlayer.key_wpnDown = ConfigVariableString('changeWpn-down', 'wheel_down').get_string_value()
    
    
    
    def get_inputs_keys(self, task):#We need a diffrent function if we ever want to add controller support
        poller = base.mouseWatcherNode
        
        self._yMove = poller.is_button_down(self.key_for) - poller.is_button_down(self.key_bak)
        self._xMove = poller.is_button_down(self.key_right) - poller.is_button_down(self.key_left)
        
        self._wantJump = poller.is_button_down(self.key_jump)
        self._wantCrouch = poller.is_button_down(self.key_crouch)
        
        if poller.is_button_down(self.key_fire1): self._wpnFire = 1
        elif poller.is_button_down(self.key_fire2): self._wpnFire = 2
        else: self._wpnFire = 0
        
        if poller.is_button_down(self.key_reload): messenger.send('reload{' + self.name)
        
        if poller.is_button_down(self.key_wpnUp):
            self.wpnMgr.change_weapon(1)
            self._changeWpn = True
        elif poller.is_button_down(self.key_wpnDown):
            self.wpnMgr.change_weapon(-1)
            self._changeWpn = True
        
        pointer = base.win.get_pointer(0)
        if pointer.get_in_window():#Get mouse movement
            scSize = base.win.getProperties()
            xSize, ySize = scSize.get_x_size() // 2, scSize.get_y_size() // 2
            yScalar = xSize/ySize#Try to correct for differences in aspect ratio
            self._hRot, self._pRot = -((pointer.get_x() - xSize)/2) * 0.4, -((pointer.get_y() - ySize) /(2*yScalar)) * 0.4*yScalar
            base.win.movePointer(0, xSize, ySize)
        else: self._hRot, self._pRot = 0,0
        return Task.cont
    

    def changeWpn(self, val):
        self.wpnMgr.change_weapon(val)
        self._changeWpn = True
    
    def take_damage(self, damage: damageTypeBase):
        super().take_damage(damage)
        messenger.send(self.name + "health_change")
        
    def die(self, cause):
        super().die(cause)
        if base.isHost:
            base.server.add_message("kill{" + self.name, (cause,))
            
    def add_weapon(self, wpnType, **kwargs):
        super().add_weapon(wpnType, **kwargs, isClient = True)
        
    
    def update(self, task = None):#TODO:: add a function inside slotMgr that checks if active weapon is a triggerWpn
        if self._wpnFire:
            self.fire(self._wpnFire)
        return super().update(task)
    
    def destroy(self):
        if self._inputActive:
            self.toggle_inputs()
        #self.ignoreAll()
        super().destroy()
        
def make_client_player_class(base_class = playerEnt):
    class newClientPlayer(base_class, clientPlayer):
        pass
    return newClientPlayer


########################\
#####host net player#####
########################/

class hostNetPlayer(playerEnt):#(player._yMove, _xMove, _wantJump, _wantCrouch, _hRot, _pRot, vX,vY,vZ,h,p,x,y,z,is_airborne)

    net_commands = (("kill", "string", 1),
        )

    host_net_commands = ("kill")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.addTask(self.checkMove, self.name + 'check movement', sort = 10)
        self.accept('playData{' + self.name, self.storePDat)
        self.accept('fire{' + self.name, self.fire)
        self.accept('changeWpn{' + self.name, self.set_weapon)
        self.pDat = None
        self.over = False
        
    def storePDat(self, val):
        self.pDat = val
        
    def checkMove(self, taskobj):
        if self.pDat:
            self._yMove = self.pDat[0]
            self._xMove = self.pDat[1]
            self._wantJump = self.pDat[2]
            self._wantCrouch = self.pDat[3]
            self._hRot = self.pDat[4]
            self._pRot = self.pDat[5]
            
            self.update()
            if ((self._isAirborne == self.pDat[14]) and
                    (self._isCrouched == self.pDat[15]) and
                    self.np.get_pos().almost_equal(Point3(self.pDat[11],self.pDat[12],self.pDat[13]), 0.05) and
                    isclose(self.pDat[9], self.np.get_h(), rel_tol = 1) and
                    isclose(self.pDat[10], self._rig.get_p(), rel_tol = 1)):

                if self.velocity.almost_equal(Point3(self.pDat[6], self.pDat[7], self.pDat[8]), 0.05):
                    self.velocity.set_x(self.pDat[6])
                    self.velocity.set_y(self.pDat[7])
                    self.velocity.set_z(self.pDat[8])
                    
                self.np.set_h(self.pDat[9])
                self._rig.set_p(self.pDat[10])
                self.model.set_look(self._rig.get_p())
                
                self.np.set_pos(self.pDat[11],self.pDat[12],self.pDat[13],)
                
                self._isAirborne = self.pDat[14]
                
                if self._isCrouched != self.pDat[15]:
                    if self._isCrouched:
                        self.uncrouch()
                    else:
                        self.crouch
            else:
                self.over = True#Force client into accurate position
            self.pDat = None
        else: self.update()
        return Task.cont

    '''#Function for testing causes of networking bumpiness
    def checkOver(self):
        print(self._isAirborne == self.pDat[14])
        print(self.np.get_pos().almost_equal(Point3(self.pDat[11],self.pDat[12],self.pDat[13])), 0.05)
        print(isclose(self.pDat[9], self.np.get_h(), rel_tol = 1))
        print(isclose(self.pDat[10], self._rig.get_p(), rel_tol = 1))
        print(self._pRot)
        print('next Frame')
    '''
    
    def take_damage(self, damage: damageTypeBase):
        super().take_damage(damage)
        if self.health > 0:
            base.server.add_message("playerHealthChange{" + self.name, (self.health,))#TODO:: figure this out.
        
    def die(self, cause):
        super().die(cause)
        base.server.add_message("kill{" + self.name, (cause,))

    
    def fire(self, fireVal):
        self._wpnFire = fireVal
        super().fire(fireVal)
        
    def set_weapon(self, slot, priority):
        self.wpnMgr.goto_subSlot(slot, priority)


def make_host_net_player_class(base_class = playerEnt):
    class newNetPlayer(base_class, hostNetPlayer):
        pass
    return newNetPlayer
        

##########################\
#####client net player#####
##########################/

class clientNetPlayer(playerEnt):#This one doesn't check to see if movement seems legit nor sends out instructions.
    over = False#This might not be nessisary???
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.addTask(self.Move, self.name + 'move', sort = 10)
        self.accept('playData{' + self.name, self.storePDat)
        
        self.accept('kill{' + self.name, self.die)
        
        self.accept('fire{' + self.name, self.fire)
        self.accept('changeWpn{' + self.name, self.set_weapon)
        
        self.accept("playerHealthChange{" + self.name, self.change_health)
        self.pDat = None
        
    def storePDat(self, val):
        self.pDat = val
        
    def Move(self, taskobj):
        if self.pDat:
            self._yMove = self.pDat[0]
            self._xMove = self.pDat[1]
            self.model.walk(self._xMove, self._yMove)
            
            self._wantJump = self.pDat[2]
            self._wantCrouch = self.pDat[3]
            
            self._hRot = self.pDat[4]
            self._pRot = self.pDat[5]
            
            self.velocity.set_x(self.pDat[6])
            self.velocity.set_y(self.pDat[7])
            self.velocity.set_z(self.pDat[8])
            
            self.np.set_h(self.pDat[9])
            self._rig.set_p(self.pDat[10])
            self.model.set_look(self._rig.get_p())
            
            self.np.set_pos(self.pDat[11],self.pDat[12],self.pDat[13])
            self._isAirborne = (self.pDat[14])
            if self._isCrouched != self.pDat[15]:
                if self._isCrouched:
                    self.uncrouch()
                else:
                    self.crouch

            self.pDat = None
        else:self.update()
        return Task.cont
        

    def set_weapon(self, slot, priority):
        self.wpnMgr.goto_subSlot(slot, priority)

def make_client_net_player_class(base_class = playerEnt):
    class newNetPlayer(base_class, clientNetPlayer):
        pass
    return newNetPlayer