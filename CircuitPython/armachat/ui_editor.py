import re
import time
from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay

class ui_editor(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        self.lines = []

        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("[%keyLayout%] %line%:%col%/%pos%:%len%%space%%RW%", SimpleTextDisplay.YELLOW),
            ]
        else:
            self.lines = [
                Line("[%keyLayout%] %line%:%col%/%pos%:%len%%space%%RW%", SimpleTextDisplay.YELLOW),
            ]

        for i in range(0, self.visibleLines):
            self.lines.append(Line("", SimpleTextDisplay.WHITE))

        self.lines.append(Line("", SimpleTextDisplay.GREEN))
        
        self.actionLine26 = [
            Line("[Ent] %action%    [Del] Delete", SimpleTextDisplay.GREEN),
            Line("[Ent] > Right  [Del] < Left", SimpleTextDisplay.GREEN),
            Line("[Ent] Down    [Del] Up", SimpleTextDisplay.GREEN)
        ]
        self.actionLine20 = [
            Line("[Ent] %action%    [Del] Del", SimpleTextDisplay.GREEN),
            Line("[Ent] >Rt  [Del] <Lt", SimpleTextDisplay.GREEN),
            Line("[Ent] Down  [Del] Up", SimpleTextDisplay.GREEN)
        ]

        self.vars.keypad.alt_is_esc = False
        
        # The following fields are used for validation of the input
        # self.editor["maxLines"]
        # self.editor["maxLen"]
        self.allowNumbers = True
        self.allUpper = True
        self.allowLower = True
        self.allowSpecial = True
        self.validationRegEx = None
        self.isEditor = True

    def addChar(self, txt):
        addTxt = txt
        if txt == "spc":
            addTxt = " "
        elif txt == "tab":
            addTxt = "\t"

        newText = (self.editor["text"][0:self.editor["cursorPos"]]) + addTxt + (self.editor["text"][self.editor["cursorPos"]:])

        if not self.validateText(newText):
            return False
        
        self.editor["text"] = newText
        self.editor["cursorPos"] += 1
        if txt == "\n":
            self.editor["cursorPosY"] += 1
        
        return True

    def moveCursor(self, x, y):
        self.editor["cursorPosX"] += x
        self.editor["cursorPosY"] += y

        # Handle change in X
        if self.editor["cursorPosX"] < 0:
            if self.editor["cursorPosY"] > 0:
                self.editor["cursorPosY"] -= 1
            else:
                self.editor["cursorPosX"] = 0
        
        # Handle change in Y
        if self.editor["cursorPosY"] < 0:
            self.editor["cursorPosY"] = 0
        elif self.editor["cursorPosY"] > self.editor["text"].count("\n"):
            self.addChar("\n")

    def removeChar(self):
        if self.editor["cursorPos"] > 0:
            self.editor["text"] = (self.editor["text"][0 : self.editor["cursorPos"] - 1]) + (self.editor["text"][self.editor["cursorPos"]:])
            self.editor["cursorPos"] -= 1
        
    def show(self):
        self.line_index = 0
        self.updateDisplay(True)
        self.show_screen()
        self.vars.display.sleepUpdate(None, True)

        while True:
            keypress = self.vars.keypad.get_key()

            self.receive()

            if self.vars.display.sleepUpdate(keypress):
                continue

            if keypress is not None:
                print("keypress -> ", keypress)
                useXY = False
                
                self._gc()
                if keypress["key"] == "alt":
                    if keypress["longPress"]:
                        self.vars.keypad.keyLayoutLocked = not self.vars.keypad.keyLayoutLocked
                    else:
                        self.vars.keypad.keyLayoutLocked = False
                        self.vars.keypad.change_keyboardLayout()
                elif keypress["longPress"] and (keypress["key"] == "ent" or keypress["key"] == "rt" or keypress["key"] == "dn"):
                    self.addChar("\n")
                elif keypress["key"] == "bsp":
                    self.removeChar()
                elif keypress["key"] == "up":
                    self.moveCursor(0, -1)
                    useXY = True
                elif keypress["key"] == "dn":
                    self.moveCursor(0, 1)
                    useXY = True
                elif keypress["key"] == "lt":
                    self.moveCursor(-1, 0)
                    useXY = True
                elif keypress["key"] == "rt":
                    self.moveCursor(1, 0)
                    useXY = True
                elif keypress["key"] == "ent":
                    self.vars.sound.ring()
                    confResult = self.showConfirmation()
                    
                    if confResult == "Y":
                        return self.editor["text"].rstrip()
                    elif confResult == "N":
                        return None
                else:
                    self.addChar(keypress["key"])
                    
                    if not self.vars.keypad.keyLayoutLocked:
                        self.vars.keypad.change_keyboardLayout(True)
                
                self.updateDisplay(useXY)
                
                self.show_screen()

    def updateDisplay(self, useXY = False):
        editor = self.editor
        lines = self.lines

        displayLines = editor["text"].splitlines()
        loopPos = 0

        # determine which lines to display (Allow for vertical scrolling)
        startLine = 0
        if self.visibleLines - editor["cursorPosY"] <= 0:
            startLine = (editor["cursorPosY"] - self.visibleLines) + 1
        
        endLine = startLine + self.visibleLines - 1
        dspLn = 0
        displayLines.append("")
        
        for i in range(0, len(displayLines)):
            lineHasCursor = False
            if i > 0:
                loopPos += 1  # Count newline char

            if not useXY:
                if loopPos + len(displayLines[i]) >= editor["cursorPos"] and loopPos <= editor["cursorPos"]:
                    editor["cursorPosX"] = editor["cursorPos"] - loopPos
                    editor["cursorPosY"] = i
                    lineHasCursor = True
            else:
                if editor["cursorPosY"] == i:
                    if editor["cursorPosX"] > len(displayLines[i]) and editor["cursorPosX"] < len(displayLines):
                        editor["cursorPosY"] += 1
                        editor["cursorPosX"] = 0
                    else:
                        if editor["cursorPosX"] == -1 or editor["cursorPosX"] > len(displayLines[i]):
                            editor["cursorPosX"] = len(displayLines[i])
                        editor["cursorPos"] = loopPos + editor["cursorPosX"]
                        lineHasCursor = True
            
            loopPos += len(displayLines[i])

            if dspLn >= startLine and dspLn <= endLine:
                linetxt = ""
                if lineHasCursor:
                    linetxt = (displayLines[i][0:editor["cursorPosX"]]) + "_" + (displayLines[i][editor["cursorPosX"]:])
                else:
                    linetxt = displayLines[i]
                lines[1 + (dspLn - startLine)] = Line(linetxt, SimpleTextDisplay.WHITE)
            dspLn += 1
        
        while dspLn < endLine + 1:
            lines[1 + (dspLn - startLine)] = Line("", SimpleTextDisplay.WHITE)
            dspLn += 1
        
        # Update last line/prompts
        if editor["maxLines"] == 1 and self.vars.keypad.keyboard_current_idx == 2:
            lines[len(lines) - 1] = Line("", SimpleTextDisplay.GREEN)
        else:
            lines[len(lines) - 1] = \
                self.actionLine26[self.vars.keypad.keyboard_current_idx] \
                if self.vars.display.width_chars >= 26 \
                else self.actionLine20[self.vars.keypad.keyboard_current_idx]

    def validateText(self, text):
        if self.editor["maxLen"] > 0 and len(self.editor["text"]) > self.editor["maxLen"]:
            self.showConfirmation(message="Text too long", okOnly = True, message2="Max Len=" + str(self.editor["maxLen"]))
            return False
        
        if self.editor["maxLines"] > 0 and text.count("\n") >= self.editor["maxLines"]:
            self.showConfirmation(message="Too many lines", okOnly = True, message2="Max Lines=" + str(self.editor["maxLines"]))
            return False

        if len(self.editor["validation"]) > 0:
            validationPattern = None
            try:
                validationPattern = re.compile(self.editor["validation"])
            
            except:
                print("ERROR: Validation RegEx is invalid -> ", self.editor["validation"])
                print("WARNING: Validation check will return true.")
                return True

            if not re.match(validationPattern, text):
                self.showConfirmation(message=self.editor["validationMsg1"], okOnly = True, message2=self.editor["validationMsg2"])
                return False

        return True