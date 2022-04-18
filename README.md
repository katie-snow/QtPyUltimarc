Ultimarc Configurator
=
A cross-platform tool for configuring Ultimarc USB devices.


Development Environment Setup
-


Fedora
-
1. Install required packages

::

    $ sudo dnf install qt5-devel qt5-qtquick* qt5*examples qt-creator libusb-devel libudev-devel hidapi-devel libglvnd-opengl

2. Clone repository

::

    $ git clone git@github.com:katie-snow/QtPyUltimarc.git

3. Setup Python virtual environment

::

    $ cd QtPyUltimarc
    $ python3 -m venv venv
    $ source ./venv/bin/activate
    $ pip install --upgrade pip setuptools
    $ pip install pip-tools
    $ pip-sync


4. Configure Python path environment variable

::

    $ export PYTHONPATH=`pwd`

5. Test CLI tools

::

    $ cd ultimarc
    $ python -m tools --help


6. Update i18n translations POT file.

::

    $ cd QtPyUltimarc
    $ python setup.py extract_messages


## Troubleshooting

**libusb error -3: Access denied.**

*Add "ultimarc/udev/95-ultimarc.rules" to /etc/udev/rules.d/ directory and reload udev rules.*
