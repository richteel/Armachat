from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from armachat import config

class ui_setup_sound(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
                Line("3 Sound:", SimpleTextDisplay.GREEN),
                Line("[V] Volume: %volume%", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("[T] Tone: %tone%", SimpleTextDisplay.WHITE),
                Line("[M] Melody: %melodyIdx%", SimpleTextDisplay.WHITE),
                Line("    %melodyName%", SimpleTextDisplay.WHITE),
                Line("    %melodyLenSecs% secs", SimpleTextDisplay.WHITE),
                Line("[P] Play Melody", SimpleTextDisplay.WHITE),
                Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
            ]
        else:
            self.lines = [
                Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
                Line("3 Sound:", SimpleTextDisplay.GREEN),
                Line("[V] Volume: %volume%", SimpleTextDisplay.WHITE),
                Line("", SimpleTextDisplay.WHITE),
                Line("[T] Tone: %tone%", SimpleTextDisplay.WHITE),
                Line("[M] Melody: %melodyIdx%", SimpleTextDisplay.WHITE),
                Line("    %melodyName%", SimpleTextDisplay.WHITE),
                Line("    %melodyLenSecs% secs", SimpleTextDisplay.WHITE),
                Line("[P] Play Melody", SimpleTextDisplay.WHITE),
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
                    if keypress["key"] == "v":
                        self.show_screen()
                    elif keypress["key"] == "alt":
                        self.vars.sound.ring()
                        return None
                    elif keypress["key"] == "bsp":
                        self.vars.sound.ring()
                        return keypress
                    elif keypress["key"] == "t":
                        if keypress["longPress"]:
                            config.tone = self.changeValInt(config.tone, 1000, 10000, -1000)
                        else:
                            config.tone = self.changeValInt(config.tone, 1000, 10000, 1000)
                        config.writeConfig()
                        self.show_screen()
                        self.vars.sound.ring()
                    elif keypress["key"] == "m":
                        self.vars.sound.ring()
                        if keypress["longPress"]:
                            config.melody = self.changeValInt(config.melody, 0, len(self.vars.sound.melody.melodies) - 1, -1)
                        else:
                            config.melody = self.changeValInt(config.melody, 0, len(self.vars.sound.melody.melodies) - 1)
                        config.writeConfig()
                        self.show_screen()
                    elif keypress["key"] == "p":
                        self.vars.sound.ring()
                        self.show_screen()
                        self.vars.sound.play_melody(config.melody)
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()
