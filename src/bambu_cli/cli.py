#!/usr/bin/env python

import argparse
from actions.login import login
from actions.info import get_version_info
from actions.print import print_file
from actions.add import add_printer
import logging

from actions.upload import upload_file

logging.basicConfig(level=logging.INFO, filename='bambu.log',
                    datefmt='%Y-%m-%d %H:%M:%S')


def main():
    parser = argparse.ArgumentParser(
        prog='bambu',
        description='Control Bambu Printers through the command line')
    subparsers = parser.add_subparsers(required=True)

    add_parser = subparsers.add_parser('add', help='Add a printer')
    add_parser.add_argument('ip', type=str, help='The printer IP address')
    add_parser.add_argument(
        'serial', type=str, help='The printer serial number')
    add_parser.add_argument('access_code', type=str,
                            help='The printer access code')
    add_parser.add_argument(
        '--name', type=str, help='A friendly name for the printer')
    add_parser.set_defaults(action=add_printer)

    print_parser = subparsers.add_parser('print', help='Print a file')
    print_parser.add_argument('printer', type=str, help='The printer to use')
    print_parser.add_argument('file', type=str, help='The file to print')
    print_parser.set_defaults(action=print_file)

    upload_parser = subparsers.add_parser('upload', help='Upload a file')
    upload_parser.add_argument(
        'printer', type=str, help='The printer to upload to')
    upload_parser.add_argument('file', type=str, help='The file to upload')
    upload_parser.set_defaults(action=upload_file)

    info_parser = subparsers.add_parser('info', help='Get printer info')
    info_parser.add_argument(
        'printer', type=str, help='The printer to get info for')
    info_parser.set_defaults(action=get_version_info)

    login_parser = subparsers.add_parser('login', help='Login to Bambu Cloud')
    # login_parser.add_argument('email', type=str, help='Bambu Cloud email')
    # login_parser.add_argument('password', type=str, help='Bambu Cloud password')
    login_parser.add_argument('refresh_token', type=str,
                              help='Bambu Cloud refresh token')
    login_parser.set_defaults(action=login)

    args = parser.parse_args()
    args.action(args)


if __name__ == '__main__':
    main()
