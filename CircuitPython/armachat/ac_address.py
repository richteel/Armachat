import re


def addressLst2Str(address, separator="-"):
    if isinstance(address, bytes) or isinstance(address, bytearray):
        address = list(address)

    if not isinstance(address, list):
        print("addressLst2Str: type(address) ->", type(address))

    assert isinstance(address, list), "ERROR: addressLst2Str - Address is not a list"

    if len(address) != 4:
        return None

    retVal = ""

    for n in address:
        if n < 0 or n > 255:
            return None

        if len(retVal) > 0:
            retVal += separator

        retVal += str(n)

    return retVal


def addressToList(address, length=4):
    assert isinstance(address, str), "ERROR: addressToList - Address is not a string"

    try:
        regX = re.compile(",|\.|-|_|:|;")
        q = [int(x.strip()) for x in regX.split(address)]

        for s in q:
            if s < 0 or s > 255:
                # raise ValueError("ERROR in addressToList:
                #   Invalid address - Number not between 0 and 255 -> ", address)
                return None

        if len(q) == length:
            return q
        else:
            # raise ValueError("ERROR in addressToList:
            #   Invalid address - Expected " + length + " bytes -> ", address)
            return None
    except ValueError:
        # raise ValueError("ERROR in addressToList:
        #   Invalid address - Invalid character -> ", address)
        return None

def broadcastAddressList_List(address, mask=[255, 255, 255, 0]):
    assert isinstance(
        address, list
    ), "ERROR: broadcastAddressList - Address is not a list"

    addrStr = addressLst2Str(address)
    maskStr = addressLst2Str(mask)

    return broadcastAddressList(addrStr, maskStr)


def broadcastAddressList(address, mask="255-255-255-0"):
    assert isinstance(
        address, str
    ), "ERROR: broadcastAddressList - Address is not a string"

    # b = broadcastAddressBytes(address, mask)
    addrLst = addressToList(address)
    maskLst = addressToList(mask)
    retVal = []

    if addrLst is None or maskLst is None or len(addrLst) != 4 or len(maskLst) != 4:
        return None

    for i in range(0, 4):
        a = addrLst[i]
        m = maskLst[i]
        retVal += [a | ~m & 255]

    return retVal


def _unitTests():
    assert (
        addressToList("128-2-76-4") is not None
    ), 'ERROR: Test Failed - addressToList("128-2-76-4") returned None'

    assert (
        addressToList("128-2-76-400") is None
    ), 'ERROR: Test Failed - addressToList("128-2-76-400") did not return None'

    assert (
        addressToList("128-2-f0-4") is None
    ), 'ERROR: Test Failed - addressToList("128-2-f0-4") did not return None'

    assert addressToList("128-2-76-4") == [
        128,
        2,
        76,
        4,
    ], 'ERROR: Test Failed - addressToList("128-2-76-4") returned incorrect value'

    assert (
        addressLst2Str([64, 12, 88, 5]) is not None
    ), "ERROR: Test Failed - addressLst2Str([64, 12, 88, 5]) returned None"

    assert (
        addressLst2Str([64, 12, 88, 500]) is None
    ), "ERROR: Test Failed - addressLst2Str([64, 12, 88, 500]) did not return None"

    assert (
        addressLst2Str([64, 12, 88, 5]) == "64-12-88-5"
    ), "ERROR: Test Failed - addressLst2Str([64, 12, 88, 5]) returned incorrect value"

    assert broadcastAddressList("128-2-76-4") == [
        128,
        2,
        76,
        255,
    ], 'ERROR: Test Failed - broadcastAddressList("128-2-76-255") " + \
       "returned incorrect value'

    assert (
        broadcastAddressList("128-2-76-400") is None
    ), 'ERROR: Test Failed - broadcastAddressList("128-2-76-400") did not return None'


_unitTests()
