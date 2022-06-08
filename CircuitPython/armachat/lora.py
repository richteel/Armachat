import time
import adafruit_bus_device.spi_device as spidev
import aesio
from armachat import ac_address
from armachat import ac_log
from armachat import config

# Constants
FLAGS_ACK = 0x80
BROADCAST_ADDRESS = 255

REG_00_FIFO = 0x00
REG_01_OP_MODE = 0x01
REG_06_FRF_MSB = 0x06
REG_07_FRF_MID = 0x07
REG_08_FRF_LSB = 0x08
REG_0E_FIFO_TX_BASE_ADDR = 0x0E
REG_0F_FIFO_RX_BASE_ADDR = 0x0F
REG_10_FIFO_RX_CURRENT_ADDR = 0x10
REG_12_IRQ_FLAGS = 0x12
REG_13_RX_NB_BYTES = 0x13
REG_1D_MODEM_CONFIG1 = 0x1D
REG_1E_MODEM_CONFIG2 = 0x1E
REG_19_PKT_SNR_VALUE = 0x19
REG_1A_PKT_RSSI_VALUE = 0x1A
REG_20_PREAMBLE_MSB = 0x20
REG_21_PREAMBLE_LSB = 0x21
REG_22_PAYLOAD_LENGTH = 0x22
REG_26_MODEM_CONFIG3 = 0x26

REG_4D_PA_DAC = 0x4D
REG_40_DIO_MAPPING1 = 0x40
REG_0D_FIFO_ADDR_PTR = 0x0D

PA_DAC_ENABLE = 0x07
PA_DAC_DISABLE = 0x04
PA_SELECT = 0x80

CAD_DETECTED_MASK = 0x01
RX_DONE = 0x40
TX_DONE = 0x08
CAD_DONE = 0x04
CAD_DETECTED = 0x01

LONG_RANGE_MODE = 0x80
MODE_SLEEP = 0x00
MODE_STDBY = 0x01
MODE_TX = 0x03
MODE_RXCONTINUOUS = 0x05
MODE_CAD = 0x07

REG_09_PA_CONFIG = 0x09
FXOSC = 32000000.0
FSTEP = FXOSC / 524288

'''
class ModemConfig:
    # Bw = 500kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on.
    Bw500Cr45Sf128 = (0x92, 0x74, 0x04)  # Short/Fast
    # Bw = 125kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on.
    Bw125Cr45Sf128 = (0x72, 0x74, 0x04)  # Short/Slow
    # Bw = 250kHz, Cr = 4/7, Sf = 1024chips/symbol, CRC on.
    Bw250Cr47Sf1024 = (0x82, 0xA4, 0x04)  # Medium/Fast
    # Bw = 250kHz, Cr = 4/6, Sf = 2048chips/symbol, CRC on.
    Bw250Cr46Sf2048 = (0x84, 0xB4, 0x04)  # Medium/Slow
    # Bw = 31.25kHz, Cr = 4/8, Sf = 512chips/symbol, CRC on.
    Bw31_25Cr48Sf512 = (0x48, 0x94, 0x04)  # Long/Fast
    # Bw = 125kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on.
    Bw125Cr48Sf4096 = (0x78, 0xC4, 0x0C)  # Long/Slow
'''

