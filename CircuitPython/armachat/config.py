import os
import math
from armachat import ringtone

'''
    Values saved to config.txt
'''
# Brightness may be from 0 to 4
bright = 4

# Volume may be from 0 to 6
volume = 4

# Sleep may be 0 to 6
#	0 = Never		4 = 120
#	1 = 15 secs		5 = 300
#	2 = 30 secs		6 = 600
#	3 = 60
sleep = 0

# Tone may be from 1000 to 10000 in steps of 1000
tone = 5000

# Melody may be from 0 to length of items minus one, in melodies list of the 
# included melody file in audio.py
melody = 0

# LoRa Profile may be from 1 to 6
# Matches Mestastic values in table at
# https://meshtastic.org/docs/settings/channel
#	1 = Bw500Cr45Sf128       Short/Fast
#	2 = Bw125Cr45Sf128       Short/Slow
#	3 = Bw250Cr47Sf1024      Medium/Fast
#	4 = Bw250Cr46Sf2048      Medium/Slow
#	5 = Bw31_25Cr48Sf512     Long/Fast
#	6 = Bw125Cr48Sf4096      Long/Slow
loraProfile = 1

# Region values may be US, EU433, EU868, CN, JP, ANZ, RU, KR, TW, IN, NZ865, TH, Unset
region = "Unset"

# Frequency values are dependant on the module freq
freq = 915.0

# Power values may be 5 to 23
power = 5

theme = 1
hopLimit = 3
myName = "DemoUser"
destinations = "Test 1|12-36-124-1|Test 2|12-36-124-2|Test 3|12-36-124-3"
font = 2
groupMask = "255-255-255-0"
password = "Sixteen byte key"
myAddress = "12-36-124-3"
unitName = "ARMACHAT"
passwordIv = "Sixteen byte key"

'''
    Values not saved to config.txt
    Included in config_excludeNames
'''
# Model value may be max, compact, or watch
model = "compact"

# ----------         End of Settings          ----------
# ---------- Start read/write config.txt file ----------

# File Open Modes
# r -> read
# rb -> read binary
# w -> write
# wb -> write binary
# a -> append
# ab -> append binary

CONFIG_FILENAME = "config.txt"
audio = None

config_settings = set()
config_excludeNames = {
    "CONFIG_FILENAME",
    "__file__",
    "__name__",
    "maxChars",
    "maxLines",
    "model"
    "audio"
}
config_includeTypes = {
    float,
    int,
    str
}

loraProfiles = [
    {"profile": 1, "modemPreset": (0x92, 0x74, 0x04), "modemPresetConfig": "Bw500Cr45Sf128", "modemPresetDescription": "Short/Fast", "bw": 500},
    {"profile": 2, "modemPreset": (0x72, 0x74, 0x04), "modemPresetConfig": "Bw125Cr45Sf128", "modemPresetDescription": "Short/Slow", "bw": 125},
    {"profile": 3, "modemPreset": (0x82, 0xA4, 0x04), "modemPresetConfig": "Bw250Cr47Sf1024", "modemPresetDescription": "Medium/Fast", "bw": 250},
    {"profile": 4, "modemPreset": (0x84, 0xB4, 0x04), "modemPresetConfig": "Bw250Cr46Sf2048", "modemPresetDescription": "Medium/Slow", "bw": 250},
    {"profile": 5, "modemPreset": (0x48, 0x94, 0x04), "modemPresetConfig": "Bw31_25Cr48Sf512", "modemPresetDescription": "Long/Fast", "bw": 31.25},
    {"profile": 6, "modemPreset": (0x78, 0xC4, 0x0C), "modemPresetConfig": "Bw125Cr48Sf4096", "modemPresetDescription": "Long/Slow", "bw": 125},
]

regions = [
    {"region": "US", "freqCenter": 915.0, "freqStart": 902.0, "freqEnd": 928.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 30},
    {"region": "EU433", "freqCenter": 433.5, "freqStart": 433.0, "freqEnd": 434.0, "dutyCycle": 10, "spacing": 0, "powerLimit": 12},
    {"region": "EU868", "freqCenter": 869.525, "freqStart": 869.4, "freqEnd": 869.65, "dutyCycle": 10, "spacing": 0, "powerLimit": 16},
    {"region": "CN", "freqCenter": 490.0, "freqStart": 470.0, "freqEnd": 510.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 19},
    {"region": "JP", "freqCenter": 924.3, "freqStart": 920.8, "freqEnd": 927.8, "dutyCycle": 100, "spacing": 0, "powerLimit": 16},
    {"region": "ANZ", "freqCenter": 921.5, "freqStart": 915.0, "freqEnd": 928.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 30},
    {"region": "RU", "freqCenter": 868.95, "freqStart": 868.7, "freqEnd": 869.2, "dutyCycle": 100, "spacing": 0, "powerLimit": 20},
    {"region": "KR", "freqCenter": 921.5, "freqStart": 920.0, "freqEnd": 923.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 0},
    {"region": "TW", "freqCenter": 922.5, "freqStart": 920.0, "freqEnd": 925.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 0},
    {"region": "IN", "freqCenter": 866.0, "freqStart": 865.0, "freqEnd": 867.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 30},
    {"region": "NZ865", "freqCenter": 866.0, "freqStart": 864.0, "freqEnd": 868.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 0},
    {"region": "TH", "freqCenter": 922.5, "freqStart": 920.0, "freqEnd": 925.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 16},
    {"region": "Unset", "freqCenter": 915.0, "freqStart": 902.0, "freqEnd": 928.0, "dutyCycle": 100, "spacing": 0, "powerLimit": 30},
]

