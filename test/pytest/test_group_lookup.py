import sys

sys.path.insert(0, "../..")
import pprint

from ttp import ttp


def test_group_lookup_using_lookup_table_action_replace():
    template_1 = """
<input load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.2        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.14.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
</input>

<lookup name="lookup_data" load="ini">
[ip_addresses]
10.12.13.2 = app_1
10.12.14.3 = app_2
</lookup>

<group name="arp" lookup="'ip', name='lookup_data.ip_addresses', replace=True">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
</group>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "arp": [
                    {
                        "age": "98",
                        "interface": "FastEthernet2.13",
                        "ip": "app_1",
                        "mac": "0950.5785.5cd1",
                    },
                    {
                        "age": "131",
                        "interface": "GigabitEthernet2.13",
                        "ip": "app_2",
                        "mac": "0150.7685.14d5",
                    },
                ]
            }
        ]
    ]


def test_group_lookup_using_lookup_table_action_add_field():
    template_1 = """
<input load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.2        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.14.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
</input>

<lookup name="lookup_data" load="python">
{ "ip_addresses": {
  "10.12.13.2": "app_1",
  "10.12.14.3": "app_2"}}
</lookup>

<group name="arp" lookup="'ip', name='lookup_data.ip_addresses', add_field='APP'">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
</group>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "arp": [
                    {
                        "APP": "app_1",
                        "age": "98",
                        "interface": "FastEthernet2.13",
                        "ip": "10.12.13.2",
                        "mac": "0950.5785.5cd1",
                    },
                    {
                        "APP": "app_2",
                        "age": "131",
                        "interface": "GigabitEthernet2.13",
                        "ip": "10.12.14.3",
                        "mac": "0150.7685.14d5",
                    },
                ]
            }
        ]
    ]


def test_group_lookup_using_lookup_table_action_update():
    template_1 = """
<input load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.2        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.14.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
</input>

<lookup name="lookup_data" load="yaml">
ip_addresses:
  10.12.13.2: 
    app_name: app_1
    app_owner: team2
  10.12.14.3: 
    app_name: app_2
    app_owner: team_2
</lookup>

<group name="arp" lookup="'ip', name='lookup_data.ip_addresses', update=True">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
</group>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "arp": [
                    {
                        "age": "98",
                        "app_name": "app_1",
                        "app_owner": "team2",
                        "interface": "FastEthernet2.13",
                        "ip": "10.12.13.2",
                        "mac": "0950.5785.5cd1",
                    },
                    {
                        "age": "131",
                        "app_name": "app_2",
                        "app_owner": "team_2",
                        "interface": "GigabitEthernet2.13",
                        "ip": "10.12.14.3",
                        "mac": "0150.7685.14d5",
                    },
                ]
            }
        ]
    ]


def test_group_lookup_using_group_in_same_input_action_update():
    template_1 = """
<input load="text">
interface FastEthernet2.13
 description Customer CPE interface
 ip address 10.12.13.1 255.255.255.0
 vrf forwarding CPE-VRF
!
interface GigabitEthernet2.13
 description Customer CPE interface
 ip address 10.12.14.1 255.255.255.0
 vrf forwarding CUST1
!
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.2        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.14.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
</input>

<group name="interfaces.{{ interface }}">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ subnet | PHRASE | to_ip | network | to_str }}
 vrf forwarding {{ vrf }}
</group>

<group name="arp" lookup="interface, group='interfaces', update=True">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
</group>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "arp": [
                    {
                        "age": "98",
                        "description": "Customer CPE interface",
                        "interface": "FastEthernet2.13",
                        "ip": "10.12.13.2",
                        "mac": "0950.5785.5cd1",
                        "subnet": "10.12.13.0/24",
                        "vrf": "CPE-VRF",
                    },
                    {
                        "age": "131",
                        "description": "Customer CPE interface",
                        "interface": "GigabitEthernet2.13",
                        "ip": "10.12.14.3",
                        "mac": "0150.7685.14d5",
                        "subnet": "10.12.14.0/24",
                        "vrf": "CUST1",
                    },
                ],
                "interfaces": {
                    "FastEthernet2.13": {
                        "description": "Customer CPE interface",
                        "subnet": "10.12.13.0/24",
                        "vrf": "CPE-VRF",
                    },
                    "GigabitEthernet2.13": {
                        "description": "Customer CPE " "interface",
                        "subnet": "10.12.14.0/24",
                        "vrf": "CUST1",
                    },
                },
            }
        ]
    ]


