from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectButton, DirectOptionMenu, DirectFrame, DirectLabel, DirectEntry, DirectScrolledFrame, DGG
from direct.task import Task


class optionsMenu (DirectObject):
    def __init__(self, pmen):
        from .option_lists import keybinds, textOps#If user never opens this module, we don't need to import these.
        self.keybinds = keybinds
        self.textOps = textOps

        self.pmen = pmen#store pointer to main menu instance
        self.keybindButton = DirectButton(text="keybindings", scale = 0.1, command= self.build_binds, pos = (-1, 0.5, 0.9))
        self.otherButton = DirectButton(text="others", scale = 0.1, command= self.build_others, pos = (-0.5, 0.5, 0.9))
        self.scroll = DirectScrolledFrame(canvasSize=(-1.4, 1.4, -2, 2), frameSize = (-1.5, 1.4, -0.8, 0.8), frameColor = (0.5, 0.3, 0.3, 1))
        
        self.close = DirectButton(text="Close", scale = 0.1, command= self.delete, pos = (-1, 0, -0.93))
        self.saveButton = DirectButton(text="Save", scale = 0.1, command= self.save, pos = (-0.6, 0, -0.93))
        
        self.activeLabels = []
        self.activeEnts = []
        self.build_binds()
        
    def save (self):#This broken when running through VS
        writer = open("options.prc", "w")
        for i in self.textOps:
            writer.write(i.get_name() + ' ' + i.get_string_value() +'\n')
        for i in self.keybinds:
            writer.write(i.get_name() + ' ' + i.get_string_value()+ '\n')
        writer.flush()
        writer.close()
        
    def delete(self):
        self.clear_ops()
        self.keybindButton.destroy()
        self.otherButton.destroy()
        self.scroll.destroy()
        self.close.destroy()
        self.saveButton.destroy()
        
        self.pmen.build_menu()
        self.ignore_all()
        
    def build_binds (self):
        self.clear_ops()
        posid = 0
        canvas = self.scroll.getCanvas()
        for op in self.keybinds:
            k = DirectLabel(text = op.get_name(), parent = canvas, text_scale = 0.1, pos = (0, 0, 1.8-(posid*0.12)), frameSize = (-1.4, 0, -0.05, 0.05), text_pos = (-0.7,-0.025))
            self.activeLabels.append(k)
            o = DirectButton(text = op.get_string_value(), parent = canvas, text_scale = 0.1, pos = (0, 0, 1.8-(posid*0.12)), frameSize = (0, 1.4, -0.05, 0.05), text_pos = (0.7,-0.025), command = self.recast_bind, extraArgs = (self.keybinds.index(op),))
            self.activeEnts.append(o)
            posid +=1
        
    def build_others (self):
        self.clear_ops()
        posid = 0
        canvas = self.scroll.getCanvas()
        for op in self.textOps:
            k = DirectLabel(text = op.get_name(), parent = canvas, text_scale = 0.1, pos = (0, 0, 1.8-(posid*0.12)), frameSize = (-1.4, 0, -0.05, 0.05), text_pos = (-0.7,-0.025))
            self.activeLabels.append(k)
            k = DirectEntry(initialText = op.get_string_value(), parent = canvas, text_scale = 0.1, pos = (0, 0, 1.8-(posid*0.12)), frameSize = (0, 1.4, -0.05, 0.05), text_pos = (0.7,-0.025), command = self.typed_update, extraArgs = [self.textOps.index(op),])
            self.activeEnts.append(k)
            posid +=1
        
    def clear_ops(self):
        for i in self.activeLabels:
            i.destroy()
        self.activeLabels.clear()
        for i in self.activeEnts:
            i.destroy()
        self.activeEnts.clear()
    
    def typed_update(self, newVal, index):
        self.textOps[index].set_value(newVal)
    
    def recast_bind(self, index):
        for i in self.activeEnts:
            if self.activeEnts.index(i) == index:
                continue
            i["state"] = DGG.DISABLED
            i["relief"] = DGG.FLAT
        self.activeEnts[index]["text"] = "Press new key"
        base.buttonThrowers[0].node().setButtonDownEvent('keystroke')
        self.accept("keystroke", self.get_key)
        self.newKey = None
        taskMgr.add(self.wait_for_press, "waiting for key press", extraArgs = [index])
        

    def wait_for_press (self, index):
        if self.newKey:
            self.keybinds[index].set_value(self.newKey)
            self.activeEnts[index]["text"] = self.newKey
            base.buttonThrowers[0].node().setButtonDownEvent('')
            for i in self.activeEnts:
                i["state"] = DGG.NORMAL
                i["relief"] = DGG.GROOVE
            self.ignoreAll()
            return Task.done
        return Task.cont
        
    def get_key(self, key):
        self.newKey = key