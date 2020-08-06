import sys
sys.path.insert(0,'../..')
import pprint

import logging
logging.basicConfig(level="ERROR")

from ttp import ttp

def test_nornir_input_source():
    template = """
<vars>
hostname="gethostname"
</vars>

<input source="nornir" name="arp">
hosts = {
    "R1": {
            "hostname": "192.168.1.151",
            "platform": "cisco_ios"
        },
    "R2": {
            "hostname": "192.168.1.153",
            "port": 22,
            "username": "ciscos", # should generate error on wrong password
            "password": "cisco",
            "platform": "cisco_ios"
        }   
}
username = "cisco"
password = "cisco"
commands = ["show ip arp"]
</input>

<group name="arp" input="arp">
Internet  {{ ip }}  {{ age }}   {{ mac }} ARPA   {{ interface }}
{{ hostname | set(hostname) }}
</group>


<input source="nornir" name="interfaces">
hosts = {
    "R1": {
            "hostname": "192.168.1.151",
            "platform": "cisco_ios",
        },
    "R2": {
            "hostname": "192.168.1.153",
            "platform": "cisco_ios",
        }   
}
username = "get_user_input"
password = "get_user_pass"
commands = "show run"
netmiko_kwargs = {
    "strip_prompt": False, 
    "strip_command": False
}
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
# test_nornir_input_source()