def printValue(name, val):
    print(name +" (", type, ") -> ", val)

def fileExists(fileName):
    retVal = False

    try:
        with open(fileName, "r") as f:
            f.readlines()
            retVal = True
    except OSError:
        print(fileName + " does not exist")

    return retVal


def fileSystemWriteMode():
    retVal = False
    testFileName = "delete.txt"

    try:
        with open(testFileName, "w") as f:
            f.write("test\n")
            retVal = True

        os.remove(testFileName)
    except OSError:
        print("config.py - Read Only File System")

    return retVal


def getChannel():
    regionObj = getRegion()
    profileObj = getProfile()

    channel = math.floor((freq - regionObj["freqStart"])/((profileObj["bw"] + regionObj["spacing"])/1000))
    return channel

def getChannelWidth():
    regionObj = getRegion()
    profileObj = getProfile()
    return (profileObj["bw"] + regionObj["spacing"])/1000

def getConfigProperties():
    my_globals = globals()
    for g in my_globals:
        if g not in config_excludeNames:
            if type(globals()[g]) in config_includeTypes:
                config_settings.add(g)


def getProfile():
    return loraProfiles[loraProfile - 1]

def getRegion():
    for r in range(len(regions)):
        if regions[r]["region"] == region:
            return regions[r]
    
    return None

def isProfileAllowedInRegion():
    if loraProfile < 1 or loraProfile > len(loraProfiles) - 1:
        return False
    
    regionObj = getRegion()
    profileObj = getProfile()

    if regionObj is None or profileObj is None:
            return False

    freqBand = (regionObj["freqEnd"] - regionObj["freqStart"]) * 1000
    if freqBand < profileObj["bw"]:
        return False
    
    return True

# printConfigProperties is useful for debugging and may be removed
def printConfigProperties():
    i = 1
    for c in config_settings:
        # print(str(i) + chr(9) + c + chr(9) + str(globals()[c]))

        if str(type(globals()[c])) == "<class 'str'>":
            print(c + " = \"" + str(globals()[c]) + "\"")
        else:
            print(c + " = " + str(globals()[c]))
        i = i + 1


def readConfig(createIfNotExists=False):
    if len(config_settings) == 0:
        getConfigProperties()

    if not fileExists(CONFIG_FILENAME):
        if createIfNotExists:
            writeConfig()
        return False

    with open(CONFIG_FILENAME, "r") as f:
        conf = f.readlines()
        print("Reading config:")
        for line in conf:
            if line.strip().startswith("#"):  # Ignore comment
                continue

            keyvalPair = line.split("=")

            if(len(keyvalPair) != 2):  # Ignore not key value pair
                continue

            key = keyvalPair[0].strip()
            value = keyvalPair[1].strip()

            if key not in config_settings:  # Ignore key is not a setting
                continue

            if isinstance(globals()[key], str):
                if value.startswith("\"") and value.endswith("\""):
                    value = value[1:-1]
                globals()[key] = value
            elif isinstance(globals()[key], int):
                globals()[key] = int(value)
            elif isinstance(globals()[key], float):
                globals()[key] = float(value)

    return True

def setFreqToCenterFreq():
    regionObj = getRegion()
    globals()["freq"] = (regionObj["freqEnd"] + regionObj["freqStart"])/2
    print("globals()[\"freq\"] -> ", globals()["freq"])
    setFreqToCenterOfChannel()
    print("globals()[\"freq\"] -> ", globals()["freq"])

def setFreqToCenterOfChannel():
    regionObj = getRegion()
    channel = getChannel()
    channelWidth = getChannelWidth()
    # Make certain the freq is in the center of the channel
    globals()["freq"] = (((channel + 1) * channelWidth) + regionObj["freqStart"]) - (channelWidth/2)

