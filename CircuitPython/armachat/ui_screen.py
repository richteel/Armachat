import gc
import supervisor
import displayio
import terminalio
import time
import re
from adafruit_display_text import label
from collections import namedtuple
from adafruit_simple_text_display import SimpleTextDisplay
from armachat import config
from armachat import hw

Line = namedtuple('Line', ['text', 'color'])

class ui_screen(object):
    def __init__(self, ac_vars):
        self.vars = ac_vars
        self.debug = False
        self.exit_keys = []
        self.lines = []
        self.line_index = 0
        self.editor = { 
            "action": "",
            "cursorPos": 0,
            "cursorPosX": 0,
            "cursorPosY": 0,
            "text": "",
            "maxLines": 0,
            "maxLen": 0,
            "validation": "",
            "validationMsg1": "",
            "validationMsg2": "",
            }
        self.receiveTimeout = 0.1
        self.currentMessageIdx = 0
        self.visibleLines = self.vars.display.height_lines - 3

        self.fs_rw = "RO"
        self.fs_rw_long = "Read Only"
        if config.fileSystemWriteMode():
            self.fs_rw = "RW"
            self.fs_rw_long = "Read Write"
        self._gc()
        self.lastReceive = time.monotonic()

    def _countMessages(self, msgStat=""):
        if msgStat is None:
            return 0
        c = 0
        for i in range(len(self.vars.messages)):
            if len(msgStat) == 0 or self.vars.messages[i]["status"] == msgStat:
                c = c + 1
        return c

    def _findall(self, pattern, string):
        while True:
            match = re.search(pattern, string)
            if not match:
                break
            yield match.group(0)
            string = string[match.end():]

    def _gc(self):
        if self.debug:
            print("Free RAM: {:,}".format(gc.mem_free()))
        gc.collect()
        if self.debug:
            print("gc.collect()")
            print("Free RAM: {:,}".format(gc.mem_free()))
    
    def _inc_lines(self, step):
        if self.vars.display.height_lines >= len(self.lines):
            return False
        
        t = self.line_index + step

        if t < 0:
            self.vars.sound.ring()
            t = 0

        if t < len(self.lines):
            self.line_index = t
        else:
            self.vars.sound.ring()

        return True

    def _replace_var(self, text, screen_vars):
        txt = text
        
        for match in self._findall('\%(.+?)\%', txt):
            try:
                txt = txt.replace(match, str(screen_vars[match[1:-1]]))
            except KeyError:
                key = match[1:-1]
                print(f"Missing key '{key}' in screen_vars")

        return txt
    
    def _screen_vars(self):
        return {
            "action": self.editor["action"],
            "bright": config.bright,
            "channel": str(config.getChannel()),
            "col": self.editor["cursorPosX"],
            "countMessagesAll": str(len(self.vars.messages)),
            "countMessagesNew": str(self._countMessages("N")),
            "countMessagesUndel": str(self._countMessages("S")),
            "cpuTemp": "{:.2f}".format(hw.get_CpuTempC()),
            "diskSize": "{:,.1f}".format(hw.get_DiskSpaceKb()),
            "font": config.font,
            "freeSpace": "{:,.1f}".format(hw.get_FreeSpaceKb()),
            "freeRam": "{:,}".format(gc.mem_free()),
            "freq": "{:5.2f}".format(config.freq),
            "keyLayout": self.vars.keypad.keyLayout,
            "len": len(self.editor["text"]),
            "locked": "L" if self.vars.keypad.keyLayoutLocked else "U",
            "line": self.editor["cursorPosY"],
            "melodyIdx": str(config.melody),
            "melodyName": self.vars.sound.get_melodyName(config.melody),
            "melodyLenSecs": self.vars.sound.get_melodyLength(config.melody),
            "msgFrom": self.vars.messages[self.currentMessageIdx]["from"] if len(self.vars.messages) > 0 else "",
            "msgHop": self.vars.messages[self.currentMessageIdx]["hops"] if len(self.vars.messages) > 0 else "",
            "msgId": self.vars.messages[self.currentMessageIdx]["id"] if len(self.vars.messages) > 0 else "",
            "msgIdx": str(self.currentMessageIdx + 1) if len(self.vars.messages) > 0 else "0",
            "msgRssi": self.vars.messages[self.currentMessageIdx]["rssi"] if len(self.vars.messages) > 0 else "",
            "msgSnr": self.vars.messages[self.currentMessageIdx]["snr"] if len(self.vars.messages) > 0 else "",
            "msgStatus": self.vars.messages[self.currentMessageIdx]["status"] if len(self.vars.messages) > 0 else "",
            "msgTime": self.vars.messages[self.currentMessageIdx]["timestamp"] if len(self.vars.messages) > 0 else "",
            "msgTo": self.vars.messages[self.currentMessageIdx]["to"] if len(self.vars.messages) > 0 else "",
            "myAddress": str(config.myAddress),
            "myName": config.myName,
            "pos": self.editor["cursorPos"],
            "power": str(config.power),
            "profile": str(config.loraProfile),
            "profileName": config.loraProfiles[config.loraProfile - 1]["modemPresetConfig"],
            "profileDesc": config.loraProfiles[config.loraProfile - 1]["modemPresetDescription"],
            "region": config.region,
            "RW": self.fs_rw,
            "RWlong": self.fs_rw_long,
            "sleep": self.vars.display.get_sleepTime(),
            "theme": config.theme,
            "toAddress": self.vars.address_book[self.vars.to_dest_idx]["address"],
            "toName": self.vars.address_book[self.vars.to_dest_idx]["name"],
            "tone": str(config.tone),
            "usbConnected": "USB power connected" if hw.VBUS_status.value else "No USB power",
            "volume": str(config.volume),
            "vsys": "{:5.2f} V".format(hw.get_VSYSvoltage()),
        }
    
    def _show_screen(self):
        screen_vars = self._screen_vars()
        
        if self.line_index >= len(self.lines):
            self.line_index = 0
        
        screenColors = ()

        for i in range(0, self.vars.display.height_lines):
            line = self.line_index + i

            if i > self.vars.display.height_lines - 1 or line > len(self.lines) - 1:
                screenColors += (SimpleTextDisplay.WHITE,)
            else:
                screenColors += (self.lines[line].color,)
        
        self.vars.display.screen = SimpleTextDisplay(
            display=self.vars.display.display,
            font=self.vars.display.font,
            text_scale=1,
            colors=screenColors
        )

        for i in range(0, self.vars.display.height_lines):
            line = self.line_index + i

            if i > self.vars.display.height_lines - 1 or line > len(self.lines) - 1:
                self.vars.display.screen[i].text = ""
            else:
                self.vars.display.screen[i].text = \
                    self._replace_var(self.lines[line].text, screen_vars)
            gc.collect()
            
        self.vars.display.screen.show()
        self._gc()

    def appendMessage(self, message):
        timeStamp = str(time.monotonic())

        self.vars.messages.append(
            message["to"]
            + "|"
            + message["from"]
            + "|"
            + message["id"]
            + "|"
            + str(message["hops"]) if message["hops"] is not None else "n/a"
            + "|"
            + message["status"]
            + "|"
            + str(message["rssi"]) if message["rssi"] is not None else "n/a"
            + "|"
            + str(message["snr"]) if message["snr"] is not None else "n/a"
            + "|"
            + timeStamp
            + "|"
            + str(message["data"]),
            "utf-8",
        )

    def changeValInt(self, currentval, min, max, step=1, loopval=False):
        newval = currentval
        newval += step
        
        if not loopval and (newval < min or newval > max):
            newval = currentval
        elif loopval and newval < min:
            newval = max
        elif loopval and newval > max:
            newval = min
        
        return newval

    def checkKeys(self, keypress):
        handled = False
        
        if self.debug:
            print("keypress -> ", keypress)

        # Navigation for small screens
        if keypress["key"] == "o":
            if self._inc_lines(-1 * self.vars.display.height_lines):
                self.show_screen()
                self.vars.sound.ring()
            else:
                self.vars.sound.beep()
        elif keypress["key"] == "l":
            if self._inc_lines(self.vars.display.height_lines):
                self.show_screen()
                self.vars.sound.ring()
            else:
                self.vars.sound.beep()
        # Special keys for all screens except editor
        # Volume
        elif keypress["key"] == "v":
            preval = config.volume
            if keypress["longPress"]:
                config.volume = self.changeValInt(config.volume, 0, 6, -1)
            else:
                config.volume = self.changeValInt(config.volume, 0, 6)
            config.writeConfig()
            
            if preval != config.volume:
                self.vars.sound.ring()
            else:
                self.vars.sound.beep()
        # Brightness (Screen)
        elif keypress["key"] == "b":
            preval = config.bright
            if keypress["longPress"]:
                self.vars.display.incBacklight(-1)
            else:
                self.vars.display.incBacklight(1)
            config.writeConfig()

            if preval != config.bright:
                self.vars.sound.ring()
            else:
                self.vars.sound.beep()
        # Toggle Keyboard Backlight
        elif keypress["key"] == "q":
            if self.vars.keypad.toggleBacklight():
                self.vars.sound.ring()
            else:
                self.vars.sound.beep()
        # Toggle Display Backlight
        elif keypress["key"] == "a":
            self.vars.sound.ring()
            self.vars.display.toggleBacklight()

        return handled

    def getTimeStamp(self):
        return time.monotonic()

    def isUsbConnected(self):
        return supervisor.runtime.usb_connected

    def receive(self):
        '''
        if time.monotonic() - self.lastReceive < 1.0:
            return
        
        self.lastReceive = time.monotonic()
        '''

        message = self.vars.radio.receive(timeout=self.receiveTimeout)

        if message is None:
            return

        if message["flag2"] == 33:
            self._gc()
            for i in range(len(self.vars.messages)):
                if self.vars.messages[i]["id"] == message["id"] and self.vars.messages[i]["status"] == "S":
                    self.vars.messages[i]["status"] = "D"
                    break

            self.show_screen()
            self._gc()
        else:
            self._gc()
            self.vars.messages.append(message)
            self.show_screen()
            self.sendConfirmation(message)
            self.vars.sound.play_melody(config.melody)
            self._gc()
    
    def sendConfirmation(self, message):
        msgto = message["to"]
        confirmationMessage = message.copy()
        confirmationMessage["flag2"] = 33
        confirmationMessage["to"] = message["from"]
        message["from"] = msgto
        confirmationMessage["data"] = self.vars.radio.encryptMessage("Confirmation")
        self.vars.radio.sendMessage(confirmationMessage)

    def show(self):
        raise NotImplementedError

    def showConfirmation(self, message="", okOnly = False, message2=""):
        self._gc()
        font_width, font_height = terminalio.FONT.get_bounding_box()
        font_scale = 2
        if self.visibleLines < 5:
            font_scale = 1
        char_width = self.vars.display.display.width/(font_width * font_scale) - 2
        startX = (font_width * font_scale)
        startY = int((self.vars.display.display.height - (font_height * 3))/2)

        text1 = message if len(message)>0 else self.editor["action"]
        text2 = "[ENT] Yes [DEL] No"
        text3 = "[ALT] Cancel"
        if okOnly:
            text2 = message2
            text3 = "[ENT] OK"

        text1 = self.textCenter(text1, char_width)
        text2 = self.textCenter(text2, char_width)
        text3 = self.textCenter(text3, char_width)

        # Make the display context
        splash = displayio.Group(x=startX, y=startY)

        text_area1 = label.Label(
            terminalio.FONT, text=text1, scale=font_scale, background_tight=False, background_color=0x000066, color=0xFFFFFF
        )
        
        text_area2 = label.Label(
            terminalio.FONT, text=text2, scale=font_scale, background_tight=False, background_color=0x0000FF, color=0xFFFFFF
        )
        text_area2.y = (font_height * font_scale)

        text_area3 = label.Label(
            terminalio.FONT, text=text3, scale=font_scale, background_tight=False, background_color=0x0000FF, color=0xFFFFFF
        )
        text_area3.y = font_height * font_scale * 2

        splash.append(text_area1)
        splash.append(text_area2)
        splash.append(text_area3)

        self.vars.keypad.keyLayout = self.vars.keypad.keyboards[0]["layout"]

        # self.vars.display.display.show(splash)
        self.vars.display.screen.text_group.append(splash)
        self.vars.display.screen.show()

        while True:
            self.receive()
            keypress = self.vars.keypad.get_key()

            if self.vars.display.sleepUpdate(keypress):
                continue

            if keypress is not None:
                self._gc()
                # ent, bsp, or alt
                if not self.checkKeys(keypress):
                    if keypress["key"] == "ent" or keypress["key"] == "rt" or keypress["key"] == "dn":
                        self.vars.sound.ring()
                        return "Y"
                    elif keypress["key"] == "bsp" or keypress["key"] == "lt" or keypress["key"] == "up":
                        self.vars.sound.ring()
                        return "N"
                    elif keypress["key"] == "alt":
                        self.vars.sound.ring()
                        self.vars.keypad.keyLayout = self.vars.keypad.keyboards[self.vars.keypad.keyboard_current_idx]["layout"]
                        return None
                    else:
                        self.vars.sound.beep()

        # self.vars.keypad.keyLayout = self.vars.keypad.keyboards[self.vars.keypad.keyboard_current_idx]["layout"]
    
    def show_screen(self):
        self._gc()
        self._show_screen()
        self._gc()    
    
    def textCenter(self, text, char_width):
        retText = (" " * int((char_width - len(text))/2)) + text
        retText += " " * int(char_width - len(retText))
        return retText