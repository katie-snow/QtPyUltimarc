#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Enable i18n internationalization support for python
#
import gettext
import os

base_path = os.path.dirname(os.path.abspath(__name__))

translate = gettext.translation(base_path, './locale', fallback=True)
translate_gettext = translate.gettext