def validateAllSettings():
    allvalid = True
    my_globals = globals()
    for g in my_globals:
        if g not in config_excludeNames:
            if type(globals()[g]) in config_includeTypes:
                if not validateSetting(g):
                    print("Setting not valid -> ", g)
                    allvalid = False
    
    return allvalid

def validateSetting(name):
    startVal = globals()[name]
    minval = 0
    maxval = 0

    if name == "bright":
        maxval = 4
    elif name == "volume":
        maxval = 6
    elif name == "sleep":
        maxval = 6
    elif name == "tone":
        minval = 1000
        maxval = 10000
    elif name == "melody":
        maxval = ringtone.melodiesLen() - 1
    elif name == "loraProfile":
        minval = 1
        maxval = len(loraProfiles)
    elif name == "region":
        foundRegion = False
        for reg in regions:
            if reg["region"] == globals()[name]:
                foundRegion = True
                break
        if not foundRegion:
            globals()[name] = "unset"
            regionObj = getRegion()
            if regionObj is not None:
                globals()["freq"] = regionObj["freqCenter"]
                setFreqToCenterOfChannel()
                return False
    elif name == "freq":
        regionObj = getRegion()
        profileObj = getProfile()

        if regionObj is not None and profileObj is not None:
            minval = regionObj["freqStart"] + (profileObj["bw"]/2000)
            maxval = regionObj["freqEnd"] - (profileObj["bw"]/2000)
    elif name == "power":
        regionObj = getRegion()

        if regionObj is not None:
            maxval = regionObj["powerLimit"]
    
    # if min and max values are different, check them
    if maxval != minval and maxval > minval:
        if globals()[name] < minval:
            globals()[name] = minval
        elif globals()[name] > maxval:
            globals()[name] = maxval

    # need to do one more validation on region and loraProfile
    if name == "region" or name == "loraProfile":
        if not isProfileAllowedInRegion():
            globals()["loraProfile"] = 5  # BW = 31.25 KHz
            setFreqToCenterFreq()
            setFreqToCenterOfChannel()
            return False

    return startVal == globals()[name]

def writeConfig():
    if len(config_settings) == 0:
        getConfigProperties()

    # Create dict to track if items have been saved
    configTrackDict = {}
    for k in config_settings:
        configTrackDict[k] = False

    # printValue("configTrackDict", configTrackDict)

    if not fileSystemWriteMode():
        print("Cannot write config file.")
        return False

    # Recover from previous failure #
    # If the old config file exists, assume a failure last time.
    # Copy the old config file back and try again.
    # This will cause an issue if the original configuration file
    # was the source of the issue and the code has not changed to
    # address the issue.
    if fileExists(CONFIG_FILENAME + ".old"):
        if fileExists(CONFIG_FILENAME):
            os.remove(CONFIG_FILENAME)
        os.rename(CONFIG_FILENAME + ".old", CONFIG_FILENAME)

    # if the config file exists, rename it then delete it
    if fileExists(CONFIG_FILENAME):
        os.rename(CONFIG_FILENAME, CONFIG_FILENAME + ".old")
    
    with open(CONFIG_FILENAME, "w") as f_new:
        # if a previous config file exists, keep comments and formats for existing values
        if fileExists(CONFIG_FILENAME + ".old"):
            with open(CONFIG_FILENAME + ".old", "r") as f_old:
                    conf_old = f_old.readlines()
                    for line in conf_old:
                        if line.strip().startswith("#"):  # Comment
                            writeConfigLine(f_new, line)
                            continue

                        keyvalPair = line.split("=")
                        if(len(keyvalPair) != 2):  # Not key value pair
                            writeConfigLine(f_new, line)
                            continue

                        key = keyvalPair[0].strip()

                        if key not in config_settings:  # Ignore key is not a setting
                            writeConfigLine(f_new, line)
                        elif isinstance(globals()[key], str):
                            writeConfigLine(f_new, key + " = \"" + globals()[key] + "\"")
                            configTrackDict[key] = True
                        else:
                            writeConfigLine(f_new, key + " = " + str(globals()[key]))
                            configTrackDict[key] = True

        for dkey, dval in configTrackDict.items():
            if not dval:
                if isinstance(globals()[dkey], str):
                    writeConfigLine(f_new, dkey + " = \"" + globals()[dkey] + "\"")
                else:
                    writeConfigLine(f_new, dkey + " = " + str(globals()[dkey]))

    if fileExists(CONFIG_FILENAME + ".old"):
        os.remove(CONFIG_FILENAME + ".old")

    return True

def writeConfigLine(f, line):
    if line.endswith("\n"):
        f.write(line)
    else:
        f.write(line + "\n")


readConfig()

if not validateAllSettings():
    print("One or more settings are not valid")
    printConfigProperties()
    writeConfig()
else:
    print("All settings are valid")

setFreqToCenterOfChannel()