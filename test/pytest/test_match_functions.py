import sys

sys.path.insert(0, "../..")
import pprint
import logging
import json

logging.basicConfig(level=logging.DEBUG)

from ttp import ttp


def test_sformat_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | sformat("BSQ {}") }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description": "Storage", "interface": "BSQ Port-Channel11"},
                {"description": "RID", "interface": "BSQ Loopback0"},
                {"description": "Management", "interface": "BSQ Port-Channel12"},
                {"description": "Management", "interface": "BSQ Vlan777"},
            ]
        ]
    ]


# test_sformat_inline()


def test_sformat_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<vars>
var_1 = "BSQ {}"
</vars>

<group>
interface {{ interface | sformat(var_1) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description": "Storage", "interface": "BSQ Port-Channel11"},
                {"description": "RID", "interface": "BSQ Loopback0"},
                {"description": "Management", "interface": "BSQ Port-Channel12"},
                {"description": "Management", "interface": "BSQ Vlan777"},
            ]
        ]
    ]


def test_to_list_with_joinmatches():
    template = """
<input load="text">
interface GigabitEthernet3/3
 switchport trunk allowed vlan add 138,166,173 
 switchport trunk allowed vlan add 400,401,410
</input>
 
<group>
interface {{ interface }}
 switchport trunk allowed vlan add {{ trunk_vlans | to_list | joinmatches }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {
                    "interface": "GigabitEthernet3/3",
                    "trunk_vlans": ["138,166,173", "400,401,410"],
                }
            ]
        ]
    ]


# test_to_list_with_joinmatches()


def test_multiple_joinmatches():
    data = """
SWITCH# show vlan port 2/11 detail

Status and Counters - VLAN Information - for ports 2/11

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

60 ABC | Port-based No No Tagged

70 DEF | Port-based No No Tagged

101 GHIJ | Port-based No No Untagged

105 KLMNO | Port-based No No Tagged

116 PQRS | Port-based No No Tagged

117 TVU | Port-based No No Tagged

SWITCH# show vlan port 2/12 detail

Status and Counters - VLAN Information - for ports 2/12

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

61 ABC | Port-based No No Tagged

71 DEF | Port-based No No Tagged

103 GHI | Port-based No No Untagged
    """
    template = """
<vars>
hostname="gethostname"
</vars>

<group name="vlans*">
Status and Counters - VLAN Information - for ports {{ Port_Number }}
{{ Tagged_VLAN | joinmatches(", ") }} {{ name | joinmatches(", ") }} | {{ ignore }} {{ ignore }} {{ ignore }} Tagged
{{ Untagged_VLAN }}                   {{ name | joinmatches(", ") }} | {{ ignore }} {{ ignore }} {{ ignore }} Untagged
{{ Hostname | set(hostname) }}
</group>   
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [
        [
            {
                "vlans": [
                    {
                        "Hostname": "SWITCH",
                        "Port_Number": "2/11",
                        "Tagged_VLAN": "60, 70, 105, 116, 117",
                        "Untagged_VLAN": "101",
                        "name": "ABC, DEF, GHIJ, KLMNO, PQRS, TVU",
                    },
                    {
                        "Hostname": "SWITCH",
                        "Port_Number": "2/12",
                        "Tagged_VLAN": "61, 71",
                        "Untagged_VLAN": "103",
                        "name": "ABC, DEF, GHI",
                    },
                ]
            }
        ]
    ]


# test_multiple_joinmatches()


def test_joinmatches_with_ignore():
    data = """
SWITCH# show vlan port 2/11 detail

Status and Counters - VLAN Information - for ports 2/11

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

60 ABC | Port-based No No Tagged

70 DEF | Port-based No No Tagged

101 GHIJ | Port-based No No Untagged

105 KLMNO | Port-based No No Tagged

116 PQRS | Port-based No No Tagged

117 TVU | Port-based No No Tagged

SWITCH# show vlan port 2/12 detail

Status and Counters - VLAN Information - for ports 2/12

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

61 ABC | Port-based No No Tagged

71 DEF | Port-based No No Tagged

103 GHI | Port-based No No Untagged
    """
    template = """
<vars>
hostname="gethostname"
</vars>

<group name="vlans*">
Status and Counters - VLAN Information - for ports {{ Port_Number }}
{{ Tagged_VLAN | joinmatches(" ") }} {{ ignore }} | {{ ignore }} {{ ignore }} {{ ignore }} Tagged
{{ Untagged_VLAN }}                  {{ ignore }} | {{ ignore }} {{ ignore }} {{ ignore }} Untagged
{{ Hostname | set(hostname) }}
</group>   
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "vlans": [
                    {
                        "Hostname": "SWITCH",
                        "Port_Number": "2/11",
                        "Tagged_VLAN": "60 70 105 116 117",
                        "Untagged_VLAN": "101",
                    },
                    {
                        "Hostname": "SWITCH",
                        "Port_Number": "2/12",
                        "Tagged_VLAN": "61 71",
                        "Untagged_VLAN": "103",
                    },
                ]
            }
        ]
    ]


def test_match_variable_default_set_to_list():
    template = """
