import sys
sys.path.insert(0,'../..')
import pprint
import logging

logging.basicConfig(level=logging.DEBUG)

from ttp import ttp

def test_line_when_its_start_re():
    data_to_parse_a="""
R1#sh vrrp
GigabitEthernet1 - Group 100
DC-LAN Subnet
State is Master
Virtual IP address is 192.168.10.1
Virtual MAC address is 0000.5e00.0164
Advertisement interval is 1.000 sec
Preemption enabled
Priority is 120
VRRS Group name DC_LAN
Track object 1 state Up decrement 30
Authentication text "hash"
Master Router is 192.168.1.233 (local), priority is 120
Master Advertisement interval is 1.000 sec
Master Down interval is 3.531 sec
Some other line
"""

    data_to_parse_b="""
R2#sh vrrp
GigabitEthernet1 - Group 100
State is Init
Virtual IP address is 192.168.10.1
Virtual MAC address is 0000.5e00.0164
Advertisement interval is 1.000 sec
Preemption enabled
Priority is 115
Authentication text "hash"
Master Router is 192.168.1.233, priority is 120
Master Advertisement interval is 1.000 sec
Master Down interval is 3.550 sec
"""

    ttp_template = """
<template name="vrrp" results="per_template">

<vars>
hostname="gethostname"
</vars>

<group name="{{ hostname }}.{{ interface }}.Group-{{ VRRP_Group }}">
{{ interface }} - Group {{ VRRP_Group | DIGIT }}
<group name="_">
{{ VRRP_Description | _line_ }}
State is {{ ignore }} {{ _end_ }}
</group>
State is {{ VRRP_State | contains("Master") | let("VRRP Master for this Group") }}
State is {{ VRRP_State | contains("Init") | let("VRRP Slave for this Group") }}
Virtual IP address is {{ VRRP_Virtual_IP | IP }}
Virtual MAC address is {{ VRRP_MAC | MAC }}
Advertisement interval is {{ adv_interval }} sec
Preemption {{ VRRP_Preempt }}
Priority is {{ VRRP_Priority }}
VRRS Group name {{ Group_Name }}
Track object {{ track_obj }} state {{ track_obj_status }} decrement {{ track_obj_decrement }}
Authentication text {{ Auth_Text }}
Master Router is {{ Master_IP }} (local), priority is {{ priority }}
Master Router is {{ Master_IP }}, priority is {{ priority }}
Master Advertisement interval is {{ master_int }} sec
Master Down interval is {{ master_down }} sec
</group>
</template>
"""
    parser = ttp(template=ttp_template)
    parser.add_input(data_to_parse_a, template_name="vrrp")
    parser.add_input(data_to_parse_b, template_name="vrrp")
    parser.parse()
    
    res = parser.result(structure="dictionary")
    #pprint.pprint(res, width=100)
    
    assert res == {'vrrp': {'R1': {'GigabitEthernet1': {'Group-100': {'Auth_Text': '"hash"',
                                                                    'Group_Name': 'DC_LAN',
                                                                    'Master_IP': '192.168.1.233',
                                                                    'VRRP_Description': 'DC-LAN Subnet',
                                                                    'VRRP_MAC': '0000.5e00.0164',
                                                                    'VRRP_Preempt': 'enabled',
                                                                    'VRRP_Priority': '120',
                                                                    'VRRP_Virtual_IP': '192.168.10.1',
                                                                    'adv_interval': '1.000',
                                                                    'master_down': '3.531',
                                                                    'master_int': '1.000',
                                                                    'priority': '120',
                                                                    'track_obj': '1',
                                                                    'track_obj_decrement': '30',
                                                                    'track_obj_status': 'Up'}}},
                            'R2': {'GigabitEthernet1': {'Group-100': {'Auth_Text': '"hash"',
                                                                    'Master_IP': '192.168.1.233',
                                                                    'VRRP_MAC': '0000.5e00.0164',
                                                                    'VRRP_Preempt': 'enabled',
                                                                    'VRRP_Priority': '115',
                                                                    'VRRP_State': 'VRRP Slave for this Group',
                                                                    'VRRP_Virtual_IP': '192.168.10.1',
                                                                    'adv_interval': '1.000',
                                                                    'master_down': '3.550',
                                                                    'master_int': '1.000',
                                                                    'priority': '120'}}}}}
                                                                    
                                                                    