from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from armachat.ui_setup_radio import ui_setup_radio as ui_setup_radio
from adafruit_simple_text_display import SimpleTextDisplay

class ui_setup(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("Setup", SimpleTextDisplay.GREEN),
                Line("", SimpleTextDisplay.WHITE),
                Line("Pg [ENT]next [DEL]previous", SimpleTextDisplay.WHITE),
                Line("[ALT] to exit", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
            ]
        else:
            self.lines = [
                Line("Setup", SimpleTextDisplay.GREEN),
                Line("Scroll [L]dwn  [O]up", SimpleTextDisplay.WHITE),
                Line("Pg [ENT]nxt [DEL]pre", SimpleTextDisplay.WHITE),
                Line("[ALT] to exit", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
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
                        gui_setup_next = ui_setup_radio(self.vars)
                        if gui_setup_next.show() == None:
                            return None
                        self.line_index = 0
                        self.show_screen()
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()
