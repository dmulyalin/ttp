import sys
import os
sys.path.insert(0, "../..")
import pprint

import logging

logging.basicConfig(level=logging.DEBUG)

from ttp import ttp


def test_match_vars_with_hyphen():
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
interface {{ interface-name }}
  description {{ description-bla }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description-bla": "Storage", "interface-name": "Port-Channel11"},
                {"description-bla": "RID", "interface-name": "Loopback0"},
                {"description-bla": "Management", "interface-name": "Port-Channel12"},
                {"description-bla": "Management", "interface-name": "Vlan777"},
            ]
        ]
    ]


# test_match_vars_with_hyphen()


def test_match_vars_with_dot():
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
interface {{ interface.name }}
  description {{ description.bla }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description.bla": "Storage", "interface.name": "Port-Channel11"},
                {"description.bla": "RID", "interface.name": "Loopback0"},
                {"description.bla": "Management", "interface.name": "Port-Channel12"},
                {"description.bla": "Management", "interface.name": "Vlan777"},
            ]
        ]
    ]


def test_match_vars_starts_with_digit():
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
interface {{ 77interface.name }}
  description {{ 77description.bla }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"77description.bla": "Storage", "77interface.name": "Port-Channel11"},
                {"77description.bla": "RID", "77interface.name": "Loopback0"},
                {
                    "77description.bla": "Management",
                    "77interface.name": "Port-Channel12",
                },
                {"77description.bla": "Management", "77interface.name": "Vlan777"},
            ]
        ]
    ]


def test_match_vars_multiple_non_alpha_chars():
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
interface {{ 77interface.#$%name }}
  description {{ 77description.*(-bla }}
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
                    "77description.*(-bla": "Storage",
                    "77interface.#$%name": "Port-Channel11",
                },
                {"77description.*(-bla": "RID", "77interface.#$%name": "Loopback0"},
                {
                    "77description.*(-bla": "Management",
                    "77interface.#$%name": "Port-Channel12",
                },
                {
                    "77description.*(-bla": "Management",
                    "77interface.#$%name": "Vlan777",
                },
            ]
        ]
    ]


def test_match_vars_set_with_hyphen():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
  no switchport
interface Vlan777
  description Management
interface Port-Channel27
  no switchport
</input>

<group>
interface {{ interface-name }}
  description {{ description-bla | default("Undefined") }}
  no switchport {{ no-switchport | set(True) }}
  {{ is-shutdown | set(False) }}
</group>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {
                    "description-bla": "Storage",
                    "interface-name": "Port-Channel11",
                    "is-shutdown": False,
                },
                {
                    "description-bla": "RID",
                    "interface-name": "Loopback0",
                    "is-shutdown": False,
                },
                {
                    "description-bla": "Management",
                    "interface-name": "Port-Channel12",
                    "is-shutdown": False,
                    "no-switchport": True,
                },
                {
                    "description-bla": "Management",
                    "interface-name": "Vlan777",
                    "is-shutdown": False,
                },
                {
                    "description-bla": "Undefined",
                    "interface-name": "Port-Channel27",
                    "is-shutdown": False,
                    "no-switchport": True,
                },
            ]
        ]
    ]


# test_match_vars_set_with_hyphen()


def test_per_template_mode():
    data_1 = """
interface Port-Chanel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
    """
    data_2 = """
interface Port-Chane10
  description Storage Management
interface Loopback77
  description RID
interface Vlan321
  description Management    
    """
    template = """
<template name="top_key_name" results="per_template">
<group name="interfaces*">
interface {{ interface }}
  description {{ description }}
</group>
</template>
    """
    parser = ttp(template=template, log_level="error")
    parser.add_input(data_1, template_name="top_key_name")
    parser.add_input(data_2, template_name="top_key_name")
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res, width=150)
    assert res == {
        "top_key_name": {
            "interfaces": [
                {"interface": "Port-Chanel11"},
                {"description": "RID", "interface": "Loopback0"},
                {"description": "Management", "interface": "Vlan777"},
                {"interface": "Port-Chane10"},
                {"description": "RID", "interface": "Loopback77"},
                {"description": "Management", "interface": "Vlan321"},
            ]
        }
    }


# test_per_template_mode()


