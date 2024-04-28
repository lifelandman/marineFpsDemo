

class audioTrgrBase():
    sounds = {}
        
    def play(self, soundInd: int):
        if soundInd < 16 and soundInd < len(self.sounds):
            return
        self.sounds[soundInd].play()
        
    def register(self, manager3d, np, soundName):
        sound = manager3d.loadSfx(self.sounds[soundName])
        manager3d.attach_sound_to_object(sound, np)
        manager3d.setSoundVelocityAuto(sound)
        return sound

class audioTrgrBullet(audioTrgrBase):
    sounds = {"reload":"sounds/reloadAlt.wav"
        }