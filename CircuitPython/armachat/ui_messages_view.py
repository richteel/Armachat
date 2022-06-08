from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from armachat.ui_setup_id import ui_setup_id as ui_setup_id
from armachat import config

class ui_messages_view(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        self.lines = []
        self.visibleLines = self.vars.display.height_lines - 3

        self.actionLine26 = Line("ALT-Ex Ent> Del< SPC-Detail", SimpleTextDisplay.RED)
        self.actionLine20 = Line("Ent> Del< SPC-Detail", SimpleTextDisplay.GREEN)

        self.scrollTopLine = 0
        self.currentDisplayDetails = False
        self.displayMessage()

    def displayMessage(self):
        self.currentDisplayDetails = False
        if self.vars.display.width_chars >= 26:
            self.lines = [
            Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
            Line("Message: %msgIdx% of %countMessagesAll%", SimpleTextDisplay.GREEN),
            ]
        else:
            self.lines = [
                Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
                Line("Message: %msgIdx% of %countMessagesAll%", SimpleTextDisplay.GREEN),
            ]
        
        for i in range(0, self.visibleLines):
            self.lines.append(Line("", SimpleTextDisplay.WHITE))

        self.lines.append(self.actionLine26 if self.vars.display.width_chars >= 26 else self.actionLine20)
        # TODO: Display message

        self.updateMessageDisplay()
        self.show_screen()

    def displayDetails(self):
        self.currentDisplayDetails = True
        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
                Line("Message: %msgIdx% of %countMessagesAll%", SimpleTextDisplay.GREEN),
                Line("Status: %msgStatus%", SimpleTextDisplay.WHITE),
                Line("To: %msgTo%", SimpleTextDisplay.WHITE),
                Line("From: %msgFrom%", SimpleTextDisplay.WHITE),
                Line("MsgId: %msgId%", SimpleTextDisplay.WHITE),
                Line("Hop: %msgHop%", SimpleTextDisplay.WHITE),
                Line("RSSI: %msgRssi%   SNR: %msgSnr%", SimpleTextDisplay.WHITE),
                Line("Time: %msgTime%", SimpleTextDisplay.WHITE),
                Line("ALT-Ex Ent> Del< SPC-Detail", SimpleTextDisplay.RED)
            ]
        else:
            self.lines = [
                Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
                Line("Message: %msgIdx% of %countMessagesAll%", SimpleTextDisplay.GREEN),
                Line("Status: %msgStatus%", SimpleTextDisplay.WHITE),
                Line("To: %msgTo%", SimpleTextDisplay.WHITE),
                Line("From: %msgFrom%", SimpleTextDisplay.WHITE),
                Line("MsgId: %msgId%", SimpleTextDisplay.WHITE),
                Line("Hop: %msgHop%", SimpleTextDisplay.WHITE),
                Line("RSSI: %msgRssi%   SNR: %msgSnr%", SimpleTextDisplay.WHITE),
                Line("Time: %msgTime%", SimpleTextDisplay.WHITE),
                Line("Ent> Del< SPC-Detail", SimpleTextDisplay.RED)
            ]

        self.lines.append(self.actionLine26 if self.vars.display.width_chars >= 26 else self.actionLine20)
        self.show_screen()
        
        
    def show(self):
        self.line_index = 0
        self.updateMessageDisplay()
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
                        if self.currentMessageIdx + 1 < len(self.vars.messages):
                            self.currentMessageIdx += 1
                            self.vars.sound.ring()
                            self.line_index = 0
                            self.scrollTopLine = 0
                            self.displayMessage()
                        else:
                            self.vars.sound.beep()
                    elif keypress["key"] == "bsp":
                        if self.currentMessageIdx - 1 >= 0:
                            self.currentMessageIdx -= 1
                            self.vars.sound.ring()
                            self.line_index = 0
                            self.scrollTopLine = 0
                            self.displayMessage()
                        else:
                            self.vars.sound.beep()
                    elif keypress["key"] == " ":
                        if len(self.vars.messages) > 0:
                            self.vars.sound.ring()
                            self.scrollTopLine = 0
                            if self.currentDisplayDetails:
                                self.displayMessage()
                            else:
                                self.displayDetails()
                        else:
                            self.vars.sound.beep()
                    elif keypress["key"] == "O":
                        self.scrollTopLine -= 1
                        if self.updateMessageDisplay():
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                    elif keypress["key"] == "L":
                        self.scrollTopLine += 1
                        if self.updateMessageDisplay():
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()

    def updateMessageDisplay(self):
        # CHECK: If no messages return
        if len(self.vars.messages) == 0:
            return False
        # CHECK: If top line is less than zero, set to zero and exit
        if self.scrollTopLine < 0:
            self.scrollTopLine = 0
            return False
        
        # Split message into lines
        displayLines = self.vars.messages[self.currentMessageIdx]["messageText"].splitlines()
        # CHECK: If done no further scrolling, exit
        if self.scrollTopLine > 0 and self.scrollTopLine > len(displayLines) - self.visibleLines:
            self.scrollTopLine = len(displayLines) - self.visibleLines
            if self.scrollTopLine < 0:
                self.scrollTopLine = 0
            return False

        # Display the message
        for i in range(self.visibleLines):
            lineIndex = self.scrollTopLine + i
            if lineIndex >= len(displayLines):
                self.lines[2 + i] = Line("", SimpleTextDisplay.WHITE)
            else:
                self.lines[2 + i] = Line(displayLines[lineIndex], SimpleTextDisplay.WHITE)
        
        return True
        