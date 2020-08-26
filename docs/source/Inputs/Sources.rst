Sources
===================

Inputs can use various sources to retrieve data for parsing.

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Source
     - Description
   * - `Netmiko`_   
     - uses Netmiko library to retrieve data from devices over SSH or Telnet
   * - `Nornir`_   
     - uses Nornir library with Netmiko plugin to retrieve data from devices
     
Netmiko
---------

**Prerequisites:** `Netmiko library <https://pypi.org/project/netmiko/>`_ need to be installed on the system

This source allows to retrieve configuration or state data from network devices using SSH or Telnet by connecting to devices one by one.

**Supported attributes**

* ``commands`` list of commands to retrieve from devices
* ``devices`` list of devices to retrieve commands from
* ``username`` device username, if value is ``get_user_input`` prompts user for input
* ``password`` device password, if value is ``get_user_pass`` prompts user for input
* ``Netmiko kwargs`` - any other arguments to pass on to `Netmiko ConnectHandler <https://ktbyers.github.io/netmiko/docs/netmiko/index.html#netmiko.ConnectHandler>`_ method

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
    
Nornir
---------

**Prerequisites:** `Nornir library <https://pypi.org/project/nornir/>`_ need to be installed on the system

This source allows to retrieve configuration or state data from network devices using Nornir library. Nornir runs connections to devices in parallel, allowing significantly reduce the time required to retrieve data.

This source uses `netmiko_send_command <https://nornir.readthedocs.io/en/latest/plugins/tasks/networking.html#nornir.plugins.tasks.networking.netmiko_send_command>`_ task plugin to send commands to devices.

**Supported attributes**

* ``hosts`` Nornir hosts inventory data with devices' details
* ``commands`` list of commands to execute on devices
* ``username`` devices username, if value is ``get_user_input`` prompts user for input
* ``password`` devices password, if value is ``get_user_pass`` prompts user for input
* ``num_workers`` default is 100, maximum number of worker threads to instantiate for tasks execution
* ``netmiko_kwargs`` arguments to pass on to `netmiko_send_command <https://nornir.readthedocs.io/en/latest/plugins/tasks/networking.html#nornir.plugins.tasks.networking.netmiko_send_command>`_ task plugin, default values:: 

    strip_prompt = False
    strip_command = False


Nornir normally uses inventory data to get username and password values, TTP allows to specify these attributes separately and share them with each host in inventory. Username and password provided within hosts inventory considered to be more specific and not overridden.

**Example**

Template::

    <input source="nornir" name="arp">
    hosts = {
        "R1": {
                "hostname": "192.168.1.151",
                "platform": "cisco_ios"
            },
        "R2": {
                "hostname": "192.168.1.153",
                "username": "cisco",
                "password": "cisco",
                "platform": "cisco_ios"
            }   
    }
    username = "get_user_input"
    password = "get_user_pass"
    commands = ["show ip arp"]
    netmiko_kwargs = {
        "strip_prompt": False, 
        "strip_command": False
    }
    </input>
    
    <group name="arp" input="arp">
    Internet  {{ ip }}  {{ age }}   {{ mac }} ARPA   {{ interface }}
    {{ hostname | set(hostname) }}
    </group>