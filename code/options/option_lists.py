from panda3d.core import ConfigVariableString

keybinds = [
    
    ConfigVariableString('move-forward', 'w'),
    ConfigVariableString('move-backward', 's'),
    ConfigVariableString('move-left', 'arrow_left'),
    ConfigVariableString('move-right', 'arrow_right'),
    ConfigVariableString('turn-left', 'a'),
    ConfigVariableString('turn-right', 'd'),
    
    ConfigVariableString('jump', 'space'),
    ConfigVariableString('crouch', 'shift'),
    
    ConfigVariableString('pause', 'escape'),

    
    ]

textOps = [
    ConfigVariableString('my-name', 'player'),
    ]