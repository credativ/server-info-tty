#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright: 2017, 2018 peter.dreuw@credativ.de
# License: MIT, see LICENSE.txt for details.
#

"""Small python tool to display some facts on a given server on a TTY."""

__author__ = 'Peter Dreuw'
__version__ = '0.1'


# This script needs the following packages to be installed
#  - python3-blessings
#  - python-fabulous

import socket
import configparser
from time import sleep
from blessings import Terminal


# import local libs

from NetworkInterface import Interface


#############################################################################
# global variables (constants)

INI_NAME = 'config-example.ini'  # '/etc/server-info-tty/config.ini'

RELOAD_EVERY = 60    # time in seconds to wait until reload (can be set in ini)

CONFIG = configparser.ConfigParser()

T = Terminal()

#############################################################################
# some handy logo handling functions


def read_logo(logo, replace_colors):
    """reads the ascii art logo file and inserts color codes
       returns plain text ascii art and line count in a tuple"""

    i = 0
    logo_data = ""
    with open(logo, 'r') as logo_file:
        for line in iter(logo_file.readline, ''):
            logo_data = logo_data + line
            i += 1

        logo_file.close()

    logo_data = (logo_data
                 .replace(replace_colors["red"], T.red)
                 .replace(replace_colors["black"], T.white))
    return (logo_data, i)


def print_logo(logo_text, cord_x, cord_y):
    """prints the ascii art logo at cord(x,y)"""

    print(T.move(cord_y, cord_x)+logo_text)

    return


#############################################################################
# some handy network information gathering functions
# and network info block display func

def get_mac_address():
    """returns the MAC address of first non-loopback network device"""
    return Interface.get_first_interface().hwaddress


def get_ipv4_address():
    """returns the first ipv4 address of first non-loopback network device"""
    return Interface.get_first_interface().ipv4


def get_ipv6_address():
    """returns the first ipv6 address of first non-loopback network device"""
    return Interface.get_first_interface().ipv6


def get_hostname():
    """returns hostname based on socket"""
    if socket.gethostname().find('.') >= 0:
        name = socket.gethostname()
    else:
        name = socket.gethostbyaddr(socket.gethostname())[0]
    return name


def print_network_info(box_x, box_y, box_w, box_h):
    """displays network information block at box(x,y)
       with max w width and h height"""

    print(T.move(box_y, box_x) + str(Interface.get_interface_count()))

    return


#############################################################################
# main code


# read the ini file
CONFIG.read(INI_NAME)

# check if there is a logo defined
if 'logo' in CONFIG:
    LOGO_FILE = CONFIG['logo'].get("logo")
    REPLACE_COLORS = {
        "red": CONFIG['logo'].get("red", "r"),
        "black": CONFIG['logo'].get("black", "b"),
    }
else:
    LOGO_FILE = None


# check if there is a sleep delay in ini file, defaults to 60 secs
if 'DEFAULT' in CONFIG:
    RELOAD_EVERY = int(CONFIG['DEFAULT'].get('reload', 60))


# prepare ascii art logo data
LOGO_TEXT = ""
LOGO_LINECOUNT = 0

if LOGO_FILE:
    (LOGO_TEXT, LOGO_LINECOUNT) = read_logo(LOGO_FILE, REPLACE_COLORS)


# display main info

with T.fullscreen():
    # loop forever
    while 1:
        # clear screen
        print(T.clear())

        # print appliance name and basic information on system defined
        # in CONFIG.
        # this should cover first 1/4 of screen, full width

        # print network data box, half width
        print_network_info(0, 16, T.width / 2, T.height-LOGO_LINECOUNT-1)

        # print contact info box, half width

        # logo should fill approx. the lower 1/3 of screen full width
        if LOGO_FILE:
            # print out logo if defined
            print_logo(LOGO_TEXT, 0, T.height-LOGO_LINECOUNT)

        # finally: delay reload to configured seconds
        sleep(RELOAD_EVERY)
