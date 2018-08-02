#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright: 2017, 2018 peter.dreuw@credativ.de
# License: MIT, see LICENSE.txt for details.
#

"""
This class stores information about the current computers network interfaces.
The data is filled by class methods parsing the ip command output
"""

import subprocess
import re


###############################################################################
# Class definition class cInterface
# this is a helper class to either encapsulate network interface data and to
# retrieve these information from the output of /bin/ip
#

class Interface(object):      # pylint: disable=too-few-public-methods
    """keeps data for network interface"""

    interfaces = []
    first_interface = None

    def __init__(self, name):
        """creates instance with interface name"""
        self.name = name
        self.type = ""
        self.hwaddress = ""
        self.ipv4 = ""
        self.ipv6 = ""
        return

    @classmethod
    def get_interfaces(cls):
        """func to parse the output of /bin/ip to gather mac and IP address"""

        if cls.interfaces:
            # if we already populated the interfaces array, gtfo
            return cls.interfaces

        ifnr = re.compile(r"\d[:]")

        # first round: find the interfaces
        ip_out = subprocess.check_output(['/bin/ip', 'addr'], shell=False,
                                         universal_newlines=True)

        for row in ip_out.splitlines():
            words = row.split(' ')
            if ifnr.match(words[0]):
                # first line of new interface definition
                # create new cInterface object, take the if name and ignore
                # the rest

                # cut off the ":" at  the end of if name
                current = Interface(words[1][:-1])

                cls.interfaces.append(current)
            else:
                # additional line to parse for the current interface
                index = 0

                while index < len(words):
                    if words[index] != "":    # skip empty
                        if words[index][0:5] == "link/":
                            # if it starts with "link/" then we got the
                            # interface type and next IS hw address
                            current.type = words[index][5:]
                            index = index + 1
                            current.hwaddress = words[index]

                        elif words[index] == "inet":
                            # in that case, next one is ipv4 address
                            index = index + 1
                            current.ipv4 = words[index]

                        elif words[index] == "inet6":
                            # Houston, we got an IPv6 address next step
                            index = index + 1
                            current.ipv6 = words[index]

                    index = index + 1

        return Interface.interfaces

    @classmethod
    def get_first_interface(cls):
        """returns first network interface, skipping the lookback"""
        if cls.first_interface is not None:
            return cls.first_interface

        iflist = cls.get_interfaces()
        for i in iflist:
            if i.type != "loopback":
                cls.first_interface = i
                break

        return cls.first_interface

    @classmethod
    def get_interface_count(cls):
        """
        returns the number of interfaces found excluding loopback,
        will trigger a search if needed
        """

        # make shure class variables are filled
        cls.get_first_interface()

        count = 0

        for i in cls.interfaces:
            if i.type != "loopback":
                count = count + 1

        return count
