from armachat import config
from armachat import ac_address
from armachat import audio
from armachat import display
from armachat import keyboard
from armachat import lora
from armachat import hw

class ac_globals(object):
    def __init__(self):
        self.keypad = keyboard.keyboard()
        self.display = display.display()
        self.sound = audio.audio(self.keypad)
        # self.radio = lora.LoRa(hw.spi)
        self.radioInit()
        self.address_book = self.loadAddressBook()
        self.to_dest_idx = 0
        self.messages = []
        # self.model = config.model
        self.messageCount = 0
    
    def loadAddressBook(self):
        broadcastAddressList = ac_address.broadcastAddressList(
            config.myAddress, config.groupMask
        )
        broadcastAddress = ac_address.addressLst2Str(broadcastAddressList)
        print("broadcastAddress -> ", broadcastAddress)
        # destinations = "Sammy|12-36-124-8|Tom|12-36-124-17|Sandy|12-36-124-3"
        parts = config.destinations.split("|")
        retVal = [{"name": "All", "address": broadcastAddress}]

        if len(parts) % 2 != 0:
            return retVal
        for i in range(0, len(parts), 2):
            retVal += [{"name": parts[i], "address": parts[i + 1]}]
        return retVal

    def radioInit(self):
        # try:
        
        unitAddress = ac_address.addressToList(config.myAddress)
        unitGroupMask = ac_address.addressToList(config.groupMask)
        modemPreset = config.loraProfiles[config.loraProfile - 1]["modemPreset"]

        self.radio = lora.LoRa(
            hw.lora_spi,
            hw.lora_cs,
            this_address=unitAddress,
            group_mask=unitGroupMask,
            hop_limit=config.hopLimit,
            freq=config.freq,
            tx_power=config.power,
            modem_config=modemPreset,
        )  # , interrupt=28
        '''
        except Exception as e:
            log.logMessage("radioInit", "Lora module not detected !!!",
                        ac_log.LogType.ERROR)
            log.logMessage("radioInit", "ERROR -> " + str(e), ac_log.LogType.ERROR)
        '''