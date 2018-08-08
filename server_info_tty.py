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
#  - ssh    (if you want the ssh host key finger print)

import socket
import configparser
import subprocess
import os
from time import sleep
from blessings import Terminal


# import local libs

from network_interface import Interface


#############################################################################
# global variables (constants)

INI_NAME = 'config.ini'  # better '/etc/server-info-tty/config.ini'?

RELOAD_EVERY = 60    # time in seconds to wait until reload (can be set in ini)

CONFIG = configparser.ConfigParser()

SSH_FP_COMMAND = "/usr/bin/ssh-keygen -l -f %s"

T = Terminal()

IF_NUMS = ['First Interface .... :',
           'Second Interface ... :',
           'Third Interface .... :',
           'Fourth Interface ... :']

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


def print_appliance_name(box_x, box_y, box_w, box_h):
    """prints appliance name"""
    if 'host' in CONFIG:
        app_name = CONFIG['host'].get('product_name', 'Linux host')
    else:
        app_name = 'Linux host'

    if len(app_name) > box_w:
        raise ValueError("width too small for configured product name")

    # only underline that one if there is room for it, otherwise use TTY
    # capabilities if possible
    if box_h > 1:
        print(T.move(box_y, box_x) + T.yellow_bold(app_name))
        print(T.move(box_y + 1, box_x) + T.yellow("=" * len(app_name)))
    else:
        print(T.move(box_y, box_x) + T.bold_underline_yellow(app_name))

    return

def print_contact_info_box(box_x, box_y, box_w, box_h, dept):
    """unified printer for provider and contact box"""

    if box_h < 5:
        raise ValueError("Box height too small: " + dept)

    if dept in CONFIG:
        c_name = CONFIG[dept].get("c_name", "")
        c_phone = CONFIG[dept].get("c_phone", "")
        c_website = CONFIG[dept].get("c_website", "")
        c_email = CONFIG[dept].get("c_email", "")
        c_headline = CONFIG[dept].get("c_headline", dept.title())
    else:
        c_name = c_phone = c_website = c_email = ""
        c_headline = dept.title()

    print(T.move(box_y, box_x) + T.bold_underline(c_headline))
    print(T.move(box_y + 1, box_x) + T.normal + c_name)
    print(T.move(box_y + 2, box_x) + T.normal + c_phone)
    print(T.move(box_y + 3, box_x) + T.normal + c_website)
    print(T.move(box_y + 4, box_x) + T.normal + c_email)


def print_contact(box_x, box_y, box_w, box_h):
    """print box with contact data provided by config file"""
    print_contact_info_box(box_x, box_y, box_w, box_h, "contact")


def print_provider(box_x, box_y, box_w, box_h):
    """print box with provider contact data found in config file"""
    print_contact_info_box(box_x, box_y, box_w, box_h, "provider")


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


def print_host_info(box_x, box_y, box_w, box_h):
    """print box information on the host"""

    # show headline only if at least one option is allowed
    if (
            ('host' not in CONFIG) or
            (CONFIG['host'].get('hostname', 'yes') == 'yes') or
            (CONFIG['host'].get('ssh_host_key_fp', 'yes') == 'yes')):

        print(T.move(box_y, box_x) + T.bold_underline("Host information:"))

    if (
            ('host' not in CONFIG) or
            (CONFIG['host'].get('hostname', 'yes') == 'yes')):
        print(T.move(box_y+1, box_x) +
              T.white("Host name .......... : ") + get_hostname())

    if (
            ('host' not in CONFIG) or
            (CONFIG['host'].get('ssh_host_key_fp', 'yes') == 'yes')):

        if 'host' in CONFIG:
            key_file = CONFIG['host'].get(
                "ssh_host_key_file", "/etc/ssh/ssh_host_rsa_key.pub")
        else:
            key_file = "/etc/ssh/ssh_host_rsa_key.pub"

        print(T.move(box_y+2, box_x) +
              T.white("SSH host key fingerprint:"))

        if not os.access(key_file, os.R_OK):
            # no access to key file, bail out with error
            print(T.move(box_y+3, box_x) +
                  "Public host key file not readable")
            return

        command = SSH_FP_COMMAND % key_file
        finger_print = str(
            subprocess.Popen(command.split(" "),
                             universal_newlines=True,
                             stdout=subprocess.PIPE).stdout.read()
        )

        print(T.move(box_y+3, box_x) + finger_print)
    return


