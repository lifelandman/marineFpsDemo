from panda3d.core import ConfigVariableString

keybinds = [
    
    ConfigVariableString('move-forward', 'w'),
    ConfigVariableString('move-backward', 's'),
    ConfigVariableString('move-left', 'a'),
    ConfigVariableString('move-right', 'd'),
    
    ConfigVariableString('jump', 'space'),
    ConfigVariableString('crouch', 'shift'),
    
    ConfigVariableString('pause', 'escape'),
    
    ConfigVariableString('fire1', 'mouse1'),
    ConfigVariableString('fire2', 'mouse3'),#This is right click
    ConfigVariableString('reload', 'r'),
    
    ConfigVariableString('changeWpn-up', 'wheel_up'),
    ConfigVariableString('changeWpn-down', 'wheel_down'),

    
    ]

textOps = [
    ConfigVariableString('my-name', 'player'),
    ]