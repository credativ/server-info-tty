
"""Small python tool to display some facts on a given server on a TTY."""

__author__ = 'Peter Dreuw'
__version__ = '0.1'


# This script needs the following packages to be installed
#  - python3-blessings
#  - python-fabulous

import socket
from time import sleep
from blessings import Terminal
import configparser

# import local libs

from NetworkInterface import Interface


#############################################################################
# global variables

INI_NAME = 'config-example.ini'  # '/etc/server-info-tty/config.ini'

reload_every = 60 # time in seconds to wait until reload (can be set in ini)

config = configparser.ConfigParser()

t = Terminal()



#############################################################################
# some handy logo handling functions

def read_logo(logo, replace_colors):
    """reads the ascii art logo file and inserts color codes
       returns plain text ascii art and line count in a tuple"""

    i = 0
    logo_data = ""
    with open(logo, 'r') as f:
        for line in iter(f.readline, ''):
            logo_data = logo_data + line
            i += 1

        f.close()

    logo_data = (logo_data
                 .replace(replace_colors["red"], t.red)
                 .replace(replace_colors["black"], t.white))
    return (logo_data, i)


def print_logo(logo_text, x, y):
    """prints the ascii art logo at (x,y)"""

    print(t.move(y, x)+logo_text)

    return


#############################################################################
# some handy network information gathering functions

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


#############################################################################
# main code


# read the ini file
config.read(INI_NAME)

# check if there is a logo defined
if 'logo' in config:
    logo_file = config['logo'].get("logo")
    replace_colors = {
        "red" : config['logo'].get("red", "r"),
        "black" : config['logo'].get("black", "b"),
    }
else:
    logo_file = None

    
# check if there is a sleep delay in ini file, defaults to 60 secs
if 'DEFAULT' in config:
    reload_every = int(config['DEFAULT'].get('reload', 60))



with t.fullscreen():
    # loop forever
    while 1:
        # clear screen
        print(t.clear())

        # print appliance name and basic information on system defined
        # in config.
        # this should cover first 1/4 of screen, full width


        # print network data box, half width

        
        # print contact info box, half width
        
        
        # logo should fill approx. the lower 1/3 of screen full width 
        if logo_file:
            # print out logo if defined
            (logotext, linecount) = read_logo(logo_file, replace_colors)
            print_logo(logotext, 0, t.height-linecount)


        # finally: delay reload to configured seconds
        sleep(reload_every)
