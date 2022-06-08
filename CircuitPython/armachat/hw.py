'''
MODELS
    - max:
    - compact:
    - watch:
'''

import time
import board
import busio
import displayio
import analogio
import digitalio
import gc
import os
import microcontroller
from armachat import config
from adafruit_st7789 import ST7789
from adafruit_st7735r import ST7735R
from pwmio import PWMOut
from adafruit_bitmap_font import bitmap_font

# LCD Global Settings
tft_dc = None
tft_cs = None
tft_clk = None   # SCL pin
tft_mosi = None  # SDA pin
tft_rst = None
tft_backlight = None
tft_spi = None

maxLines = 0
maxChars = 0
font = None

displayio.release_displays()

# Speaker/Buzzer
audio_gpio = None

# LoRa
lora_cs = None
lora_reset = None
lora_clk = None
lora_mosi = None
lora_miso = None
lora_spi = None

# Keyboard Global Settings
cols = None
rows = None
keys1 = None
keys2 = None
keys3 = None
keyboard_bl = None
keypad_cols = None
keypad_rows = None

if config.model == "max" or config.model == "compact":
    # Setup Display
    tft_dc = board.GP16
    tft_cs = board.GP21
    tft_clk = board.GP18  # SCL pin
    tft_mosi = board.GP19  # SDA pin
    # tft_rst = None
    tft_backlight = board.GP20

    tft_spi = busio.SPI(tft_clk, MOSI=tft_mosi)
    display_bus = displayio.FourWire(
        tft_spi, command=tft_dc, chip_select=tft_cs
    )
    display = ST7789(
        display_bus, width=320, height=240, rotation=270,
        backlight_pin=tft_backlight
    )

    maxLines = 10
    maxChars = 26
    font_file = "fonts/neep-24.pcf"
    font = bitmap_font.load_font(font_file)

    # Setup Speaker/Buzzer
    audio_gpio = board.GP0

    # Setup LoRa
    lora_cs = digitalio.DigitalInOut(board.GP13)
    lora_reset = digitalio.DigitalInOut(board.GP17)
    lora_clk = board.GP10
    lora_mosi = board.GP11
    lora_miso = board.GP12
    lora_spi = busio.SPI(lora_clk, MOSI=lora_mosi, MISO=lora_miso)

    # Setup Keyboard
    if config.model == "max":
        keypad_cols = [
            digitalio.DigitalInOut(x)
            for x in (board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP14)
        ]
        keypad_rows = [
            digitalio.DigitalInOut(x)
            for x in (
                board.GP6, board.GP9, board.GP15, board.GP8, board.GP7, board.GP22
            )
        ]
        keys1 = (
            (" ", ".", "m", "n", "b", "dn"),
            ("ent", "l", "k", "j", "h", "lt"),
            ("p", "o", "i", "u", "y", "up"),
            ("bsp", "z", "x", "c", "v", "rt"),
            ("a", "s", "d", "f", "g", "tab"),
            ("q", "w", "e", "r", "t", "alt"),
        )
        keys2 = (
            ("_", ",", ">", "<", '""', "{"),
            ("~", "-", "*", "&", "+", "["),
            ("0", "9", "8", "7", "6", "}"),
            ("=", "(", ")", "?", "/", "]"),
            ("!", "@", "#", "$", "%", "\\"),
            ("1", "2", "3", "4", "5", "alt"),
        )
        keys3 = (
            (":", ";", "M", "N", "B", "dn"),
            ("ent", "L", "K", "J", "H", "lt"),
            ("P", "O", "I", "U", "Y", "up"),
            ("bsp", "Z", "X", "C", "V", "rt"),
            ("A", "S", "D", "F", "G", "tab"),
            ("Q", "W", "E", "R", "T", "alt"),
        )
    elif config.model == "compact":
        keyboard_bl = digitalio.DigitalInOut(board.GP14)
        keyboard_bl.direction = digitalio.Direction.OUTPUT

        keypad_cols = [
            digitalio.DigitalInOut(x)
            for x in (board.GP1, board.GP2, board.GP3, board.GP4, board.GP5)
        ]
        keypad_rows = [
            digitalio.DigitalInOut(x)
            for x in (
                board.GP6, board.GP9, board.GP15, board.GP8, board.GP7, board.GP22
            )
        ]
        keys1 = (
            ('ent', ' ', 'm', 'n', 'b'),
            ('bsp', 'l', 'k', 'j', 'h'),
            ('p', 'o', 'i', 'u', 'y'),
            ('alt', 'z', 'x', 'c', 'v'),
            ('a', 's', 'd', 'f', 'g'),
            ('q', 'w', 'e', 'r', 't')
        )
        keys2 = (
            ('dn', '.', ':', ';', '"'),
            ('up', '-', '*', '&', '+'),
            ('0', '9', '8', '7', '6'),
            ('alt', '(', ')', '?', '/'),
            ('!', '@', '#', '$', '%'),
            ('1', '2', '3', '4', '5')
        )
        keys3 = (
            ('rt', ',', 'M', 'N', 'B'),
            ('lt', 'L', 'K', 'J', 'H'),
            ('P', 'O', 'I', 'U', 'Y'),
            ('alt', 'Z', 'X', 'C', 'V'),
            ('A', 'S', 'D', 'F', 'G'),
            ('Q', 'W', 'E', 'R', 'T')
        )
