from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay

class ui_hw_info(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
                Line("System info:", SimpleTextDisplay.GREEN),
                Line("VSYS power: %vsys% V", SimpleTextDisplay.WHITE),
                Line("%usbConnected%", SimpleTextDisplay.WHITE),
                Line("Disk size: %diskSize% KB", SimpleTextDisplay.WHITE),
                Line("Free space: %freeSpace% KB", SimpleTextDisplay.WHITE),
                Line("CPU Temp: %cpuTemp% degrees C", SimpleTextDisplay.WHITE),
                Line("Free RAM: %freeRam%", SimpleTextDisplay.WHITE),
                Line("FS Mode: %RWlong%", SimpleTextDisplay.WHITE),
                Line("[ALT] Exit", SimpleTextDisplay.RED)
            ]
        else:
            self.lines = [
                Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
                Line("System info:", SimpleTextDisplay.GREEN),
                Line("VSYS power: %vsys% V", SimpleTextDisplay.WHITE),
                Line("%usbConnected%", SimpleTextDisplay.WHITE),
                Line("Disk size: %diskSize% KB", SimpleTextDisplay.WHITE),
                Line("Free space: %freeSpace% KB", SimpleTextDisplay.WHITE),
                Line("CPU Temp: %cpuTemp% C", SimpleTextDisplay.WHITE),
                Line("Free RAM: %freeRam%", SimpleTextDisplay.WHITE),
                Line("FS Mode: %RWlong%", SimpleTextDisplay.WHITE),
                Line("[ALT] Exit", SimpleTextDisplay.RED)
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
                    else:
                        self.vars.sound.beep()
