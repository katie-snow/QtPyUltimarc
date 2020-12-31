#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Mock up various LibUSB objects for testing with.
#

# Descriptor values for a USB button.
DESC_USB_BUTTON = {
  'bDescriptorType': 1,
  'bDeviceClass': 0,
  'bDeviceProtocol': 0,
  'bDeviceSubClass': 0,
  'bLength': 18,
  'bMaxPacketSize0': 8,
  'bNumConfigurations': 1,
  'bcdDevice': 1,
  'bcdUSB': 512,
  'iManufacturer': 0x0002,
  'iProduct': 0x0002,
  'iSerialNumber': 0x0001,
  'idProduct': 0x1200,
  'idVendor': 0xd209
}