elif config.model == "watch":
    # Setup Display
    tft_dc = board.GP8
    tft_cs = board.GP9
    tft_clk = board.GP10  # SCL pin
    tft_mosi = board.GP11  # SDA pin
    tft_rst = board.GP12
    tft_backlight = board.GP25

    tft_spi = busio.SPI(tft_clk, MOSI=tft_mosi)
    display_bus = displayio.FourWire(
        tft_spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst
    )
    display = ST7735R(
        display_bus, width=160, height=80, rotation=90,
        backlight_pin=tft_backlight, rowstart=1, colstart=26, invert=True
    )

    maxLines = 5
    maxChars = 20
    font_file = "fonts/pavlova-16.pcf"
    font = bitmap_font.load_font(font_file)

    # Setup Speaker/Buzzer
    audio_gpio = board.GP4

    # Setup LoRa
    lora_cs = digitalio.DigitalInOut(board.GP1)
    # lora_reset = digitalio.DigitalInOut(board.GP17)
    lora_clk = board.GP2
    lora_mosi = board.GP3
    lora_miso = board.GP0
    lora_spi = busio.SPI(lora_clk, MOSI=lora_mosi, MISO=lora_miso)

    # Setup Keyboard
    keypad_cols = [
        digitalio.DigitalInOut(x)
        for x in (board.GP28, board.GP27, board.GP26, board.GP22, board.GP21)
    ]
    keypad_rows = [
        digitalio.DigitalInOut(x)
        for x in (
                board.GP20, board.GP19, board.GP18, board.GP17, board.GP16, board.GP15
            )
    ]
    keys1 = (
        ("ent", " ", "m", "n", "b"),
        ("bsp", "l", "k", "j", "h"),
        ("p", "o", "i", "u", "y"),
        ("alt", "z", "x", "c", "v"),
        ("a", "s", "d", "f", "g"),
        ("q", "w", "e", "r", "t"),
    )
    keys2 = (
        ("rt", ",", ">", "<", '""'),
        ("lt", "-", "*", "&", "+"),
        ("0", "9", "8", "7", "6"),
        ("alt", "(", ")", "?", "/"),
        ("!", "@", "#", "$", "%"),
        ("1", "2", "3", "4", "5"),
    )
    keys3 = (
        ("dn", ";", "M", "N", "B"),
        ("up", "L", "K", "J", "H"),
        ("P", "O", "I", "U", "Y"),
        ("alt", "Z", "X", "C", "V"),
        ("A", "S", "D", "F", "G"),
        ("Q", "W", "E", "R", "T"),
    )
else:
    print("Error\tac_models.py\t\tModel, " + config.model + ", not supported")

# keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys1)

# Setup LED
# LED = digitalio.DigitalInOut(board.LED)
# LED.direction = digitalio.Direction.OUTPUT

# Allow us to read the input voltage
VSYS_voltage = analogio.AnalogIn(board.VOLTAGE_MONITOR)
VBUS_status = digitalio.DigitalInOut(board.VBUS_SENSE)  # defaults to input
VBUS_status.pull = digitalio.Pull.UP  # turn on internal pull-up resistor

SMPSmode = digitalio.DigitalInOut(board.SMPS_MODE)
SMPSmode.direction = digitalio.Direction.OUTPUT
SMPSmode.value = True

def get_CpuTempC():
    return microcontroller.cpu.temperature

def get_DiskSpaceKb():
    fs_stat = os.statvfs("/")
    return (fs_stat[0] * fs_stat[2] / 1024)

def get_FreeSpaceKb():
    fs_stat = os.statvfs("/")
    return (fs_stat[0] * fs_stat[3] / 1024)

def get_FreeRam():
    return gc.mem_free()

def get_VSYSvoltage():
    VSYSin = ((VSYS_voltage.value * 3.3) / 65536) * 3
    return VSYSin
