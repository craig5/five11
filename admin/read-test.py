#!/usr/bin/env python2.7
# vim: set expandtab tabstop=4 shiftwidth=4 autoindent smartindent:
import argparse
import os
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LIB_DIR = os.path.join(_BASE_DIR, 'src', 'lib')
import site
site.addsitedir(_LIB_DIR)
#
import five11
import five11.data

def setup_cli():
    cli = argparse.ArgumentParser()
    cli.add_argument('--debug', action='store_true',help='Enable debugging.')
    return cli

def main():
    name = 'read-test'
    logger = five11.create_logger(name=name)
    cli = setup_cli()
    args = cli.parse_args()
    dm = five11.data.DataManager(args=args, logger=logger)
    dm.read_data()
    print dm.trains_data


if __name__ == '__main__':
    main()

# End of file.
