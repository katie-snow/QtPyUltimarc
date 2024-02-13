|badge1| |badge2| |badge3| |badge4|

.. |badge1| image:: https://github.com/katie-snow/QtPyUltimarc/actions/workflows/tests.yaml/badge.svg
  :alt: Unittest Completion Status
.. |badge2| image:: https://raw.githubusercontent.com/katie-snow/QtPyUltimarc/coverage-badge/coverage.svg?raw=true
  :alt: Code Coverage Status
.. |badge3| image:: https://img.shields.io/badge/python-v3.8%20|%20v3.9%20|%20v3.10%20|%20v3.11%20|%20v3.12-blue
  :alt: Python v3.8, v3.9, v3.10, v3.11, v3.12
.. |badge4| image:: https://img.shields.io/badge/OS%20Support-Linux%20|%20Mac%20OS%20|%20MS%20Windows-blue
  :alt: OS Support Linux, Mac OS, MS Windows


****************************************************************************************
Python Ultimarc Tools: Python tools for managing Ultimarc devices
****************************************************************************************

The **Python Ultimarc** tools are a pure python implementation and cross platform set of command line tools, graphical
tool and python library for managing Ultimarc USB arcade devices. Both the CLI and UI tools run on Linux, Mac OS and MS Windows.

For more information about Ultimarc devices visit https://www.ultimarc.com.

Supported Ultimarc Devices
==========================

.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Ultimarc Device
     - CLI Support
     - UI Support
   * - J-PAC
     - Yes
     - Yes
   * - I-PAC2
     - Yes
     - Yes
   * - I-PAC4
     - Yes
     - Yes
   * - MINI-PAC
     - Yes
     - Yes
   * - USB Button
     - Yes
     - No
   * - UltraStik 360 Joystick
     - Yes
     - No
   * - AimTrak Light Gun
     - No
     - No

Get It Now
==========

To install only the command line tools, run:
::

    $ pip install ultimarc

To install both the command line and graphical tools, run:
::

    $ pip install ultimarc[ui]


Graphical Tool
==============

To launch the graphical configration tool, run:
::

    $ ultimarc-ui

The graphical tool supports managing plugged in devices, along with creating and editing configuration files for
unplugged devices.


Command Line Tools
==================

The command line tools are a set of tools to inspect and manage different Ultimarc devices. The tools are launched by
executing '**ultimarc**' in a terminal command window. To view the available tool commands, run the tool with the
'--help' argument:
::

    $ ultimarc --help

    usage: python -m tools [command] [-h|--help] [args]

    available commands:
      ipac2          : Manage ipac2 devices
      ipac4          : Manage ipac4 devices
      jpac           : Manage jpac devices
      list           : list all attached ultimarc devices
      mini-pac       : Manage Mini-pac devices
      usb-button     : manage usb-button devices.

To view the help for a specific tool, add the tool name and use the '--help' argument:
::

    $ ultimarc list --help

    usage: list [-h] [--debug] [--log-file] [-q] [--bus BUS] [--address ADDRESS] [-c CLASS_ID] [-d]

    list all attached ultimarc devices

    optional arguments:
      -h, --help            show this help message and exit
      --debug               enable debug output
      --log-file            write output to a log file
      -q, --quiet           suppress normal output
      --bus BUS             filter by usb device bus number
      --address ADDRESS     filter by usb device address number
      -c CLASS_ID, --class-id CLASS_ID
                            filter by device class id
      -d, --descriptors     Show device descriptor values.

    class ids: usb-button,aimtrak,mini-pac,ipac2,ipac4,jpac


Udev Support
==================

For Udev support for Ultimarc devices, copy the file 'ultimarc/udev/95-ultimarc.rules' to the /etc/udev/rules.d folder.


Project Links
=============

- PyPI: https://pypi.python.org/pypi/python-easy-json
- Issues: https://github.com/katie-snow/QtPyUltimarc/issues

License
=======

GPL-3.0 licensed. See the bundled `LICENSE <https://github.com/katie-snow/QtPyUltimarc/blob/main/LICENSE>` file for more details.
