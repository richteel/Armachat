from adafruit_simple_text_display import SimpleTextDisplay
from armachat import hw
from armachat import config
import time

class display(object):
    def __init__(self):
        self.screen = None

        self.width_chars = hw.maxChars
        self.height_lines = hw.maxLines
        self.display = hw.display
        self.font = hw.font
        self._lastBrightness = self.display.brightness
        self._brightsteps = [0.01, 0.05, 0.1, 0.5, 1.0]
        self._lastKeyPress = time.monotonic()
        self._sleep = False
        self._sleepsteps = [0, 15, 30, 60, 120, 300, 600]

        if config.sleep < 0 or config.sleep > len(self._sleepsteps):
            config.sleep = 0
            config.writeConfig()
        
        self.set_brightness(config.bright)

    def get_brightness(self):
        return self.display.brightness
    
    # used by z & x to decrease and increase display brightness
    def incBacklight(self, step):
        if hw.tft_backlight is None:
            return

        bright_start = self.get_brightness()

        config.bright += step

        self.set_brightness(config.bright)

        return self.get_brightness() != bright_start

    def set_brightness(self, step):
        config.bright = step

        if config.bright < 0:
            config.bright = 0
        elif config.bright >= len(self._brightsteps):
            config.bright = len(self._brightsteps) - 1
        
        self.display.brightness = self._brightsteps[config.bright]
        self._lastBrightness = self.display.brightness

        config.writeConfig()

    def get_sleepStep(self):
        if config.sleep < 0:
            config.sleep = 0
            config.writeConfig()
        elif config.sleep > len(self._sleepsteps):
            config.sleep = len(self._sleepsteps) - 1
            config.writeConfig()

        return config.sleep
        
    def get_sleepTime(self):
        return self._sleepsteps[self.get_sleepStep()]
    
    def incSleep(self, step):
        sleep_start = config.sleep

        config.sleep += step

        self.set_sleep(config.sleep)

        return self.get_sleepStep() != sleep_start

    def set_sleep(self, step):
        config.sleep = step

        if config.sleep < 0:
            config.sleep = 0
        elif config.sleep >= len(self._sleepsteps):
            config.sleep = len(self._sleepsteps) - 1
        
        config.writeConfig()

    def sleepUpdate(self, keypress, initTimer=False):
        beginSleepState = self._sleep

        if keypress is not None or initTimer:
            self._lastKeyPress = time.monotonic()
            # Wake up
            if self._sleep:
                self._sleep = False
                self.set_brightness(config.bright)
        else:
            now = time.monotonic()
            if config.sleep != 0 and now >= self._lastKeyPress + self._sleepsteps[config.sleep]:
                self._sleep = True
                self.display.brightness = 0

        return beginSleepState and not self._sleep

    def test(self):
        screenColors = (
            SimpleTextDisplay.GREEN,
        )
        
        for q in range(1, self.height_lines-1):
            screenColors += (SimpleTextDisplay.WHITE,)

        screenColors += (SimpleTextDisplay.RED,)

        self.screen = SimpleTextDisplay(
            display=self.display,
            font=self.font,
            text_scale=1,
            colors=screenColors
        )

        t = ""
        for i in range(1, self.width_chars + 1):
            t += str(i % 10)

        for j in range(0,self.height_lines):
            self.screen[j].text = t

        self.screen.show()

    def toggleBacklight(self):
        if hw.tft_backlight is None:
            return

        if self.display.brightness == 0.0:
            self.display.brightness = self._lastBrightness
        else:
            self._lastBrightness = self.display.brightness
            self.display.brightness = 0.0