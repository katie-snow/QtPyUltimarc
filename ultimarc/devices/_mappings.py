#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
#
# Mappings for devices.
#
import logging

from ultimarc import translate_gettext as _

_logger = logging.getLogger('ultimarc')
#
# PAC 2015 or newer debounce values
#
IPACSeriesDebounce = {
    'standard': 0,
    'none': 0x01,
    'short': 0x02,
    'long': 0x03
}


def get_ipac_series_debounce_key(val):
    for key, value in IPACSeriesDebounce.items():
        if val == value:
            return key
    _logger.info(_(f'"{val}" debounce value is not a valid value'))
    return 'standard'


#
# IPAC 2015 or newer key mapping.
#
IPACSeriesMapping = {
    "A": 0x04,
    "B": 0x05,
    "C": 0x06,
    "D": 0x07,
    "E": 0x08,
    "F": 0x09,
    "G": 0x0A,
    "H": 0x0B,
    "I": 0x0C,
    "J": 0x0D,
    "K": 0x0E,
    "L": 0x0F,
    "M": 0x10,
    "N": 0x11,
    "O": 0x12,
    "P": 0x13,
    "Q": 0x14,
    "R": 0x15,
    "S": 0x16,
    "T": 0x17,
    "U": 0x18,
    "V": 0x19,
    "W": 0x1A,
    "X": 0x1B,
    "Y": 0x1C,
    "Z": 0x1D,
    "1": 0x1E,
    "2": 0x1F,
    "3": 0x20,
    "4": 0x21,
    "5": 0x22,
    "6": 0x23,
    "7": 0x24,
    "8": 0x25,
    "9": 0x26,
    "0": 0x27,
    "ENTER": 0x28,
    "ESC": 0x29,
    "BKSP": 0x2A,
    "TAB": 0x2B,
    "SPACE": 0x2C,
    "-": 0x2D,
    "=": 0x2E,
    "[": 0x2F,
    "]": 0x30,
    "non US #": 0x32,
    "'": 0x34,
    "`": 0x35,
    ",": 0x36,
    ".": 0x37,
    "/": 0x38,
    "CAPS": 0x39,
    "F1": 0x3A,
    "F2": 0x3B,
    "F3": 0x3C,
    "F4": 0x3D,
    "F5": 0x3E,
    "F6": 0x3F,
    "F7": 0x40,
    "F8": 0x41,
    "F9": 0x42,
    "F10": 0x43,
    "F11": 0x44,
    "F12": 0x45,
    "PRNT SCRN": 0x46,
    "SCROLL": 0x47,
    "PAUSE": 0x48,
    "INSERT": 0x49,
    "HOME": 0x4A,
    "PGUP": 0x4B,
    "DEL": 0x4C,
    "END": 0x4D,
    "PGDWN": 0x4E,
    "RIGHT": 0x4F,
    "LEFT": 0x50,
    "DOWN": 0x51,
    "UP": 0x52,
    "NUM": 0x53,
    "KP /": 0x54,
    "KP *": 0x55,
    "KP -": 0x56,
    "KP +": 0x57,
    "KP ENTER": 0x58,
    "KP 1": 0x59,
    "KP 2": 0x5A,
    "KP 3": 0x5B,
    "KP 4": 0x5C,
    "KP 5": 0x5D,
    "KP 6": 0x5E,
    "KP 7": 0x5F,
    "KP 8": 0x60,
    "KP 9": 0x61,
    "KP 0": 0x62,
    "KP .": 0x63,
    "\\": 0x64,
    "NON US \\": 0x64,
    "APP": 0x65,
    "KB POWER": 0x66,
    "KP =": 0x67,
    "CTRL L": 0x70,
    "SHIFT L": 0x71,
    "ALT L": 0x72,
    "WIN L": 0x73,
    "CTRL R": 0x74,
    "SHIFT R": 0x75,
    "ALT R": 0x76,
    "WIN MENU": 0x77,
    "MOUSE L DBL CLK": 0x80,
    "MOUSE L": 0x81,
    "MOUSE M": 0x82,
    "MOUSE R": 0x83,
    "POWER": 0x88,
    "SLEEP": 0x89,
    "WAKE": 0x8A,
    "VOL UP": 0x8B,
    "VOL DOWN": 0x8C,
    "GAMEPAD 1": 0x90,
    "GAMEPAD 2": 0x91,
    "GAMEPAD 3": 0x92,
    "GAMEPAD 4": 0x93,
    "GAMEPAD 5": 0x94,
    "GAMEPAD 6": 0x95,
    "GAMEPAD 7": 0x96,
    "GAMEPAD 8": 0x97,
    "GAMEPAD 9": 0x98,
    "GAMEPAD 10": 0x99,
    "GAMEPAD 11": 0x9A,
    "GAMEPAD 12": 0x9B,
    "GAMEPAD 13": 0x9C,
    "GAMEPAD 14": 0x9D,
    "GAMEPAD 15": 0x9E,
    "GAMEPAD 16": 0x9F,
    "GAMEPAD 17": 0xA0,
    "GAMEPAD 18": 0xA1,
    "GAMEPAD 19": 0xA2,
    "GAMEPAD 20": 0xA3,
    "GAMEPAD 21": 0xA4,
    "GAMEPAD 22": 0xA5,
    "GAMEPAD 23": 0xA6,
    "GAMEPAD 24": 0xA7,
    "GAMEPAD 25": 0xA8,
    "GAMEPAD 26": 0xA9,
    "GAMEPAD 27": 0xAA,
    "GAMEPAD 28": 0xAB,
    "GAMEPAD 29": 0xAC,
    "GAMEPAD 30": 0xAD,
    "GAMEPAD 31": 0xAE,
    "GAMEPAD 32": 0xAF,
    "ANALOG 0": 0xB0,
    "ANALOG 1": 0xB1,
    "ANALOG 2": 0xB2,
    "ANALOG 3": 0xB3,
    "ANALOG 4": 0xB4,
    "ANALOG 5": 0xB5,
    "ANALOG 6": 0xB6,
    "ANALOG 7": 0xB7,
    "HAT 0": 0xBA,
    "HAT 1": 0xBB,
    "HAT 2": 0xDC,
    "HAT 3": 0xBD,
    "TRACKBALL X1": 0xC0,
    "TRACKBALL X2": 0xC1,
    "TRACKBALL Y1": 0xC2,
    "TRACKBALL Y2": 0xC3,
    "TRACKBALL Z1": 0xC4,
    "TRACKBALL Z2": 0xC5,
    "MUTE": 0xe2,
    "PLAY/PAUSE": 0xe3,
    "NEXT": 0xe4,
    "PREV": 0xe5,
    "STOP": 0xe6,
    "EMAIL": 0xf0,
    "SEARCH": 0xf1,
    "BOOKMARKS": 0xf2,
    "OPEN BROWSER": 0xf3,
    "WEB BACK": 0xf4,
    "WEB FORWARD": 0xf5,
    "WEB STOP": 0xf6,
    "WEB REFRESH": 0xf7,
    "MEDIA PLAYER": 0xf8,
    "CALCULATOR": 0xfa,
    "EXPLORER": 0xfc,
    "WAIT 3 SEC": 0xfe,
}


