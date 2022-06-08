import gc
from armachat import config
from armachat import hw
from armachat import ringtone as melody
import time
from pwmio import PWMOut

class audio():
    def __init__(self, keypad=None):
        self.keypad = keypad
        self.melody = melody

    def _getFreq(self, freq=0, defaultFreq=5000):
        retVal = freq
        # Humans 20 Hz to 20 KHz
        if retVal < 20:
            retVal = config.tone
        if retVal <= 200 or freq > 20000:
            retVal = defaultFreq
        
        return retVal

    def beep(self, freq=0):
        self.play_tone(self._getFreq(freq), 0.002)

    def get_melodyLength(self, idx):
        if idx < 0 or idx > len(melody.melodies) -1:
            return None
        
        return melody.melodies[idx]["time"]

    def get_melodyName(self, idx):
        if idx < 0 or idx > len(melody.melodies) -1:
            return None
        
        return melody.melodies[idx]["name"]

    def get_melodyNames(self):
        retVal = []

        for song in melody.melodies:
            retVal += [song["name"]]
        
        return retVal

    def note(self, name):
        if name is None:
            return 0

        octave = int(name[-1])
        PITCHES = "c,c#,d,d#,e,f,f#,g,g#,a,a#,b".split(",")
        pitch = PITCHES.index(name[:-1].lower())
        return 440 * 2 ** ((octave - 4) + (pitch - 9) / 12.)
    
    # REF: https://blog.wokwi.com/play-musical-notes-on-circuitpython/
    def play_melody(self, melodyIndex):
        gc.collect()
        if melodyIndex < 0:
            melodyIndex = 0
        elif melodyIndex >= len(melody.melodies):
            melodyIndex = len(melody.melodies) - 1

        sequence = melody.melodies[melodyIndex]["sequence"]
        tempo = melody.melodies[melodyIndex]["tempo"]
        wholeInSec = 1/((tempo/60)/4)
        totalTimeInSec = melody.melodies[melodyIndex]["time"]

        print("Playing ", melody.melodies[melodyIndex]["name"])
        print("with tempo of {} bpm", tempo)
        print("and a whole note at {} seconds", wholeInSec)
        print("Total time {} seconds", totalTimeInSec)

        for (notename, eighths) in sequence:
            if self.keypad is not None:
                if self.keypad.get_key() is not None:
                    return
            self.play_tone(self.note(notename), eighths * (wholeInSec/8))
            time.sleep(wholeInSec/64)
        gc.collect()

    def play_tone(self, freq, length):
        '''
        if freq == 0:
            print("Rest\t{}".format(length))
        else:
            print("{}\t{}".format(freq, length))
        '''

        if hw.audio_gpio is None:
            return
        
        if freq > 0:
            audioPin = PWMOut(hw.audio_gpio, duty_cycle=0, frequency=440, variable_frequency=True)
            audioPin.frequency = int(freq)
            audioPin.duty_cycle = 1000 * (config.volume)  # Full PWM range from 0 to 65535
            time.sleep(length)
            audioPin.duty_cycle = 0
            audioPin.deinit()
        else:
            time.sleep(length)

    def ring(self, freq=0):
        if hw.audio_gpio is None:
            return

        audioPin = PWMOut(hw.audio_gpio, duty_cycle=0, frequency=440, variable_frequency=True)
        audioPin.frequency = int(self._getFreq(freq) * 0.4)
        audioPin.duty_cycle = 1000 * (config.volume)
        time.sleep(0.1)
        audioPin.frequency = int(self._getFreq(freq) * 0.6)
        audioPin.duty_cycle = 1000 * (config.volume)
        time.sleep(0.1)
        audioPin.frequency = int(self._getFreq(freq) * 1.2)
        audioPin.duty_cycle = 1000 * (config.volume)
        time.sleep(0.1)
        audioPin.duty_cycle = 0
        audioPin.deinit()