def test_newline_with_carriage_return():
    data = b"\ninterface Port-Chanel11\r\n\r\n\r\n  description Storage_Management\r\ninterface Loopback0\n  description RID\ninterface Vlan777\n  description Management\r\n".decode(
        "utf-8"
    )
    template = """
<group name="interfaces*">
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            {
                "interfaces": [
                    {"description": "Storage_Management", "interface": "Port-Chanel11"},
                    {"description": "RID", "interface": "Loopback0"},
                    {"description": "Management", "interface": "Vlan777"},
                ]
            }
        ]
    ]


# test_newline_with_carriage_return()


def test_groups_with_defaults_only_and_with_children_with_defaults_only():
    template = """
<input load="text">
device-hostame uptime is 27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds
</input>

<group name="uptime-1**">
device-hostame uptime is {{ uptime | PHRASE }}
<group name="child_with_default">
 some line with {{ var1 | default("val1") }}
</group>
</group>

<group name="domain" default="Uncknown">
Default domain is {{ fqdn }}
</group>

<group name="ntp-1**">
ntp server {{ server | default('Unconfigured') }}
 ntp source {{ source | default("undefined") }}
<group name="another_child_grp_with_default**">
 npt peer {{ val2 | default("None") }}
<group name="deeper_child_with_defaults" default="something">
 another string {{ val5 }}
 my string {{ val4 }}
</group>
</group>
<group name="another_child_grp_without_default">
 npt peers {{ val3 }}
</group>
</group>

<group name="ntp-2">
ntp server {{ server }}
 ntp source {{ source | default("undefined") }}
</group>

<group name="snmp-1" default="Uncknown">
snmp community {{ community }}
snmp acl {{ acl }}
</group>


<group name="snmp-2-with-group-output**" default="Uncknown" output="out-1">
snmp community {{ community }}
snmp acl {{ acl }}
<group name="snmp_child_with_defaults" default="None">
 snmp source {{ ip }}
</group>
<group name="snmp_child_without_defaults">
 snmp community {{ comm_val }}
</group>
</group>

<output name="out-1"/>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "domain": {"fqdn": "Uncknown"},
                    "ntp-1": {
                        "another_child_grp_with_default": {
                            "deeper_child_with_defaults": {
                                "val4": "something",
                                "val5": "something",
                            },
                            "val2": "None",
                        },
                        "server": "Unconfigured",
                        "source": "undefined",
                    },
                    "snmp-1": {"acl": "Uncknown", "community": "Uncknown"},
                    "uptime-1": {
                        "child_with_default": {"var1": "val1"},
                        "uptime": "27 weeks, 3 days, 10 hours, 46 minutes, 10 "
                        "seconds",
                    },
                },
                {
                    "snmp-2-with-group-output": {
                        "acl": "Uncknown",
                        "community": "Uncknown",
                        "snmp_child_with_defaults": {"ip": "None"},
                    }
                },
            ]
        ]
    ]


# test_groups_with_defaults_only_and_with_children_with_defaults_only()


