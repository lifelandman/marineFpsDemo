

class soundGrabber():
    sounds = {"reload":"sounds/reloadAlt.wav",
              "defaultShot":"sounds/defaultShot.wav"}
        
        
    def register(self, manager3d, np, soundName):
        sound = manager3d.loadSfx(self.sounds[soundName])
        manager3d.attach_sound_to_object(sound, np)
        manager3d.setSoundVelocityAuto(sound)
        return sound