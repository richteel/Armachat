'''

'''

from armachat import hw
import adafruit_matrixkeypad
import time


class keyboard(object):
    def __init__(self):
        self.keyboards = [
            ({"keys" : hw.keys1, "layout" : "abc"}),
            ({"keys" : hw.keys3, "layout" : "ABC"}),
            ({"keys" : hw.keys2, "layout" : "123"})
        ]

        self.keyboard_current_idx = 0

        self._keypad = adafruit_matrixkeypad.Matrix_Keypad(
                hw.keypad_rows, hw.keypad_cols,
                self.keyboards[self.keyboard_current_idx]["keys"]
            )

        self.keyLayout = self.keyboards[self.keyboard_current_idx]["layout"]
        self.keyLayoutLocked = False
        self.alt_is_esc = True

    def change_keyboardLayout(self, reset=False):
        if reset:
            self.keyboard_current_idx = 0
        else:
            self.keyboard_current_idx += 1

        if self.keyboard_current_idx >= len(self.keyboards):
            self.keyboard_current_idx = 0

        self._keypad = adafruit_matrixkeypad.Matrix_Keypad(
                hw.keypad_rows, hw.keypad_cols,
                self.keyboards[self.keyboard_current_idx]["keys"]
            )

        self.keyLayout = self.keyboards[self.keyboard_current_idx]["layout"]

    def get_key(self):
        LONG_PRESS_TIME = 0.5
        keys = self._keypad.pressed_keys

        if len(keys) == 0:
            return None

        pressedTime = time.monotonic()
        pressedKey = keys[0]
        pressDuration = 0.0
        releasedTime = 0.0

        while len(self._keypad.pressed_keys) > 0:
            pass

        releasedTime = time.monotonic()
        pressDuration = releasedTime - pressedTime

        longPress = False

        if pressDuration >= LONG_PRESS_TIME:
            longPress = True
            
        '''
        if pressedKey == "alt" and not self.alt_is_esc:
            if longPress:
                self.keyLayoutLocked = not self.keyLayoutLocked
            else:
                self.keyLayoutLocked = False
                self.change_keyboardLayout()
        elif pressedKey == "alt" and self.alt_is_esc:
            # pressedKey = "esc"
            self.change_keyboardLayout(True)
        elif not self.keyLayoutLocked and self.keyboard_current_idx != 0:
            self.change_keyboardLayout(True)
        '''

        return {"key" : pressedKey, "longPress" : longPress}

    def toggleBacklight(self):
        if hw.keyboard_bl is None:
            return False
        
        hw.keyboard_bl.value = not hw.keyboard_bl.value
        return True