<input load="text">
interface Port-Channel11
  ip address 1.1.1.1/24
interface Loopback0
</input>

<group>
interface {{ interface }}
  ip address {{ ip | default([]) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11", "ip": "1.1.1.1/24"},
                {"interface": "Loopback0", "ip": []},
            ]
        ]
    ]


# test_match_variable_default_set_to_list()


def test_match_variable_default_set_to_string():
    template = """
<input load="text">
interface Port-Channel11
  ip address 1.1.1.1/24
interface Loopback0
</input>

<group>
interface {{ interface }}
  ip address {{ ip | default("Undefined") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11", "ip": "1.1.1.1/24"},
                {"interface": "Loopback0", "ip": "Undefined"},
            ]
        ]
    ]


# test_match_variable_default_set_to_string()


def test_match_variable_default_for_start_regex():
    template = """
<input load="text">
interface Port-Channel11
  description Staff ports
</input>

<group name="ntp-1**">
ntp server {{ server | default('Unconfigured') }}
 ntp source {{ source | default("undefined") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    # print(json.dumps(res, sort_keys=True, indent=4, separators=(",", ": ")))
    assert res == [[{"ntp-1": {"server": "Unconfigured", "source": "undefined"}}]]


# test_match_variable_default_for_start_regex()


def test_match_variable_default_set_to_dictionary():
    template = """
<input load="text">
interface Port-Channel11
  ip address 1.1.1.1/24
interface Loopback0
</input>

<group>
interface {{ interface }}
  ip address {{ ip | default({"defined": False}) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11", "ip": "1.1.1.1/24"},
                {"interface": "Loopback0", "ip": {"defined": False}},
            ]
        ]
    ]


# test_match_variable_default_set_to_dictionary()


def test_match_variable_set_and_let_for_same_variable_with_special_chars():
    template = """
<input load="text">
interface Port-Channel11
 ip address 1.1.1.1/24
interface Loopback0
 ip address 1.1.2.1/24
 shutdown
</input>

<group>
interface {{ interface }}
 ip address {{ ip | default({"defined": False}) }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {
                    "admin-status": "up",
                    "interface": "Port-Channel11",
                    "ip": "1.1.1.1/24",
                    "link-up-down-trap-enable": "enabled",
                },
                {
                    "admin-status": "down",
                    "enabled": False,
                    "interface": "Loopback0",
                    "ip": "1.1.2.1/24",
                    "link-up-down-trap-enable": "enabled",
                },
            ]
        ]
    ]


# test_match_variable_set_and_let_for_same_variable_with_special_chars()


def test_let_and_set():
    data = """
interface Port-Channel11
 ip address 1.1.1.1/24
 description bla bla bla
 shutdown
interface Port-Channel22
 ip address 1.1.2.1/24
 description bla bla2 bla2
    """
    template = """
interface {{ name }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {
                    "admin-status": "down",
                    "description": "bla bla bla",
                    "enabled": False,
                    "link-up-down-trap-enable": "enabled",
                    "name": "Port-Channel11",
                },
                {
                    "admin-status": "up",
                    "description": "bla bla2 bla2",
                    "link-up-down-trap-enable": "enabled",
                    "name": "Port-Channel22",
                },
            ]
        ]
    ]


# test_let_and_set()


def test_line_with_joinmatches():
    """
    Issue - when having to use sanitized variable names, joinmatches was failing
    to find variable in group re variables dictionary, as that dictionary was keyd
    byt sanitized variable name, but by the time joinmatches seeing results, results
    already have original variable name.
    """
    data = """
Chassis id: 12346.1234.1234
Port id: Eth1/1
Local Port id: Eth6/1
Port Description: Uplink to vrf1
System Name: switch-name-1
System Description: Cisco Nexus Operating System (NX-OS) Software 21.324(3)N2(3.12b)
TAC support: http://www.cisco.com/tac
Copyright (c) 2002-2099, Cisco Systems, Inc. All rights reserved.
Time remaining: 333 seconds
System Capabilities: B, R
Enabled Capabilities: B, R
Management Address: 1.1.1.1
Vlan ID: 111
    """
    template = """
System Description: {{ system-description | re(".+") | joinmatches(" ") }}
{{ system-description | _line_ | joinmatches(" ") }}
Time remaining: {{ ignore }} seconds {{ _end_ }}
    """
    parser = ttp(data, template, log_level="error")
    parser.parse()

    res = parser.result()
    pprint.pprint(res, width=100)
    assert res == [
        [
            {
                "system-description": "Cisco Nexus Operating System (NX-OS) Software 21.324(3)N2(3.12b) TAC "
                "support: http://www.cisco.com/tac Copyright (c) 2002-2099, Cisco "
                "Systems, Inc. All rights reserved."
            }
        ]
    ]


test_line_with_joinmatches()