def get_ipac_series_mapping_key(val):
    for key, value in IPACSeriesMapping.items():
        if val == value:
            return key
    return None


def get_ipac_series_macro_mapping_index(val):
    # Check if it is a Macro entry
    # Will return None on Macro entries
    r = range(0xe0, 0xef)
    return r.index(val) if val in r else None


#
# Pre 2015 IPAC key mapping
#
LegacyIPACMapping = {
    "A": 0x1C,
    "B": 0x32,
    "C": 0x21,
    "D": 0x23,
    "E": 0x24,
    "F": 0x2B,
    "G": 0x34,
    "H": 0x33,
    "I": 0x43,
    "J": 0x3B,
    "K": 0x42,
    "L": 0x4B,
    "M": 0x3A,
    "N": 0x31,
    "O": 0x44,
    "P": 0x4D,
    "Q": 0x15,
    "R": 0x2D,
    "S": 0x1B,
    "T": 0x2C,
    "U": 0x3C,
    "V": 0x2A,
    "W": 0x1D,
    "X": 0x22,
    "Y": 0x35,
    "Z": 0x1A,
    "1": 0x16,
    "2": 0x1E,
    "3": 0x26,
    "4": 0x25,
    "5": 0x2E,
    "6": 0x36,
    "7": 0x3D,
    "8": 0x3E,
    "9": 0x46,
    "0": 0x45,
    "ESC": 0x76,
    "-": 0x4E,
    "=": 0x55,
    "BKSP": 0x66,
    "TAB": 0x0D,
    "[": 0x54,
    "]": 0x5B,
    "ENTER": 0x5A,
    "KP ENTER": 0x5A,
    "CTRL L": 0x14,
    "CTRL R": 0x14,
    ";": 0x4C,
    "'": 0x52,
    "`": 0x0E,
    "SHIFT L": 0x12,
    "\\": 0x5D,
    ",": 0x41,
    ".": 0x49,
    "/": 0x4A,
    "SHIFT R": 0x59,
    "PRNT SCRN": 0x7C,
    "ALT L": 0x11,
    "ALT R": 0x11,
    "SPACE": 0x29,
    "CAPS": 0x58,
    "F1": 0x05,
    "F2": 0x06,
    "F3": 0x04,
    "F4": 0x0C,
    "F5": 0x03,
    "F6": 0x0B,
    "F7": 0x83,
    "F8": 0x0A,
    "F9": 0x01,
    "F10": 0x09,
    "F11": 0x78,
    "F12": 0x07,
    "NUM": 0x77,
    "SCROLL": 0x7E,
    "KP 1": 0x69,
    "KP 2": 0x72,
    "KP 3": 0x7A,
    "KP 4": 0x6B,
    "KP 5": 0x73,
    "KP 6": 0x74,
    "KP 7": 0x6C,
    "KP 8": 0x75,
    "KP 9": 0x7D,
    "KP 0": 0x70,
    "KP /": 0x4A,
    "KP *": 0x7C,
    "KP -": 0x7B,
    "KP +": 0x79,
    "KP .": 0x71,
    "SYSRQ": 0x84,
    "WIN MENU": 0x2F,
    "up": 0xF5,
    "down": 0xF2,
    "right": 0xF4,
    "left": 0xEB,
    "1right": 0x02,
    "3right": 0x02,
    "1up": 0x01,
    "3up": 0x01,
    "1down": 0x06,
    "3down": 0x06,
    "1left": 0x04,
    "3left": 0x04,
    "1sw1": 0x03,
    "3sw1": 0x03,
    "1sw2": 0x08,
    "3sw2": 0x08,
    "1sw3": 0x05,
    "3sw3": 0x05,
    "1sw4": 0x0A,
    "3sw4": 0x0A,
    "1sw5": 0x07,
    "3sw5": 0x07,
    "1sw6": 0x0C,
    "3sw6": 0x0C,
    "1sw7": 0x18,
    "3sw7": 0x18,
    "1sw8": 0x1A,
    "3sw8": 0x1A,
    "1start": 0x10,
    "3start": 0x10,
    "1coin": 0x14,
    "3coin": 0x14,
    "2right": 0x09,
    "4right": 0x09,
    "2up": 0x0D,
    "4up": 0x0D,
    "2down": 0x0E,
    "4down": 0x0E,
    "2left": 0x0B,
    "4left": 0x0B,
    "2sw1": 0x0F,
    "4sw1": 0x0F,
    "2sw2": 0x11,
    "4sw2": 0x11,
    "2sw3": 0x13,
    "4sw3": 0x13,
    "2sw4": 0x15,
    "4sw4": 0x15,
    "2sw5": 0x17,
    "4sw5": 0x17,
    "2sw6": 0x19,
    "4sw6": 0x19,
    "2sw7": 0x1B,
    "4sw7": 0x1B,
    "2sw8": 0x1C,
    "4sw8": 0x1C,
    "2start": 0x12,
    "4start": 0x12,
    "2coin": 0x16,
    "4coin": 0x16,
    "1a": 0x1D,
    "1b": 0x1E,
    "2a": 0x1F,
    "2b": 0x20,
    "m1": 0xe0,
    "m2": 0xe1,
    "m3": 0xe2,
    "m4": 0xe3,
}

