#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from ultimarc import translate_gettext as _
from ultimarc.tools import ToolContextManager

_logger = logging.getLogger('ultimarc')


if __name__ == '__main__':
    """ Main entry point """
    ToolContextManager.setup_logging('ultimarc')  # Configure logging
    parser = ToolContextManager.setup_logging('ultimarc')  # Setup default argparser arguments.
    args = parser.parse_args()
