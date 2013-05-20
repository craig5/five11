#!/usr/bin/env python2.7
# vim: set expandtab tabstop=4 shiftwidth=4 autoindent smartindent:

''' Start the server. '''

version = '0.1'

# python core
import os
import sys
# third party
# custom
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_LIB_DIR = os.path.join(_BASE_DIR, 'src', 'lib')
sys.path.append(_LIB_DIR)
import five11.webapp

_SERVER_PORT = 8888

def main():
    host = '0.0.0.0'
    port = _SERVER_PORT
    debug = True
    five11.webapp.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()
# End of file.