KeyLookupTable = (
    # Pre2015 IPAC2
    (1, 6, 2, 4, 13, 14, 9, 11, -1, -1, -1, -1, -1, -1, -1, -1, 3, 8, 5, 10, 7, 12, 24, 26,
     15, 17, 19, 21, 23, 25, 27, 28, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
     -1, -1, -1, 16, 20, 29, 30, 18, 22, 31, 32, -1, -1, -1, -1, -1, -1, -1),
    # Pre2015 IPAC4
    (1, 6, 2, 4, 13, 14, 9, 11, 101, 106, 102, 104, 113, 114, 109, 111, 3, 8, 5, 10, 7, 12,
     24, 26, 15, 17, 19, 21, 23, 25, 27, 28, 103, 108, 105, 110, 107, 112, 124, 126, 115,
     117, 119, 121, 123, 125, 127, 128, 16, 20, -1, -1, 18, 22, -1, -1, 116, 120, 118, 122,
     -1, -1, -1),
    # 2015 IPAC2
    (20, 18, 24, 22, 21, 19, 1, 23, -1, -1, -1, -1, -1, -1, -1, -1, 40, 38, 36, 34, 32, 30,
     28, 26, 17, 39, 37, 35, 33, 29, 27, 25, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
     -1, -1, -1, -1, 48, 46, 44, 42, 47, 45, 43, 41, -1, -1, -1, -1, -1, -1, -1),
    # 2015 MinIPAC
    (11, 9, 15, 13, 38, 40, 34, 36, -1, -1, -1, -1, -1, -1, -1, -1, 10, 12, 14, 16, 42, 44,
     46, 48, 18, 20, 22, 24, 2, 4, 6, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
     -1, -1, -1, 26, 30, 7, 5, 28, 32, 3, 1, -1, -1, -1, -1, -1, -1, -1),
    # 2015 IPAC4
    (16, 14, 20, 18, 13, 11, 17, 15, 48, 38, 47, 40, 37, 35, 39, 45, 12, 10, 32, 30, 28, 53,
     64, 56, 9, 31, 29, 27, 60, 61, 49, 57, 36, 34, 8, 6, 4, 2, 50, 58, 33, 7, 5, 3, 1, 23,
     59, 51, 62, 54, -1, -1, 55, 63, -1, -1, 24, 22, 21, 19, -1, -1, -1),
    # 2015 JPAC
    (25, 29, 37, 33, 27, 31, 39, 35, -1, -1, -1, -1, -1, -1, -1, -1, 17, 21, 1, 5, 20, 18,
     40, 38, 19, 23, 3, 7, 32, 30, 34, 36, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
     -1, -1, -1, -1, 45, 41, -1, -1, 47, 43, -1, -1, -1, -1, -1, -1, 13, 15, 11),
    # Pre2015 MINIPAC
    (1, 6, 2, 4, 13, 14, 9, 11, -1, -1, -1, -1, -1, -1, -1, -1, 3, 8, 5, 10, 7, 12, 24, 26,
     15, 17, 19, 21, 23, 25, 27, 28, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
     -1, -1, -1, 16, 20, 29, 30, 18, 22, 31, 32, -1, -1, -1, -1, -1, -1, -1)
)

