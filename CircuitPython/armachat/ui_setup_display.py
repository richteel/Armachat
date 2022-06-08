from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from armachat.ui_setup_sound import ui_setup_sound as ui_setup_sound
from armachat import config

class ui_setup_display(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
                Line("2 Display:", SimpleTextDisplay.GREEN),
                Line("[B] Bright: %bright%", SimpleTextDisplay.WHITE),
                Line("[S] Sleep:  %sleep% secs", SimpleTextDisplay.WHITE),
                Line("[F] Font:   %font%", SimpleTextDisplay.WHITE),
                Line("[T] Theme:  %theme%", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
            ]
        else:
            self.lines = [
                Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
                Line("2 Display:", SimpleTextDisplay.GREEN),
                Line("[B] Bright: %bright%", SimpleTextDisplay.WHITE),
                Line("[S] Sleep:  %sleep% secs", SimpleTextDisplay.WHITE),
                Line("[F] Font:   %font%", SimpleTextDisplay.WHITE),
                Line("[T] Theme:  %theme%", SimpleTextDisplay.WHITE),
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
                    if keypress["key"] == "b":
                        self.show_screen()
                    elif keypress["key"] == "alt":
                        self.vars.sound.ring()
                        return None
                    elif keypress["key"] == "ent":
                        self.vars.sound.ring()
                        gui_setup_next = ui_setup_sound(self.vars)
                        if gui_setup_next.show() == None:
                            return None
                        self.line_index = 0
                        self.show_screen()
                    elif keypress["key"] == "bsp":
                        self.vars.sound.ring()
                        return keypress
                    elif keypress["key"] == "s":
                        preval = config.sleep
                        if keypress["longPress"]:
                            self.vars.display.incSleep(-1)
                        else:
                            self.vars.display.incSleep(1)
                        if preval != config.sleep:
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                        self.show_screen()
                    elif keypress["key"] == "f":
                        self.vars.sound.ring()
                        # TODO
                        self.show_screen()
                    elif keypress["key"] == "t":
                        self.vars.sound.ring()
                        # TODO
                        self.show_screen()
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()
