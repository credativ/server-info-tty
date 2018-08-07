# server-info-tty

Small python tool to display some facts on a given server on a TTY.


## Idea

This tool should be installed in replace of a getty job on a standard Linux
Terminal. It will display defined information on the given host. This comes
in handy if used in a large scale server housing environment. An admin could
just plugin a keyboard and monitor to the system and finds anything needed to
proceed on the screen.

Just think of an appliance that does DHCP and you don't have the MAC address in
a large server farm. server-info-tty will display the set IP address etc.

This is accompanied by contact names, adress, phone numbers etc. as you like
when configuring this small tool.


## Status
In development

## TODO:
* improve documentation
* add network gateway functionallity
* add samples for systemd tty installation
* improve layout calculations which are more or less static right now
  