def print_network_info(box_x, box_y, box_w, box_h):
    """displays network information block at box(x,y)
       with max w width and h height"""

    print(T.move(box_y, box_x) + T.bold_underline("Network information"))
    count = Interface.get_interface_count()
    print(T.move(box_y + 1, box_x) + T.white("Network Interfaces . :"))
    print(T.move(box_y + 1, box_x + 23) + str(count) + T.white)

    if (('DEFAULT' in CONFIG) or
        (('DEFAULT' in CONFIG) and
         (CONFIG['DEFAULT'].get('allow_more', "yes") == "yes") and
         (count > 1))):
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

        # determine, how many interface rows we should show on main page
        if ((count > 3) and (T.width // 4 > box_w+1)):
            if_to_show = 3
        elif ((count > 2) and (T.width // 3 > box_w+1)):
            if_to_show = 2
        elif ((count > 1) and (T.width // 2 > box_w+1)):
            if_to_show = 1
        else:
            if_to_show = 0

        # loop on the needed rows determined above
        if_count = 0
        while if_count <= if_to_show:
            # calculate the x offset for current row
            x_offset = if_count * 65 + box_x
            y = box_y + 4
            print(T.move(y, x_offset) + T.white(IF_NUMS[if_count]))
            print(T.move(y, x_offset + 23)
                  + T.normal
                  + interfaces[if_count].name)
            y += 1
            print(T.move(y, x_offset) + T.white("Hardware Address ... :"))
            print(T.move(y, x_offset + 23) + interfaces[if_count].hwaddress)
            y += 1
            print(T.move(y, x_offset) + T.white("Interface type ..... :"))
            print(T.move(y, x_offset + 23) + interfaces[if_count].type)
            y += 1

            if 'network' in CONFIG:
                if CONFIG['network'].get('ipv4', "yes") == "yes":
                    print(T.move(y, x_offset)
                          + T.white("IPv4 Address(es) ... :"))
                    for i in interfaces[if_count].ipv4:
                        print(T.move(y, x_offset + 23) + i)
                    y += 1

                if CONFIG['network'].get('ipv6', "yes") == "yes":
                    print(T.move(y, x_offset)
                          + T.white("IPv6 Address(es) ... :"))
                    for i in interfaces[if_count].ipv6:
                        print(T.move(y, x_offset + 23) + i)
                        y += 1
            if_count += 1

    else:
        print(T.move(box_y + 3, x_offset) +
              T.normal_red("No network interfaces found."))

    return


#############################################################################
# main code


# read the ini file
CONFIG.read(INI_NAME)

# check if there is a logo defined
if 'logo' in CONFIG:
    LOGO_FILE = CONFIG['logo'].get("logo", "./logo.txt")
    REPLACE_COLORS = {
        "red": CONFIG['logo'].get("red", "r"),
        "black": CONFIG['logo'].get("black", "b"),
    }
else:
    LOGO_FILE = "./logo.txt"
    REPLACE_COLORS = {
        "red": "r",
        "black": "b",
    }


# check if there is a sleep delay in ini file, defaults to 60 secs
if 'DEFAULT' in CONFIG:
    RELOAD_EVERY = int(CONFIG['DEFAULT'].get('reload', 60))


# prepare ascii art logo data
LOGO_TEXT = ""
LOGO_LINECOUNT = 0

if LOGO_FILE is not None:
    (LOGO_TEXT, LOGO_LINECOUNT) = read_logo(LOGO_FILE, REPLACE_COLORS)

# helpfull for debugging sizes
# print("height: " + str(T.height) + " width: " + str(T.width))
# exit()

# display main info

with T.fullscreen():
    # loop forever
    while 1:
        # clear screen
        print(T.clear())

        # print appliance name and basic information on system defined
        # in CONFIG.
        # this should cover first 1/4 of screen, full width
        print_appliance_name(1, 1, T.width, 1)

        # print contact info box, half width
        HALF_WIDTH = (T.width - 4) // 2
        print_contact(1, 4, HALF_WIDTH, 6)
        print_provider(4 + HALF_WIDTH, 4, HALF_WIDTH, 6)

        # print host info block
        print_host_info(0, 10, T.width, 6)

        # print network data box, half width
        print_network_info(0, 16, 64, T.height-LOGO_LINECOUNT-1)

        # logo should fill approx. the lower 1/3 of screen full width
        if LOGO_FILE is not None:
            # print out logo if defined
            print_logo(LOGO_TEXT, 0, T.height-LOGO_LINECOUNT-2)

        # finally: delay reload to configured seconds
        sleep(RELOAD_EVERY)
