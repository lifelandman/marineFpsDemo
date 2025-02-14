from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file, TextNode


class game(ShowBase):
    
    version = '.2'#This is used by lobby to prevent connection between diffrent game versions. of course.
    

    def __init__(self, indirectStart = True):
        ShowBase.__init__(self)
        from code.main_menu import menu_ui
        load_prc_file("gameConfig.prc")
        self.optionPage = load_prc_file("options.prc")#Need a handle on this ConfigPage for saving modifications to it
        base.disableMouse()
        
        base.camLens.set_fov(69.3201, 65)
        base.camLens.set_near(0.5)
        
        #load_prc_file("gameConfig.prc")

        globalClock.set_average_frame_rate_interval(0.5)

        #messenger.toggleVerbose()
        self.setFrameRateMeter(True)
        self.menu = menu_ui(indirectStart)


if __name__ == "__main__":
    myGame = game()
    myGame.run()
