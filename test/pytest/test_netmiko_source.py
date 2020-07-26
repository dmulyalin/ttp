import sys
sys.path.insert(0,'../..')
import pprint

import logging
logging.basicConfig(level="INFO")

from ttp import ttp

def test_netmiko_input_source():
    template = """
<vars>
hostname="gethostname"
</vars>

<input source="netmiko" name="arp">
devices = ["192.168.217.10", "192.168.217.7"]
device_type = "cisco_ios"
username = "cisco" # or get_user_input
password = "cisco" # or get_user_pass
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
"""
    # parser = ttp(template=template)
    # parser.parse()
    # res = parser.result()
    # pprint.pprint(res)
   
# uncomment to test it - need some devices running
# test_netmiko_input_source()