def test_hierarch_template():
    template = """
<vars>
hostname='gethostname' 
</vars>

<group name="{{ hostname }}.bgp_config.AS_{{ loca_as }}">
router bgp {{ bgp_as | record("loca_as") }}
  router-id {{ rid }}
  <group name="vrfs*.{{ VRF }}">
  vrf {{ VRF }}
    {{ hostname | set("hostname") }}
    {{ local_as | set("loca_as") }}
    <group name="afi**">
      <group name="Unicast**.{{ AFI }}">
    address-family {{ AFI }} unicast
      network {{ network | joinmatches() }}
      redistribute direct route-map {{ redistr_direct_rpl }}
      </group>
    </group>
    <group name="peers**.{{ PEER }}">    
    neighbor {{ PEER }}
      remote-as {{ remote_as }}
      description {{ description }}
      <group name="afi**.{{ AFI }}">
       <group name="Unicast**">
      address-family {{ AFI }} unicast
        shutdown {{ shutdown | set("True") }}
        allowas-in {{ allow_as_in | set("True") }}
        route-map {{ rpl_in }} in
        route-map {{ rpl_out }} out
       </group>
      </group>
    </group>
  </group>
</group>
    """
    data = """
sw1# show run | sec bgp
router bgp 65000
  router-id 10.1.2.2
  vrf cust1
    address-family ipv4 unicast
      network 1.1.1.10/26
      redistribute direct route-map VRF-DIRECT->BGP-V4
    neighbor 1.1.1.1
      remote-as 65001
      description FIREWALLs
      no dynamic-capability
      address-family ipv4 unicast
        allowas-in
        route-map 65001-BGP-IMPORT-V4 in
        route-map 65001-BGP-EXPORT-V4 out
    neighbor 2.2.2.2
      remote-as 65002
      description SLB Front
      address-family ipv4 unicast
        allowas-in
        route-map SLB-BGP-IMPORT-V4 in
        route-map SLB-BGP-EXPORT-V4 out
    neighbor 3.3.3.3
      remote-as 1234
      description Internet BDR
      address-family ipv4 unicast
        route-map INTERNET-IMPORT-V4 in
        route-map INTERNET-EXPORT-V4 out
  vrf cust2
    address-family ipv4 unicast
      redistribute direct route-map  VRF-DIRECT->BGP-V4
    neighbor 4.4.4.4
      remote-as 4567
      description SLB Back
      address-family ipv4 unicast
        allowas-in
        route-map SLBB-BGP-IMPORT-V4 in
        route-map SLBB-BGP-EXPORT-V4 out
  vrf cust3
    router-id 10.227.146.9
    address-family ipv4 unicast
      redistribute direct route-map C3-DIRECT->BGP-V4
    neighbor 5.5.5.5
      remote-as 65100
      description cist2 core
      no dynamic-capability
      address-family ipv4 unicast
        route-map C3-BGP-IMPORT-V4 in
        route-map C3-BGP-EXPORT-V4 out
    neighbor 6.6.6.6
      remote-as 65200
      description C3: Firewalls
      address-family ipv4 unicast
        allowas-in 1
        route-map C3-FW-BGP-IMPORT-V4 in
        route-map C3-FW-BGP-EXPORT-V4 out    
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "sw1": {
                    "bgp_config": {
                        "AS_65000": {
                            "bgp_as": "65000",
                            "rid": "10.1.2.2",
                            "vrfs": [
                                {
                                    "cust1": {
                                        "afi": {
                                            "Unicast": {
                                                "ipv4": {
                                                    "network": "1.1.1.10/26",
                                                    "redistr_direct_rpl": "VRF-DIRECT->BGP-V4",
                                                }
                                            }
                                        },
                                        "local_as": "65000",
                                        "peers": {
                                            "1.1.1.1": {
                                                "afi": {
                                                    "ipv4": {
                                                        "Unicast": {
                                                            "allow_as_in": "True",
                                                            "rpl_in": "65001-BGP-IMPORT-V4",
                                                            "rpl_out": "65001-BGP-EXPORT-V4",
                                                        }
                                                    }
                                                },
                                                "description": "FIREWALLs",
                                                "remote_as": "65001",
                                            },
                                            "2.2.2.2": {
                                                "afi": {
                                                    "ipv4": {
                                                        "Unicast": {
                                                            "allow_as_in": "True",
                                                            "rpl_in": "SLB-BGP-IMPORT-V4",
                                                            "rpl_out": "SLB-BGP-EXPORT-V4",
                                                        }
                                                    }
                                                },
                                                "remote_as": "65002",
                                            },
                                            "3.3.3.3": {
                                                "afi": {
                                                    "ipv4": {
                                                        "Unicast": {
                                                            "rpl_in": "INTERNET-IMPORT-V4",
                                                            "rpl_out": "INTERNET-EXPORT-V4",
                                                        }
                                                    }
                                                },
                                                "remote_as": "1234",
                                            },
                                        },
                                    },
                                    "cust2": {
                                        "afi": {
                                            "Unicast": {
                                                "ipv4": {
                                                    "redistr_direct_rpl": "VRF-DIRECT->BGP-V4"
                                                }
                                            }
                                        },
                                        "local_as": "65000",
                                        "peers": {
                                            "4.4.4.4": {
                                                "afi": {
                                                    "ipv4": {
                                                        "Unicast": {
                                                            "allow_as_in": "True",
                                                            "rpl_in": "SLBB-BGP-IMPORT-V4",
                                                            "rpl_out": "SLBB-BGP-EXPORT-V4",
                                                        }
                                                    }
                                                },
                                                "remote_as": "4567",
                                            }
                                        },
                                    },
                                    "cust3": {
                                        "afi": {
                                            "Unicast": {
                                                "ipv4": {
                                                    "redistr_direct_rpl": "C3-DIRECT->BGP-V4"
                                                }
                                            }
                                        },
                                        "local_as": "65000",
                                        "peers": {
                                            "5.5.5.5": {
                                                "afi": {
                                                    "ipv4": {
                                                        "Unicast": {
                                                            "rpl_in": "C3-BGP-IMPORT-V4",
                                                            "rpl_out": "C3-BGP-EXPORT-V4",
                                                        }
                                                    }
                                                },
                                                "remote_as": "65100",
                                            },
                                            "6.6.6.6": {
                                                "afi": {
                                                    "ipv4": {
                                                        "Unicast": {
                                                            "rpl_in": "C3-FW-BGP-IMPORT-V4",
                                                            "rpl_out": "C3-FW-BGP-EXPORT-V4",
                                                        }
                                                    }
                                                },
                                                "remote_as": "65200",
                                            },
                                        },
                                    },
                                }
                            ],
                        }
                    }
                }
            }
        ]
    ]


# test_hierarch_template()


def test_comments_with_indentation():
    """
    Need to manually run this test to see if log message generated:
    WARNING:ttp.ttp:group.get_regexes: variable not found in line: '    ## some comment line'

    it should not, if all working properly
    """
    template = """
    ## some comment line
