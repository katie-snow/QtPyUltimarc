#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import sys

from ultimarc import translate_gettext as _
from ultimarc.tools import ToolContextManager

_logger = logging.getLogger('ultimarc')


if __name__ == '__main__':
    """ Main entry point """
    ToolContextManager.initialize_logging('ultimarc')  # Configure logging
    # Setup default argparser arguments.
    parser = ToolContextManager.get_argparser('ultimarc', _('Ultimarc device configurator.'))

    parser.add_argument('-l', '--list', help=_('display attached ultimarc devices.'), default=False,
                        action='store_true')
    args = parser.parse_args()

    if args.list is True:
        from ultimarc.tools.list_devices import ListDevicesClass
        ListDevicesClass(sys.argv, None).run()
        exit(0)

    exit(0)
