# vim: set expandtab tabstop=4 shiftwidth=4 autoindent smartindent:
#
import os

_CONSTANTS_PATH     = os.path.abspath(__file__)
_LIB_DIR            = os.path.dirname(os.path.dirname(_CONSTANTS_PATH))
_BASE_DIR           = os.path.dirname(os.path.dirname(_LIB_DIR))
#
_TEMPLATE_DIR       = os.path.join(_BASE_DIR, 'src', 'templates')
_STATIC_DIR         = os.path.join(_BASE_DIR, 'src', 'static')
_DATA_DIR           = os.path.join(_BASE_DIR, 'data')
# End of file.