some string {{ var_1 }}
    """
    parser = ttp(template=template, log_level="warning")


# test_comments_with_indentation()


def test_TTP_CACHE_FOLDER_env_variable_usage():
    """
    Check that TTP_CACHE_FOLDER properly handled when it is set
    """
    template = "some string {{ var_1 }}"
    os.environ["TTP_CACHE_FOLDER"] = "./assets/"
    parser = ttp(template=template)
    assert "ttp_dict_cache.pickle" in os.listdir("./assets/")
    os.remove("./assets/ttp_dict_cache.pickle")
    os.environ.pop("TTP_CACHE_FOLDER", None)
# test_TTP_CACHE_FOLDER_env_variable_usage()    
    

def test_child_group_do_not_start_if_no_parent_started():
    """
    This test tests that this wrong output is not produced:
    [[{'ospf_processes': {'1': {'external_lsa': {'age': '1604'},
                                'local_rid': '10.0.1.1',
                                'router_lsa': [{'age': '406',
                                                'area': 'area',
                                                'originator_rid': '10.0.1.1',
                                                'ptp_peers': [{'link_data': '0.0.0.12'},
                                                            {'link_data': '0.0.0.10'},
                                                            {'link_data': '0.0.0.52'},
                                                            {'link_data': '0.0.0.53'}]}]}}}]]
    Reason wrong output produced is because TTP parses "LS age: {{ age }}" for
    "external_lsa" even though "Type-5 AS External Link States {{ _start_ }}" 
    does not math anything in the output.
    
    Next, once "LS age: 406" like lines matched by two "LS age: {{ age }}"start 
    regexes from "name="router_lsa*" and "name="external_lsa"" groups, selection
    of match result happens in favour of "name="external_lsa"" group and it breaks
    the logic of saving results for "name="ptp_peers*"" group, leading to all
    ptp_ppers saved under same path, and "LS age: 1604" stored under "name="external_lsa""
    wrong path.
    
    The fix is to make sure that group "name="external_lsa"" pattern "LS age: {{ age }}"
    will not be parsed if no "Type-5 AS External Link States {{ _start_ }}" pattern 
    matched in the data text.
    """
    template = """
<group name="ospf_processes.{{ pid }}**">
            OSPF Router with ID ({{ local_rid }}) (Process ID {{ pid }})
            
<group name="router_lsa*" record="area" del="area" void="">
                Router Link States (Area {{ area }})

  <group set="area">
  LS age: {{ age }}
  Advertising Router: {{ originator_rid }}

    <group name="ptp_peers*">
    Link connected to: another Router (point-to-point) {{ _start_ }}
     (Link Data) Router Interface address: {{ link_data }}
    </group>
  </group>
</group>

<group name="external_lsa">
                Type-5 AS External Link States {{ _start_ }}

  <group>
  LS age: {{ age }}
{{ _end_ }}
  </group>
</group>

</group>
    """
    data = """
