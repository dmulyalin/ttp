Sources
===================

Inputs can uses various sources to retrieve data for parsing.

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Source
     - Description
   * - `Netmiko`_   
     - uses Netmiko library to retrieve data from devices over SSH or Telnet
	 
Netmiko
---------

**Prerequisites:** `Netmiko library <https://pypi.org/project/netmiko/>`_ need to be installed on the system

This source allows to retrieve configuration or state data from network devices using SSH or Telnet by connecting to devices one by one (serial execution).

**Supported attributes**

* ``commands`` list of commands to retrieve from devices
* ``devices`` list of devices to visit
* ``get_user_input`` can be used as `username` attribute value - prompts user for input
* ``get_user_pass`` can be used as `password` attribute value - prompts user for input
* ``Netmiko kwargs`` - any other arguments supported by Netmiko module for that particular driver

**Example**

Template::

    <vars>
    hostname="gethostname"
    </vars>
    
    <input source="netmiko" name="arp">
    devices = ["192.168.217.10", "192.168.217.7"]
    device_type = "cisco_ios"
    username = "cisco"
    password = "cisco"
    commands = ["show ip arp"]
    </input>
    
    <group name="arp" input="arp">
    Internet  {{ ip }}  {{ age }}   {{ mac }} ARPA   {{ interface }}
    {{ hostname | set(hostname) }}
    </group>
    
    
    <input source="netmiko" name="interfaces">
    host = "192.168.217.10"
    device_type = "cisco_ios"
    username = "get_user_input"
    password = "get_user_pass"
    commands = ["show run"]
    </input>
    
    <group name="interfaces" input="interfaces">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     encapsulation dot1Q {{ dot1q }}
     ip address {{ ip }} {{ mask }}
    {{ hostname | set(hostname) }}
    </group>