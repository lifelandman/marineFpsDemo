from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file, TextNode
from code.main_menu import menu_ui


class game(ShowBase):
    def __init__(self, indirectStart = True):
        ShowBase.__init__(self)
        load_prc_file("gameConfig.prc")
        self.optionPage = load_prc_file("options.prc")#Need a handle on this ConfigPage for saving modifications to it
        base.disableMouse()
        
        #load_prc_file("gameConfig.prc")

        globalClock.set_average_frame_rate_interval(1.0)

        #messenger.toggleVerbose()
        self.setFrameRateMeter(True)
        self.menu = menu_ui(indirectStart)



if __name__ == "__main__":
    myGame = game()
    myGame.run()