RP/0/RP0/CPU0:router-1#show ospf database router 

            OSPF Router with ID (10.0.1.1) (Process ID 1)

                Router Link States (Area 0.0.0.0)

  LS age: 406
  Options: (No TOS-capability, DC)
  LS Type: Router Links
  Link State ID: 10.0.1.1
  Advertising Router: 10.0.1.1
  LS Seq Number: 8000010c
  Checksum: 0x24dd
  Length: 132
   Number of Links: 9

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 10.0.1.4
     (Link Data) Router Interface address: 0.0.0.12
      Number of TOS metrics: 0
       TOS 0 Metrics: 1100

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 10.0.1.2
     (Link Data) Router Interface address: 0.0.0.10
      Number of TOS metrics: 0
       TOS 0 Metrics: 1100    
       
  Routing Bit Set on this LSA
  LS age: 1604
  Options: (No TOS-capability, DC)
  LS Type: Router Links
  Link State ID: 10.0.1.2
  Advertising Router: 10.0.1.2
  LS Seq Number: 8000010b
  Checksum: 0xdc96
  Length: 132
   Number of Links: 9

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 10.0.1.3
     (Link Data) Router Interface address: 0.0.0.52
      Number of TOS metrics: 0
       TOS 0 Metrics: 1100

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 10.0.1.4
     (Link Data) Router Interface address: 0.0.0.53
      Number of TOS metrics: 0
       TOS 0 Metrics: 1100
    """
    parser = ttp(data=data, template=template, log_level="warning")    
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'ospf_processes': {'1': {'local_rid': '10.0.1.1',
                                              'router_lsa': [{'age': '406',
                                                              'area': 'area',
                                                              'originator_rid': '10.0.1.1',
                                                              'ptp_peers': [{'link_data': '0.0.0.12'},
                                                                            {'link_data': '0.0.0.10'}]},
                                                             {'age': '1604',
                                                              'area': 'area',
                                                              'originator_rid': '10.0.1.2',
                                                              'ptp_peers': [{'link_data': '0.0.0.52'},
                                                                            {'link_data': '0.0.0.53'}]}]}}}]]
    
# test_child_group_do_not_start_if_no_parent_started()


def test_group_end_indicator_when_last_start_is_bigger_than_last_end():
    """
    Testcase when we have last end span is smaller than last start span, meaning we have
    start matches beyond last end match.
    
    Without fix TTP returns this data:
    [[{'ospf_processes': {'1': {'local_rid': '10.0.0.4',
                                'router_lsa': [{'area': '100',
                                                'asbr': False,
                                                'originator_rid': '10.0.0.4',
                                                'ptp_peers': [{'link_data': '10.1.45.2',
                                                               'link_id': '10.0.5.101',
                                                               'metric': '10'}]},
                                               {'area': '100',
                                                'asbr': True,
                                                'originator_rid': '10.0.5.101',
                                                'ptp_peers': [{}]}]}}}]]
                                                
    ptp_peers did not match any group match regexes, this is due to data does have
    {{ _end_ }} matched before last start
    """
    data = """
IOL4#show ip ospf database router

            OSPF Router with ID (10.0.0.4) (Process ID 1)
            
                Router Link States (Area 100)

  LS Type: Router Links
  Link State ID: 10.0.0.4
  Advertising Router: 10.0.0.4

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 10.0.5.101
     (Link Data) Router Interface address: 10.1.45.2
      Number of MTID metrics: 0
       TOS 0 Metrics: 10

  LS Type: Router Links
  Link State ID: 10.0.5.101
  Advertising Router: 10.0.5.101

    Link connected to: another Router (point-to-point)
     (Link ID) Neighboring Router ID: 10.0.0.4
     (Link Data) Router Interface address: 10.1.45.3
      Number of MTID metrics: 0
       TOS 0 Metrics: 10"""
    template = """
<group name="ospf_processes.{{ pid }}**">
            OSPF Router with ID ({{ local_rid }}) (Process ID {{ pid }})
            
<group name="router_lsa*" functions="record('area') | del('area') | void">
                Router Link States (Area {{ area }}) 
                
  <group set="area">
  LS Type: Router Links {{ _start_ }}
  Advertising Router: {{ originator_rid }}
  AS Boundary Router {{ asbr | set(True) | default(False) }}
  
    <group name="ptp_peers*">
    Link connected to: another Router (point-to-point) {{ _start_ }}
     (Link ID) Neighboring Router ID: {{ link_id }}
     (Link Data) Router Interface address: {{ link_data }}
       TOS 0 Metrics: {{ metric }}
{{ _end_ }}
    </group>

  </group>
</group>
</group>
    """
    parser = ttp(data=data, template=template, log_level="warning")    
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'ospf_processes': {'1': {'local_rid': '10.0.0.4',
                                              'router_lsa': [{'area': '100',
                                                              'asbr': False,
                                                              'originator_rid': '10.0.0.4',
                                                              'ptp_peers': [{'link_data': '10.1.45.2',
                                                                             'link_id': '10.0.5.101',
                                                                             'metric': '10'}]},
                                                             {'area': '100',
                                                              'asbr': False,
                                                              'originator_rid': '10.0.5.101',
                                                              'ptp_peers': [{'link_data': '10.1.45.3',
                                                                             'link_id': '10.0.0.4',
                                                                             'metric': '10'}]}]}}}]]
    
# test_group_end_indicator_when_last_start_is_bigger_than_last_end()