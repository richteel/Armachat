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
        self.isEditor = False
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
        self.visibleLines = self.vars.display.height_lines - 2

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
        padSpace = False
        _findall = self._findall
        width_chars = self.vars.display.width_chars
        r = _findall('\%(.+?)\%', txt)
        
        for match in r:
            if match[1:-1] == "space":
                padSpace = True
                next
            
            try:
                txt = txt.replace(match, str(screen_vars[match[1:-1]]))
            except KeyError:
                key = match[1:-1]
                if key != 'space':
                    print(f"Missing key '{key}' in screen_vars")

        if padSpace:
            spaces = width_chars - (len(txt) - len("%space%"))
            if spaces < 0:
                spaces = 0
            txt = txt.replace("%space%", " " * spaces)

        return txt
    
    def _screen_vars(self):
        editor = self.editor
        vars = self.vars
        _countMessages = self._countMessages
        currentMessageIdx = self.currentMessageIdx

        return {
            "action": editor["action"],
            "bright": config.bright,
            "channel": str(config.getChannel()),
            "col": editor["cursorPosX"],
            "countMessagesAll": str(len(vars.messages)),
            "countMessagesNew": str(_countMessages("N")),
            "countMessagesUndel": str(_countMessages("S")),
            "cpuTemp": "{:.2f}".format(hw.get_CpuTempC()),
            "diskSize": "{:,.1f}".format(hw.get_DiskSpaceKb()),
            "font": config.font,
            "freeSpace": "{:,.1f}".format(hw.get_FreeSpaceKb()),
            "freeRam": "{:,}".format(gc.mem_free()),
            "freq": "{:5.2f}".format(config.freq),
            "keyLayout": vars.keypad.keyLayout,
            "len": len(editor["text"]),
            "locked": "L" if vars.keypad.keyLayoutLocked else "U",
            "line": editor["cursorPosY"],
            "melodyIdx": str(config.melody),
            "melodyName": vars.sound.get_melodyName(config.melody),
            "melodyLenSecs": vars.sound.get_melodyLength(config.melody),
            "msgFrom": vars.messages[currentMessageIdx]["from"] if len(vars.messages) > 0 else "",
            "msgHop": vars.messages[currentMessageIdx]["hops"] if len(vars.messages) > 0 else "",
            "msgId": vars.messages[currentMessageIdx]["id"] if len(vars.messages) > 0 else "",
            "msgIdx": str(currentMessageIdx + 1) if len(vars.messages) > 0 else "0",
            "msgRssi": vars.messages[currentMessageIdx]["rssi"] if len(vars.messages) > 0 else "",
            "msgSnr": vars.messages[currentMessageIdx]["snr"] if len(vars.messages) > 0 else "",
            "msgStatus": vars.messages[currentMessageIdx]["status"] if len(vars.messages) > 0 else "",
            "msgTime": vars.messages[currentMessageIdx]["timestamp"] if len(vars.messages) > 0 else "",
            "msgTo": vars.messages[currentMessageIdx]["to"] if len(vars.messages) > 0 else "",
            "myAddress": str(config.myAddress),
            "myName": config.myName,
            "pos": editor["cursorPos"],
            "power": str(config.power),
            "profile": str(config.loraProfile),
            "profileName": config.loraProfiles[config.loraProfile - 1]["modemPresetConfig"],
            "profileDesc": config.loraProfiles[config.loraProfile - 1]["modemPresetDescription"],
            "region": config.region,
            "RW": self.fs_rw,
            "RWlong": self.fs_rw_long,
            "sleep": vars.display.get_sleepTime(),
            "theme": config.theme,
            "toAddress": vars.address_book[vars.to_dest_idx]["address"],
            "toName": vars.address_book[vars.to_dest_idx]["name"],
            "tone": str(config.tone),
            "usbConnected": "USB power connected" if hw.VBUS_status.value else "No USB power",
            "volume": str(config.volume),
            "vsys": "{:5.2f} V".format(hw.get_VSYSvoltage()),
        }
    
    # Speedup attempt by caching self referenced variables
    # REF: https://urish.medium.com/embedded-python-cranking-performance-knob-up-to-eleven-df31a5940a63
    # Prior to change execution time was 0.34375 to 0.408203
    def _show_screen(self):
        screen_vars = self._screen_vars()
        line_index = self.line_index
        display = self.vars.display
        height_lines = self.vars.display.height_lines
        screen = self.vars.display.screen
        lines = self.lines
        isEditor = self.isEditor
        _replace_var = self._replace_var

        
        if line_index >= len(self.lines):
            line_index = 0

        r = range(0, height_lines)
        # lastProcessTime = time.monotonic()
        for i in r:
            # startLineTime = time.monotonic()
            line = line_index + i

            if i > height_lines - 1 or line > len(lines) - 1:
                screen[i].text = ""
                # break
            elif isEditor and i > 0 and i < height_lines - 2:
                screen[i].text = lines[line].text
            elif "%" in lines[line].text:
                screen[i].text = _replace_var(lines[line].text, screen_vars)
            else:
                screen[i].text = lines[line].text
            
            screen[i].color = lines[line].color

            # print(f"for '{i}' in range(0, '{display.height_lines}'): -> {time.monotonic() - startLineTime}")
        
        # tTime = time.monotonic() - lastProcessTime
        # print("for i in range(0, display.height_lines) 2 -> ", tTime)
        
        screen.show()
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
                        self.vars.display.screen.text_group.remove(splash)
                        return "Y"
                    elif keypress["key"] == "bsp" or keypress["key"] == "lt" or keypress["key"] == "up":
                        self.vars.sound.ring()
                        self.vars.display.screen.text_group.remove(splash)
                        return "N"
                    elif keypress["key"] == "alt":
                        self.vars.sound.ring()
                        self.vars.display.screen.text_group.remove(splash)
                        self.vars.keypad.keyLayout = self.vars.keypad.keyboards[self.vars.keypad.keyboard_current_idx]["layout"]
                        return None
                    else:
                        self.vars.sound.beep()

        # self.vars.keypad.keyLayout = self.vars.keypad.keyboards[self.vars.keypad.keyboard_current_idx]["layout"]
    
    def show_screen(self):
        # self._gc()
        self._show_screen()
        # self._gc()    
    
    def textCenter(self, text, char_width):
        retText = (" " * int((char_width - len(text))/2)) + text
        retText += " " * int(char_width - len(retText))
        return retText