import sys

sys.path.insert(0, "../..")
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
    "IOL1": {
            "hostname": "192.168.217.10",
            "platform": "cisco_ios"
        },
    "IOL2": {
            "hostname": "192.168.217.7",
            "port": 22,
            "username": "cisco", # should generate error on wrong password
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
    "IOL1": {
            "hostname": "192.168.217.10",
            "platform": "cisco_ios",
        },
    "IOL2": {
            "hostname": "192.168.217.7",
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

# should print something like:
# [[{'arp': [{'age': '0',
#             'hostname': 'R1',
#             'interface': 'Ethernet0/0',
#             'ip': '192.168.1.104',
#             'mac': 'acfd.ce3c.7a58'},
#            {'age': '-',
#             'hostname': 'R1',
#             'interface': 'Ethernet0/0',
#             'ip': '192.168.1.151',
#             'mac': 'aabb.cc00.1000'}]},
#   {'arp': [{'age': '0',
#             'hostname': 'R2',
#             'interface': 'Ethernet0/0',
#             'ip': '192.168.1.104',
#             'mac': 'acfd.ce3c.7a58'},
#            {'age': '-',
#             'hostname': 'R2',
#             'interface': 'Ethernet0/0',
#             'ip': '192.168.1.153',
#             'mac': 'aabb.cc00.3000'}]},
#   {'interfaces': [{'description': 'MGMT',
#                    'hostname': 'R1',
#                    'interface': 'Ethernet0/0',
#                    'ip': '192.168.1.151',
#                    'mask': '255.255.255.0'},
#                   {'description': 'FREE',
#                    'hostname': 'R1',
#                    'interface': 'Ethernet0/1'},
#                   {'description': 'FREE',
#                    'hostname': 'R1',
#                    'interface': 'Ethernet0/2'},
#                   {'description': 'FREE',
#                    'hostname': 'R1',
#                    'interface': 'Ethernet0/3'}]},
#   {'interfaces': [{'hostname': 'R2',
#                    'interface': 'Ethernet0/0',
#                    'ip': '192.168.1.153',
#                    'mask': '255.255.255.0'},
#                   {'hostname': 'R2', 'interface': 'Ethernet0/1'},
#                   {'hostname': 'R2', 'interface': 'Ethernet0/2'},
#                   {'hostname': 'R2', 'interface': 'Ethernet0/3'}]}]]
