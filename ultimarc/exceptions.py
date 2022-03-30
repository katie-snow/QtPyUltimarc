#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

from ultimarc import translate_gettext as _


#
# USB device custom exception classes.
#
class USBDeviceNotFoundError(Exception):
    """ Device was not found when trying to open it. """
    def __init__(self, dev_key, message=_('Device was not found when trying to open it.')):
        self.dev_key = dev_key
        self.message = message
        super().__init__(f'{dev_key}: {message}')


class USBDeviceClaimInterfaceError(Exception):
    """ Failed to claim USB device interface. """
    def __init__(self, dev_key, message=_('Failed to claim USB device interface.')):
        self.dev_key = dev_key
        self.message = message
        super().__init__(f'{dev_key}: {message}')


class USBDeviceInterfaceNotClaimedError(Exception):
    """ Device interface has not been claimed before read or write operation. """

    def __init__(self, dev_key, message=_('Device interface has not been claimed before read or write operation.')):
        self.dev_key = dev_key
        self.message = message
        super().__init__(f'{dev_key}: {message}')
