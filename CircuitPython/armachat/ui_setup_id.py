from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from armachat.ui_setup_display import ui_setup_display as ui_setup_display
from armachat.ui_editor import ui_editor as ui_editor
from armachat import config

class ui_setup_id(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
                Line("1 Identity:", SimpleTextDisplay.GREEN),
                Line("[N] Name: %myName%", SimpleTextDisplay.WHITE),
                Line("------", SimpleTextDisplay.WHITE),
                Line("[E] Encryption {}", SimpleTextDisplay.WHITE),
                Line("[G] Group 3:3", SimpleTextDisplay.WHITE),
                Line("[G] Group 2:2", SimpleTextDisplay.WHITE),
                Line("[G] Group 1:1", SimpleTextDisplay.WHITE),
                Line("[I] ID:     1", SimpleTextDisplay.WHITE),
                Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
            ]
        else:
            self.lines = [
                Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
                Line("1 Identity:", SimpleTextDisplay.GREEN),
                Line("[N] Name: %myName%", SimpleTextDisplay.WHITE),
                Line("------", SimpleTextDisplay.WHITE),
                Line("[E] Encryption {}", SimpleTextDisplay.WHITE),
                Line("[G] Group 3:3", SimpleTextDisplay.WHITE),
                Line("[G] Group 2:2", SimpleTextDisplay.WHITE),
                Line("[G] Group 1:1", SimpleTextDisplay.WHITE),
                Line("[I] ID:     1", SimpleTextDisplay.WHITE),
                Line("ALT-Ex [ENT]> [DEL]<", SimpleTextDisplay.RED)
            ]
        
    def show(self):
        self.line_index = 0
        self.show_screen()
        self.vars.display.sleepUpdate(None, True)

        while True:
            self.receive()
            keypress = self.vars.keypad.get_key()
            if self.vars.display.sleepUpdate(keypress):
                continue

            if keypress is not None:
                self._gc()
                # O, L, Q, A, B, V
                if not self.checkKeys(keypress):
                    if keypress["key"] == "alt":
                        self.vars.sound.ring()
                        return None
                    elif keypress["key"] == "ent":
                        self.vars.sound.ring()
                        gui_setup_next = ui_setup_display(self.vars)
                        if gui_setup_next.show() == None:
                            return None
                        self.line_index = 0
                    elif keypress["key"] == "bsp":
                        self.vars.sound.ring()
                        return keypress
                    elif keypress["key"] == "n":
                        self.vars.sound.ring()
                        gui_editor = ui_editor(self.vars)
                        gui_editor.editor["action"] = "Save"
                        gui_editor.editor["maxLines"] = 1
                        gui_editor.editor["maxLen"] = 16
                        gui_editor.editor["text"] = config.myName
                        # gui_editor.editor["validation"] = "^[A-Za-z]*$"
                        # gui_editor.editor["validationMsg1"] = "Validation Error"
                        # gui_editor.editor["validationMsg2"] = "Must be characters"
                        
                        result = gui_editor.show()
                        if result is not None:
                            config.myName = result
                    elif keypress["key"] == "e":
                        self.vars.sound.ring()
                        # TODO
                    elif keypress["key"] == "g":
                        self.vars.sound.ring()
                        # TODO
                    elif keypress["key"] == "i":
                        self.vars.sound.ring()
                        # TODO
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()
                    
                    self.show_screen()
