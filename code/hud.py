
from panda3d.core import TextNode
from direct.showbase.DirectObject import DirectObject


class hudMgr(DirectObject):
    def __init__(self):
        self._healthDisplay = TextNode("health")
        self._healthCount = 0
        self._healthNP = base.a2dBottomRight.attach_new_node(self._healthDisplay)
        self._healthNP.set_scale(0.4)
        self._healthNP.set_pos(-0.7,0,0.1)
    
    def register_player(self, player):
        self._player = player
        self.accept(player.name + "health_change", self.health_change)
        self._healthCount = int(player.health)
        self._healthDisplay.set_text(str(self._healthCount))
    
    def health_change(self):
        intHealth = int(self._player.health)
        if self._healthCount != intHealth:
            self._healthCount = intHealth
            self._healthDisplay.set_text(str(self._healthCount))
    
    def delete(self):
        self._healthNP.remove_node()
        del self._healthDisplay
        del self._healthNP
        del self._healthCount