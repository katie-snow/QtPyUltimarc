#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import ctypes as ct
import logging

_logger = logging.getLogger('ultimarc')


class UltimarcStruct(ct.Structure):
    """ Parent structure """
    level = 1

    def __repr__(self) -> str:
        values = ',\n'.join(('  ' * self.level) + f'{name}={value}'
                            for name, value in self._as_dict_().items())
        return f'<{self.__class__.__name__}:\n{values}>'

    def __len__(self) -> int:
        """
        :return: Return the number of bytes for the size this structure
        """
        return sum([ct.sizeof(i[1]) for i in self._fields_])

    def _as_dict_(self) -> dict:
        return {field[0]: (hex(getattr(self, field[0]))
                           if isinstance(getattr(self, field[0]), int)
                           else self._print_array_(getattr(self, field[0])) if isinstance(getattr(self,
                                                                                                  field[0]), ct.Array)
                           else getattr(self, field[0]))
                for field in self._fields_}

    def _print_array_(self, array):
        join = '\n' + '  ' * self.level
        values = join

        count = 1
        for index, value in enumerate(array):
            values = values + f' {index}={hex(value)},'
            if count % 4 == 0:
                values = values + join
                count = 1
            else:
                count += 1
        return values

    # def __repr__(self) -> str:
    #     values = ',\n'.join(('  ' * self.level) + f'{name}={value}'
    #                         for name, value in self._asdict_().items())
    #     return f'<{self.__class__.__name__}:\n{values}>'
    #
    # def _asdict_(self) -> dict:
    #     return {field[0]: (hex(getattr(self, field[0]))
    #                        if isinstance(getattr(self, field[0]), int)
    #                        else getattr(self, field[0]))
    #             for field in self._fields_}


class PacHeaderStruct(UltimarcStruct):
    """ Defines the header structure for messages """
    level = 2
    _fields_ = [
        ('type', ct.c_ubyte),  # Type of message this will be
        ('byte_2', ct.c_ubyte),  # 0xDD unless LED packet
        ('byte_3', ct.c_ubyte),  # Quadrature button time (U-HID) or 0F (PAC)
        ('byte_4', ct.c_ubyte)  # Configuration.  Number from PacConfigStruct class
    ]


class PacConfigStruct(UltimarcStruct):
    """ Defines the bit values for the configuration byte """
    _fields_ = [
        ('high_current_output', ct.c_uint, 1),
        ('accelerometer', ct.c_uint, 1),
        ('paclink', ct.c_uint, 1),
        ('debounce', ct.c_uint, 2),
        ('reserved', ct.c_uint, 3)
    ]


class PacConfigUnion(ct.Union):
    _fields_ = [
        ('config', PacConfigStruct),
        ('asByte', ct.c_uint)
    ]


class PacStruct(UltimarcStruct):
    """ Defines the structure used by most Ultimarc boards.  Total size is 256 """
    _fields_ = [
        ('header', PacHeaderStruct),  # 1 - 4  (4 bytes)
        ('bytes', ct.c_ubyte * 252),  # 5 - 256
    ]


class UltraStikStruct(UltimarcStruct):
    """ Defines the structure used by UltraStik boards. Total size is 96 """
    _fields_ = [
        ('keepAnalog', ct.c_uint8),  # keepAnalog[0] : false off(0x50), true on(0x11)
        ('restrictor', ct.c_uint8),  # restrictor[2] : false off(0x10), true on(0x09)
        ('borders', ct.c_uint8 * 8),  # borders[3-10] : array of 8 bytes
        ('map', ct.c_uint8 * 81),  # map[11-92] : array of 81 map values
        ('reserved', ct.c_uint8 * 3),  # reserved
        ('flash', ct.c_uint8)  # flash[95] : (Pre-2015) false RAM(0xFF), true FLASH(0x00), (=> 2015) 0x0
    ]
