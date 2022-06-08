from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from armachat.ui_setup_id import ui_setup_id as ui_setup_id
from armachat import config

class ui_setup_radio(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        if self.vars.display.width_chars >= 26:
            self.lines = [
                Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
                Line("0 Radio:", SimpleTextDisplay.GREEN),
                Line("[R] Region: %region%", SimpleTextDisplay.WHITE),
                Line("[F] Frequency: %freq% MHz", SimpleTextDisplay.WHITE),
                Line("    Channel: %channel%", SimpleTextDisplay.WHITE),
                Line("[P] Power: %power%", SimpleTextDisplay.WHITE),
                Line("[S] Profile: %profile%", SimpleTextDisplay.WHITE),
                Line("%profileName%", SimpleTextDisplay.WHITE),
                Line("%profileDesc%", SimpleTextDisplay.WHITE),
                Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
            ]
        else:
            self.lines = [
                Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
                Line("0 Radio:", SimpleTextDisplay.GREEN),
                Line("[R] Region: %region%", SimpleTextDisplay.WHITE),
                Line("[F] Freq: %freq% MHz", SimpleTextDisplay.WHITE),
                Line("    Channel: %channel%", SimpleTextDisplay.WHITE),
                Line("[P] Power: %power%", SimpleTextDisplay.WHITE),
                Line("[S] Profile: %profile%", SimpleTextDisplay.WHITE),
                Line("%profileName%", SimpleTextDisplay.WHITE),
                Line("%profileDesc%", SimpleTextDisplay.WHITE),
                Line("ALT-Ex [ENT]> [DEL]<", SimpleTextDisplay.RED)
            ]

    def getRegionIndex(self, region):
        for r in range(len(config.regions)):
            if config.regions[r]["region"] == region:
                return r
        
        return None

    def _getNextBestProfile(self, step=1):
        print("Entered _getNextBestProfile()")
        region = config.getRegion()
        profile = config.getProfile()

        if region is None or profile is None:
            return

        regionBW = (region["freqEnd"] - region["freqStart"]) * 1000
        profileBW = profile["bw"]

        print("config.region -> ", config.region)
        print("regionBW -> ", regionBW)
        print("config.loraProfile -> ", config.loraProfile)
        print("profileBW -> ", profileBW)


        # while config.loraProfile > 0 and config.loraProfile < len(config.loraProfiles):
        loopCount = 0
        dirMult = 1
        while profileBW > regionBW and loopCount < 2 * len(config.loraProfiles):
            print("Entered _getNextBestProfile() loop")
            nextVal = config.loraProfile + (dirMult * step)
            if nextVal < 1 or nextVal > len(config.loraProfiles):
                dirMult = dirMult * -1
                nextVal = config.loraProfile + (dirMult * step)
            
            config.loraProfile = nextVal
            profile = config.getProfile()
            profileBW = profile["bw"]

            print("config.region -> ", config.region)
            print("regionBW -> ", regionBW)
            print("config.loraProfile -> ", config.loraProfile)
            print("profileBW -> ", profileBW)
            print("loopCount -> ", loopCount)
            
            loopCount += 1

        
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
                    elif keypress["key"] == "ent":
                        self.vars.sound.ring()
                        gui_setup_next = ui_setup_id(self.vars)
                        if gui_setup_next.show() == None:
                            return None
                        self.line_index = 0
                        self.show_screen()
                    elif keypress["key"] == "bsp":
                        self.vars.sound.ring()
                        return keypress
                    elif keypress["key"] == "f":
                        preval = config.freq
                        config.setFreqToCenterOfChannel()
                        channelWidth = config.getChannelWidth()

                        if keypress["longPress"]:
                            config.freq = config.freq - channelWidth
                        else:
                            config.freq = config.freq + channelWidth
                        config.validateSetting("freq")
                        if preval != config.freq:
                            config.writeConfig()
                            self.vars.radioInit()
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                        self.show_screen()
                    elif keypress["key"] == "p":
                        preval = config.power
                        if keypress["longPress"]:
                            config.power = self.changeValInt(config.power, 5, 23 , -1)
                        else:
                            config.power = self.changeValInt(config.power, 5, 23)
                        config.validateSetting("power")
                        if preval != config.power:
                            config.writeConfig()
                            self.vars.radioInit()
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                        self.show_screen()
                    elif keypress["key"] == "r":
                        preval = config.region
                        regionIdx = self.getRegionIndex(config.region)

                        if keypress["longPress"]:
                            if regionIdx > 0:
                                config.region = config.regions[regionIdx - 1]["region"]
                                self._getNextBestProfile(-1)
                        else:
                            if regionIdx + 1 < len(config.regions):
                                config.region = config.regions[regionIdx + 1]["region"]
                                self._getNextBestProfile(1)
                        
                        config.validateAllSettings()
                        if preval != config.region:
                            config.setFreqToCenterFreq()
                            config.setFreqToCenterOfChannel()
                            config.writeConfig()
                            self.vars.radioInit()
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                        self.show_screen()
                    elif keypress["key"] == "s":
                        preval = config.loraProfile
                        step = 1
                        if keypress["longPress"]:
                            config.loraProfile = self.changeValInt(config.loraProfile, 1, len(config.loraProfiles) , -1)
                            self._getNextBestProfile(-1)
                        else:
                            config.loraProfile = self.changeValInt(config.loraProfile, 1, len(config.loraProfiles))
                            self._getNextBestProfile(1)
                        
                        config.validateAllSettings()
                        if preval != config.loraProfile:
                            config.setFreqToCenterFreq()
                            config.setFreqToCenterOfChannel()
                            config.writeConfig()
                            self.vars.radioInit()
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                        self.show_screen()
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()
