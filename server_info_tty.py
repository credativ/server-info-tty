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

from network_interface import Interface


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
# functions to print appliance name and contact information etc.


def print_appliance_name(box_x, box_y):
    """prints appliance name"""
    1

#############################################################################
# some handy network information gathering functions
# and network info block display func


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

    print(T.move(box_y, box_x) +
          T.white + "Host name .......... : " + T.normal + get_hostname())

    count = Interface.get_interface_count()
    print(T.move(box_y + 1, box_x) + T.white + "Network Interfaces . :" + T.normal)
    print(T.move(box_y + 1, box_x + 23) + str(count) + T.white)

    if ((CONFIG['DEFAULT'].get('allow_more', "yes") == "yes") and
        (count > 1)):
        print(T.move(box_y + 2) +
              "Press " + T.yellow + "n" + T.white +
              " for more network interfaces.")

    # if we have at least one interface beyond loopback, show some
    # information on this. If not, show a short warning.
    if count > 0:
        # active interfaces aka if with an ip address (v4 or v6)
        interfaces = Interface.get_active_interfaces()
        if not interfaces:
            interfaces = Interface.get_interfaces()

        y = box_y + 4
        print(T.move(y, box_x) + "First Interface .... :")
        print(T.move(y, box_x + 23) + T.normal + interfaces[0].name)
        y += 1
        print(T.move(y, box_x) + T.white + "Hardware Address ... :")
        print(T.move(y, box_x + 23) + T.normal + interfaces[0].hwaddress)
        y += 1
        print(T.move(y, box_x) + T.white + "Interface type ..... :")
        print(T.move(y, box_x + 23) + T.normal + interfaces[0].type)
        y += 1

        if CONFIG['network'].get('ipv4', "yes") == "yes":
            print(T.move(y, box_x) + T.white + "IPv4 Address(es) ... :")
            for i in interfaces[0].ipv4:
                print(T.move(y, box_x + 23) + T.normal + i)
                y += 1

        if CONFIG['network'].get('ipv6', "yes") == "yes":
            print(T.move(y, box_x) + T.white + "IPv6 Address(es) ... :")
            for i in interfaces[0].ipv6:
                print(T.move(y, box_x + 23) + T.normal + i)
                y += 1

    else:
        print(T.move(box_y + 3, box_x) +
              T.normal + T.red + "No network interfaces found." + T.white)

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

if LOGO_FILE is not None:
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
        print_appliance_name(0,0)

        # print network data box, half width
        print_network_info(0, 16, T.width / 2, T.height-LOGO_LINECOUNT-1)

        # print contact info box, half width

        # logo should fill approx. the lower 1/3 of screen full width
        if LOGO_FILE is not None:
            # print out logo if defined
            print_logo(LOGO_TEXT, 0, T.height-LOGO_LINECOUNT)

        # finally: delay reload to configured seconds
        sleep(RELOAD_EVERY)