class LoRa(object):
    def __init__(
        self,
        spi,
        CS,
        this_address=[0, 0, 0, 0],
        group_mask=[255, 255, 255, 0],
        hop_limit=3,
        freq=915.25,
        tx_power=5,
        # modem_config=ModemConfig.Bw125Cr45Sf128,
        modem_config=(0x72, 0x74, 0x04),
        receive_all=False,
        acks=False,
        crypto=None,
    ):
        """
        channel: SPI channel, check SPIConfig for preconfigured names
        interrupt: GPIO interrupt pin
        this_address: set address for this device [0-254]
        cs_pin: chip select pin from microcontroller
        reset_pin: the GPIO used to reset the RFM9x if connected
        freq: frequency in MHz
        tx_power: transmit power in dBm
        modem_config: Check ModemConfig. Default is compatible with the Radiohead lib
        receive_all: if True, don't filter packets on address
        acks: if True, request acknowledgments
        crypto: if desired, an instance of ucrypto AES
            (https://docs.pycom.io/firmwareapi/micropython/ucrypto/) - not tested
        """

        self._mode = None
        self._cad = None
        self._freq = freq
        self._tx_power = tx_power
        self._modem_config = modem_config
        self._receive_all = receive_all
        self._acks = acks

        self.last_rssi = None
        self.last_snr = None
        self._this_address = this_address
        self._group_mask = group_mask
        self._hop_limit = hop_limit
        self._last_header_id = 0

        self.broadcastAddress = \
            ac_address.broadcastAddressList_List(self._this_address,
                                                 self._group_mask)

        self._last_payload = None
        self.crypto = crypto

        self.cad_timeout = 0
        self.send_retries = 2
        self.wait_packet_sent_timeout = 20.0
        self.retry_timeout = 0.2

        self.message_count = 0

        self.log = ac_log.log(pyFile="ac_lora.py", logFileName="ac_lora.txt")

        # check if modem_config is set to 3 bytes
        assert (
            len(self._modem_config) == 3
        ), "LoRa initialization failed - invalid modem_config"

        # check if this_address is set to 4 bytes
        assert (
            len(self._this_address) == 4
        ), "LoRa initialization failed - invalid this_address"

        # check if group_mask is set to 4 bytes
        assert (
            len(self._group_mask) == 4
        ), "LoRa initialization failed - invalid group_mask"

        # check if hop_limit is set to 4 bytes
        assert self._hop_limit < 256, "LoRa initialization failed - invalid hop_limit"

        self._device = spidev.SPIDevice(spi, CS, baudrate=5000000, polarity=0, phase=0)

        # set mode
        self._spi_write(REG_01_OP_MODE, MODE_SLEEP | LONG_RANGE_MODE)
        time.sleep(0.1)

        # check if mode is set
        assert self._spi_read(REG_01_OP_MODE) == (
            MODE_SLEEP | LONG_RANGE_MODE
        ), "LoRa initialization failed"

        self._spi_write(REG_0E_FIFO_TX_BASE_ADDR, 0)
        self._spi_write(REG_0F_FIFO_RX_BASE_ADDR, 0)

        self.set_mode_idle()

        # set modem config (Bw125Cr45Sf128)
        self._spi_write(REG_1D_MODEM_CONFIG1, self._modem_config[0])
        self._spi_write(REG_1E_MODEM_CONFIG2, self._modem_config[1])
        self._spi_write(REG_26_MODEM_CONFIG3, self._modem_config[2])

        # set preamble length (8)
        self._spi_write(REG_20_PREAMBLE_MSB, 0)
        self._spi_write(REG_21_PREAMBLE_LSB, 8)

        # set frequency
        frf = int((self._freq * 1000000.0) / FSTEP)
        self._spi_write(REG_06_FRF_MSB, (frf >> 16) & 0xFF)
        self._spi_write(REG_07_FRF_MID, (frf >> 8) & 0xFF)
        self._spi_write(REG_08_FRF_LSB, frf & 0xFF)

        # Set tx power
        if self._tx_power < 5:
            self._tx_power = 5
        if self._tx_power > 23:
            self._tx_power = 23

        if self._tx_power > 20:
            self._spi_write(REG_4D_PA_DAC, PA_DAC_ENABLE)
            self._tx_power -= 3
        else:
            self._spi_write(REG_4D_PA_DAC, PA_DAC_DISABLE)

        self._spi_write(REG_09_PA_CONFIG, PA_SELECT | (self._tx_power - 5))

    def decryptMessage(self, data):
        cipher = aesio.AES(
            bytes(config.password, "utf-8"),
            aesio.MODE_CTR,
            bytes(config.passwordIv, "utf-8"),
        )
        inp = bytes(data)
        outp = bytearray(len(inp))
        cipher.encrypt_into(inp, outp)

        try:
            packet_text = str(outp, "utf-8")
            return packet_text
        except UnicodeError as e:
            return ""

    def encryptMessage(self, messageText):
        outp = bytearray(len(messageText))
        cipher = aesio.AES(
            bytes(config.password, "utf-8"),
            aesio.MODE_CTR,
            bytes(config.passwordIv, "utf-8"),
        )
        cipher.encrypt_into(bytes(messageText, "utf-8"), outp)

        return outp

    def on_recv(self, message):
        # This should be overridden by the user
        pass

    def sleep(self):
        if self._mode != MODE_SLEEP:
            self._spi_write(REG_01_OP_MODE, MODE_SLEEP)
            self._mode = MODE_SLEEP

    def set_mode_tx(self):
        if self._mode != MODE_TX:
            self._spi_write(REG_01_OP_MODE, MODE_TX)
            self._spi_write(REG_40_DIO_MAPPING1, 0x40)  # Interrupt on TxDone
            self._mode = MODE_TX

    def set_mode_rx(self):
        if self._mode != MODE_RXCONTINUOUS:
            self._spi_write(REG_01_OP_MODE, MODE_RXCONTINUOUS)
            self._spi_write(REG_40_DIO_MAPPING1, 0x00)  # Interrupt on RxDone
            self._mode = MODE_RXCONTINUOUS

    def set_mode_cad(self):
        if self._mode != MODE_CAD:
            self._spi_write(REG_01_OP_MODE, MODE_CAD)
            self._spi_write(REG_40_DIO_MAPPING1, 0x80)  # Interrupt on CadDone
            self._mode = MODE_CAD

    def _is_channel_active(self):
        self.set_mode_cad()

        while self._mode == MODE_CAD:
            yield

        return self._cad

    def wait_cad(self):
        if not self.cad_timeout:
            return True

        start = time.monotonic()
        for status in self._is_channel_active():
            if time.monotonic() - start < self.cad_timeout:
                return False

            if status is None:
                time.sleep(0.1)
                continue
            else:
                return status

    def wait_packet_sent(self):
        # wait for `_handle_interrupt` to switch the mode back
        start = time.monotonic()
        while time.monotonic() - start < self.wait_packet_sent_timeout:
            if self._mode != MODE_TX:
                return True

        return False

    def set_mode_idle(self):
        if self._mode != MODE_STDBY:
            self._spi_write(REG_01_OP_MODE, MODE_STDBY)
            self._mode = MODE_STDBY

    def sendMessage(self, message):
        return self.send(
                            ac_address.addressToList(message["to"]), 
                            message["data"],
                            ac_address.addressToList(message["id"]), 
                            [message["flag0"], message["flag1"], message["flag2"], message["hops"]]
                        )

    def send(self, to, data, msgId, flags=None):
        """
        to - bytearray of 4 bytes
        data - bytearray also will accept and convert int, bytes, str, list
        msgId - bytearray of 4 bytes
        flags - bytearray of 4 bytes
        """

        msg_sent = False

        if to is None:
            self.log.logMessage("send",
                                "LoRa send failed - Must pass valid To Address",
                                ac_log.LogType.ERROR)
            return msg_sent

        if type(to) == list:
            to = bytearray(to)

        if not isinstance(to, bytearray) or len(to) != 4:
            self.log.logMessage("send",
                                "LoRa send failed - To Address must " +
                                "be a bytearray of 4 bytes",
                                ac_log.LogType.ERROR)
            return msg_sent
        if data is None or len(data) == 0:
            self.log.logMessage("send",
                                "LoRa send failed - Data cannot be None or empty",
                                ac_log.LogType.ERROR)
            return msg_sent
        if msgId is None:
            self.log.logMessage("send",
                                "LoRa send failed - Must pass valid msgId",
                                ac_log.LogType.ERROR)
            return msg_sent

        if type(msgId) == list:
            msgId = bytearray(msgId)

        if not isinstance(msgId, bytearray) or len(msgId) != 4:
            self.log.logMessage("send",
                                "LoRa send failed - msgId must be a " +
                                "bytearray of 4 bytes",
                                ac_log.LogType.ERROR)
            return msg_sent

        self.set_mode_idle()

        if type(flags) == list:
            flags = bytearray(flags)

        if flags is None:
            flags = bytearray([0, 0, 0, self._hop_limit])

        header = (
            to + bytearray(self._this_address) + msgId + flags
        )

        self.log.logValue("send", "header", header)

        if type(data) == int:
            data = [data]
        elif type(data) == bytes:
            data = [p for p in data]
        elif type(data) == str:
            data = [ord(s) for s in data]
        # elif type(data) == list:
        #    data = bytearray(data)

        self.log.logValue("send", "data", data)

        payload = list(header) + list(data)
        self.log.logValue("send", "payload", payload)
        # payload ->  [0, 0, 0, 0,
        #              19, 18, 17, 0,
        #              3, 2, 1, 1,
        #              115, 111, 198, 0,
        #              0, 0, 0, 3,
        #              92, 251, 53, 153,
        #              252, 1, 7, 13,
        #              97, 59]
        self._spi_write(REG_0D_FIFO_ADDR_PTR, 0)
        self._spi_write(REG_00_FIFO, payload)
        self._spi_write(REG_22_PAYLOAD_LENGTH, len(payload))

        self.set_mode_tx()
        start = time.monotonic()

        while time.monotonic() - start < self.wait_packet_sent_timeout:
            irq_flags = self._spi_read(REG_12_IRQ_FLAGS)
            if (irq_flags & TX_DONE) >> 3:
                msg_sent = True
                break

        self._spi_write(REG_12_IRQ_FLAGS, 0xFF)  # Clear all IRQ flags
        self.set_mode_idle()
        return msg_sent

    '''
    def send_to_wait(self, data, header_to, header_flags=0, retries=3):
        self._last_header_id += 1

        for _ in range(retries + 1):
            self.send(
                data,
                header_to,
                header_id=self._last_header_id,
                header_flags=header_flags,
            )
            self.set_mode_rx()

            # Don't wait for acks from a broadcast message
            if header_to == BROADCAST_ADDRESS:
                return True

            start = time.monotonic()
            while time.monotonic() - start < self.retry_timeout + (self.retry_timeout):
                if self._last_payload:
                    if (
                        self._last_payload.header_to == self._this_address
                        and self._last_payload.header_flags & FLAGS_ACK
                        and self._last_payload.header_id == self._last_header_id
                    ):

                        # We got an ACK
                        return True
        return False
    '''

    '''
    def send_ack(self, header_to, header_id):
        self.send(b"!", header_to, header_id, FLAGS_ACK)
        self.wait_packet_sent()
    '''

    def _spi_write(self, register, payload):
        if type(payload) == int:
            payload = [payload]
        elif type(payload) == bytes:
            payload = [p for p in payload]
        elif type(payload) == str:
            payload = [ord(s) for s in payload]

        with self._device as device:
            device.write(bytearray([register | 0x80] + payload))

    def _spi_read(self, register, length=1):
        buf = bytearray(length)

        with self._device as device:
            buf[0] = register & 0x7F
            device.write(buf, end=1)
            device.readinto(buf, end=length)

        if length == 1:
            return buf[0]
        else:
            return buf

    
    def receive(self, timeout=5.0):
        self.set_mode_rx()
        start = time.monotonic()
        message = None
        packet = None
        header_to = None
        header_from = None
        header_id = None
        header_flags = None

        while time.monotonic() - start < timeout:
            
            irq_flags = self._spi_read(REG_12_IRQ_FLAGS)

            if (irq_flags & RX_DONE) >> 6:
                packet_len = self._spi_read(REG_13_RX_NB_BYTES)
                self._spi_write(
                    REG_0D_FIFO_ADDR_PTR, self._spi_read(REG_10_FIFO_RX_CURRENT_ADDR)
                )

                packet = self._spi_read(REG_00_FIFO, packet_len)

                snr = self._spi_read(REG_19_PKT_SNR_VALUE) / 4
                rssi = self._spi_read(REG_1A_PKT_RSSI_VALUE)

                if snr < 0:
                    rssi = snr + rssi
                else:
                    rssi = rssi * 16 / 15

                if self._freq >= 779:
                    rssi = round(rssi - 157, 2)
                else:
                    rssi = round(rssi - 164, 2)

                self.last_rssi = rssi
                self.last_snr = snr

                if packet_len >= 4:
                    print()
                    print("packet ->", packet)
                    print("type(packet) ->", type(packet))

                    header_to = packet[0:4]
                    header_from = packet[4:8]
                    header_id = packet[8:12]
                    header_flags = packet[12:16]
                    message = bytes(packet[16:]) if packet_len > 16 else b""

                    self.last_msg = message
                break
        
        self._spi_write(REG_12_IRQ_FLAGS, 0xFF)

        if message is not None:
            print()
            print("message ->", message)
            print("type(message) ->", type(message))
        if packet is not None:
            print()
            print("packet ->", packet)
            print("type(packet) ->", type(packet))
        if packet is not None and packet_len > 16 and \
                (type(packet) == bytearray or type(packet) == list) and \
                (list(header_to) == self._this_address or
                 list(header_to) == self.broadcastAddress or
                 self._receive_all):
            msgTxt = self.decryptMessage(message)
            return {
                "to": ac_address.addressLst2Str(list(header_to)),
                "from": ac_address.addressLst2Str(list(header_from)),
                "id": ac_address.addressLst2Str(list(header_id)),
                "status": "N",
                "rssi": self.last_rssi,
                "snr": self.last_snr,
                "timestamp": str(time.monotonic()),
                "data": message,
                "flag0": header_flags[0],
                "flag1": header_flags[1],
                "flag2": header_flags[2],
                "hops": header_flags[3],
                "packet": packet,
                "messageText": msgTxt,
            }
            '''
            return {
                "packet": packet,
                "to": header_to,
                "from": header_from,
                "id": header_id,
                "flags": header_flags,
                "data": message,
            }
            '''
        elif header_to is not None:
            self.log.logMessage("receive",
                                "Received message not addressed to this unit")
            self.log.logMessage("receive",
                                "Addressed to:" +
                                ac_address.addressLst2Str(list(header_to)))
        return None


'''
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

    assert (
        getMessageId() is not None
    ), "ERROR: Test Failed - getMessageId() returned None"

    assert (
        getMessageId(12)[-3:] == "-12"
    ), "ERROR: Test Failed - getMessageId(12) returned None"


_unitTests()
'''