ShiftAdjTable = (32, 28, 50, 50, 64, 50, 32)
ShiftPosAdjTable = (-1, -1, 100, 100, 128, 100, -1)

# Only the pre2015 boards will use this lookup array
MacroLookupTable = (
    # Pre2015 IPAC2
    (63, 67, 71, 75),
    # Pre2015 IPAC4
    (59, 63, 67, 71),
    # 2015 IPAC2
    (-1, -1, -1, -1),
    # 2015 MinIPAC
    (-1, -1, -1, -1),
    # 2015 IPAC4
    (-1, -1, -1, -1),
    # 2015 JPAC
    (-1, -1, -1, -1),
    # Pre2015 MINIPAC
    (63, 67, 71, 75)
)

DecipherLookupKey = {
    "1up": 0,
    "1down": 1,
    "1right": 2,
    "1left": 3,
    "2up": 4,
    "2down": 5,
    "2right": 6,
    "2left": 7,
    "3up": 8,
    "3down": 9,
    "3right": 10,
    "3left": 11,
    "4up": 12,
    "4down": 13,
    "4right": 14,
    "4left": 15,
    "1sw1": 16,
    "1sw2": 17,
    "1sw3": 18,
    "1sw4": 19,
    "1sw5": 20,
    "1sw6": 21,
    "1sw7": 22,
    "1sw8": 23,
    "2sw1": 24,
    "2sw2": 25,
    "2sw3": 26,
    "2sw4": 27,
    "2sw5": 28,
    "2sw6": 29,
    "2sw7": 30,
    "2sw8": 31,
    "3sw1": 32,
    "3sw2": 33,
    "3sw3": 34,
    "3sw4": 35,
    "3sw5": 36,
    "3sw6": 37,
    "3sw7": 38,
    "3sw8": 39,
    "4sw1": 40,
    "4sw2": 41,
    "4sw3": 42,
    "4sw4": 43,
    "4sw5": 44,
    "4sw6": 45,
    "4sw7": 46,
    "4sw8": 47,
    "1start": 48,
    "1coin": 49,
    "1a": 50,
    "1b": 51,
    "2start": 52,
    "2coin": 53,
    "2a": 54,
    "2b": 55,
    "3start": 56,
    "3coin": 57,
    "4start": 58,
    "4coin": 59,
    "1test": 60,
    "2test": 61,
    "service": 62,
}

DecipherLookupMacroKey = {
    "m1": 0,
    "m2": 1,
    "m3": 2,
    "m4": 3,
}