def test_group_lookup_using_group_from_another_input_action_update():
    template_1 = """
<input name="interfaces" load="text">
interface FastEthernet2.13
 description Customer CPE interface
 ip address 10.12.13.1 255.255.255.0
 vrf forwarding CPE-VRF
!
interface GigabitEthernet2.13
 description Customer CPE interface
 ip address 10.12.14.1 255.255.255.0
 vrf forwarding CUST1
!
</input>

<input name="arp" load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.2        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.14.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
</input>

<group name="interfaces.{{ interface }}" input="interfaces">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ subnet | PHRASE | to_ip | network | to_str }}
 vrf forwarding {{ vrf }}
</group>

<group name="arp" lookup="interface, group='interfaces', update=True" input="arp">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
</group>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "interfaces": {
                    "FastEthernet2.13": {
                        "description": "Customer CPE interface",
                        "subnet": "10.12.13.0/24",
                        "vrf": "CPE-VRF",
                    },
                    "GigabitEthernet2.13": {
                        "description": "Customer CPE " "interface",
                        "subnet": "10.12.14.0/24",
                        "vrf": "CUST1",
                    },
                }
            },
            {
                "arp": [
                    {
                        "age": "98",
                        "description": "Customer CPE interface",
                        "interface": "FastEthernet2.13",
                        "ip": "10.12.13.2",
                        "mac": "0950.5785.5cd1",
                        "subnet": "10.12.13.0/24",
                        "vrf": "CPE-VRF",
                    },
                    {
                        "age": "131",
                        "description": "Customer CPE interface",
                        "interface": "GigabitEthernet2.13",
                        "ip": "10.12.14.3",
                        "mac": "0150.7685.14d5",
                        "subnet": "10.12.14.0/24",
                        "vrf": "CUST1",
                    },
                ]
            },
        ]
    ]


def test_group_lookup_in_template_results_per_input_action_update():
    template_1 = """
<template name="interfaces">
<input load="text">
interface FastEthernet2.13
 description Customer CPE interface
 ip address 10.12.13.1 255.255.255.0
 vrf forwarding CPE-VRF
!
interface GigabitEthernet2.13
 description Customer CPE interface
 ip address 10.12.14.1 255.255.255.0
 vrf forwarding CUST1
!
</input>

<group name="{{ interface }}">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ subnet | PHRASE | to_ip | network | to_str }}
 vrf forwarding {{ vrf }}
</group>
</template>

<template name="arp">
<input load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.2        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.14.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
</input>

<group lookup="interface, template='interfaces', update=True">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
</group>
</template>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "FastEthernet2.13": {
                    "description": "Customer CPE interface",
                    "subnet": "10.12.13.0/24",
                    "vrf": "CPE-VRF",
                },
                "GigabitEthernet2.13": {
                    "description": "Customer CPE interface",
                    "subnet": "10.12.14.0/24",
                    "vrf": "CUST1",
                },
            }
        ],
        [
            [
                {
                    "age": "98",
                    "description": "Customer CPE interface",
                    "interface": "FastEthernet2.13",
                    "ip": "10.12.13.2",
                    "mac": "0950.5785.5cd1",
                    "subnet": "10.12.13.0/24",
                    "vrf": "CPE-VRF",
                },
                {
                    "age": "131",
                    "description": "Customer CPE interface",
                    "interface": "GigabitEthernet2.13",
                    "ip": "10.12.14.3",
                    "mac": "0150.7685.14d5",
                    "subnet": "10.12.14.0/24",
                    "vrf": "CUST1",
                },
            ]
        ],
    ]


def test_group_lookup_in_template_results_per_template_action_add_field():
    template_1 = """
<template name="interfaces" results="per_template">
<input load="text">
interface FastEthernet2.13
 description Customer CPE interface
 ip address 10.12.13.1 255.255.255.0
 vrf forwarding CPE-VRF
!
</input>

<input load="text">
interface GigabitEthernet2.13
 description Customer CPE interface
 ip address 10.12.14.1 255.255.255.0
 vrf forwarding CUST1
!
</input>

<group name="{{ interface }}">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ subnet | PHRASE | to_ip | network | to_str }}
 vrf forwarding {{ vrf }}
</group>
</template>

<template name="arp">
<input load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.2        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.14.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
</input>

<group lookup="interface, template='interfaces', add_field='intf_info'">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
</group>
</template>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        {
            "FastEthernet2.13": {
                "description": "Customer CPE interface",
                "subnet": "10.12.13.0/24",
                "vrf": "CPE-VRF",
            },
            "GigabitEthernet2.13": {
                "description": "Customer CPE interface",
                "subnet": "10.12.14.0/24",
                "vrf": "CUST1",
            },
        },
        [
            [
                {
                    "age": "98",
                    "interface": "FastEthernet2.13",
                    "intf_info": {
                        "description": "Customer CPE interface",
                        "subnet": "10.12.13.0/24",
                        "vrf": "CPE-VRF",
                    },
                    "ip": "10.12.13.2",
                    "mac": "0950.5785.5cd1",
                },
                {
                    "age": "131",
                    "interface": "GigabitEthernet2.13",
                    "intf_info": {
                        "description": "Customer CPE interface",
                        "subnet": "10.12.14.0/24",
                        "vrf": "CUST1",
                    },
                    "ip": "10.12.14.3",
                    "mac": "0150.7685.14d5",
                },
            ]
        ],
    ]
