#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
# Enable i18n internationalization support for python
#
import gettext
translate = gettext.translation('ultimarc', './locale', fallback=True)
translate_gettext = translate.gettext
