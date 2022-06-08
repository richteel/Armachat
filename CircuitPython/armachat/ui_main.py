from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from armachat.ui_editor import ui_editor as ui_editor
from armachat import config
import random

class ui_main(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)
        
        self.exit_keys = ['m', 'i', 'p', 's']
        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
                Line(">(%myAddress%)%myName%", SimpleTextDisplay.GREEN),
                Line("[N] New message", SimpleTextDisplay.WHITE),
                Line("[D] To:(%toAddress%)%toName%", SimpleTextDisplay.WHITE),
                Line("[M] Messages > ALL:%countMessagesAll%", SimpleTextDisplay.WHITE),
                Line("New:%countMessagesNew% Undelivered:%countMessagesUndel%", SimpleTextDisplay.WHITE),
                Line("[ ]          [I] HW Info", SimpleTextDisplay.WHITE),
                Line("[ ]          [P] Ping", SimpleTextDisplay.WHITE),
                Line("[T] Terminal [S] Setup", SimpleTextDisplay.WHITE),
                Line("Ready ...", SimpleTextDisplay.RED)
            ]
        else:
            self.lines = [
                Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
                Line(">(%myAddress%)%myName%", SimpleTextDisplay.GREEN),
                Line("[N] New message", SimpleTextDisplay.WHITE),
                Line("[D] To:%toName%", SimpleTextDisplay.WHITE),
                Line("[M] Messages>A:%countMessagesAll%", SimpleTextDisplay.WHITE),
                Line("New:%countMessagesNew% Undeliv:%countMessagesUndel%", SimpleTextDisplay.WHITE),
                Line("[ ]       [I] HW Inf", SimpleTextDisplay.WHITE),
                Line("[ ]       [P] Ping", SimpleTextDisplay.WHITE),
                Line("[T] Term  [S] Setup", SimpleTextDisplay.WHITE),
                Line("Ready ...", SimpleTextDisplay.RED)
            ]

    def getFlags(self, f3=0, f2=0, status=0, hopLimit=config.hopLimit):
        assert isinstance(f3, int), "ERROR: getFlags - f3 is not an int"
        assert isinstance(f2, int), "ERROR: getFlags - f2 is not an int"
        assert isinstance(status, int), "ERROR: getFlags - status is not an int"
        assert isinstance(hopLimit, int), "ERROR: getFlags - hopLimit is not an int"

        assert (
            f3 >= 0 and f3 < 256
        ), "ERROR: getFlags - f3 is not between 0 and 255"
        assert (
            f2 >= 0 and f2 < 256
        ), "ERROR: getFlags - f2 is not between 0 and 255"
        assert (
            status >= 0 and status < 256
        ), "ERROR: getFlags - status is not between 0 and 255"
        assert (
            hopLimit >= 0 and hopLimit < 256
        ), "ERROR: getFlags - hopLimit is not between 0 and 255"

        return [
            f3,
            f2,
            status,
            hopLimit
        ]
    
    def getMessageId(self):
        if self.vars.messageCount > 255:
            self.vars.messageCount = 0
        
        self.vars.messageCount += 1

        return str(random.randint(0, 255)) + "-" + str(random.randint(0, 255)) + \
                    "-" + str(random.randint(0, 255)) + "-" + str(self.vars.messageCount - 1)

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
                    if keypress["key"] == "d":
                        preval = self.vars.to_dest_idx
                        if keypress["longPress"]:
                            self.vars.to_dest_idx = self.changeValInt(self.vars.to_dest_idx, 0, len(self.vars.address_book) - 1, -1)
                        else:
                            self.vars.to_dest_idx = self.changeValInt(self.vars.to_dest_idx, 0, len(self.vars.address_book) - 1)
                        if preval != self.vars.to_dest_idx:
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                    elif keypress["key"] == "n":
                        self.vars.sound.ring()
                        gui_editor = ui_editor(self.vars)
                        gui_editor.editor["action"] = "Send"
                        gui_editor.editor["maxLines"] = 0
                        gui_editor.editor["maxLen"] = 256
                        gui_editor.editor["text"] = ""
                        
                        result = gui_editor.show()
                        if result is not None and len(result) > 0:
                            print("New Message -> ", result)
                            toAddress = self.vars.address_book[self.vars.to_dest_idx]["address"]
                            data = self.vars.radio.encryptMessage(result)
                            message = {
                                        "to": toAddress,
                                        "from": config.myAddress,
                                        "id": self.getMessageId(),
                                        "status": "S",
                                        "rssi": None,
                                        "snr": None,
                                        "timestamp": self.getTimeStamp(),
                                        "data": data,
                                        "flag0" : 0,
                                        "flag1" : 0,
                                        "flag2" : 0,
                                        "hops": config.hopLimit,
                                        "messageText": result,
                                      }
                            self.vars.messages.append(message)
                            self.vars.radio.sendMessage(message)
                        elif result is not None and len(result) == 0:
                            self.showConfirmation(message="Blank Message", okOnly = True, message2="Not Sent")

                    # elif keypress["key"] == "r":
                    #    supervisor.reload()
                    elif keypress["key"] == "t":
                        self.vars.sound.ring()
                        self.vars.display.screen.show_terminal()
                        keypress = self.vars.keypad.get_key()
                        while keypress is None:
                            keypress = self.vars.keypad.get_key()
                        
                        self.vars.sound.ring()
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()
                    
                    self.show_screen()
