import sys

sys.path.insert(0, "../..")
import pprint
from ttp import ttp
import logging

logging.basicConfig(level=logging.DEBUG)


def test_group_validate_function():
    template_123 = """
<input load="text">
device-1#
interface Lo0
!
interface Lo1
 description this interface has description
</input>

<input load="text">
device-2#
interface Lo10
!
interface Lo11
 description another interface with description
</input>

<vars>
intf_description_validate = {
    'description': {'required': True, 'type': 'string'}
}
hostname_1="gethostname"
</vars>

<group validate="intf_description_validate, info='{interface} has description', result='validation_result', errors='err_details'">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 {{ hostname | set(hostname_1) }}
</group>
"""
    parser = ttp(template=template_123)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "err_details": {"description": ["required field"]},
                    "hostname": "device-1",
                    "info": "Lo0 has description",
                    "interface": "Lo0",
                    "validation_result": False,
                },
                {
                    "description": "this interface has description",
                    "err_details": {},
                    "hostname": "device-1",
                    "info": "Lo1 has description",
                    "interface": "Lo1",
                    "validation_result": True,
                },
            ],
            [
                {
                    "err_details": {"description": ["required field"]},
                    "hostname": "device-2",
                    "info": "Lo10 has description",
                    "interface": "Lo10",
                    "validation_result": False,
                },
                {
                    "description": "another interface with description",
                    "err_details": {},
                    "hostname": "device-2",
                    "info": "Lo11 has description",
                    "interface": "Lo11",
                    "validation_result": True,
                },
            ],
        ]
    ]


# test_group_validate_function()


def test_group_default_referencing_variable_parent_group_no_re_two_inputs():
    template_123 = """
<input load="text">
Hi World
</input>

<input load="text">
Hello World
</input>

<vars>
var_name = {"audiences": []}
</vars>

<group name='demo**' default="var_name">
<group name='audiences*'>
Hello {{ audience }}
</group>
</group>
"""
    parser = ttp(template=template_123, log_level="WARNING")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [{"demo": {"audiences": []}}, {"demo": {"audiences": [{"audience": "World"}]}}]
    ]


# test_group_default_referencing_variable_parent_group_no_re_two_inputs()


def test_group_default_referencing_variable_parent_group_no_re_one_input():
    template_123 = """
<input load="text">
Hi World
</input>

<vars>
var_name = {"audiences": []}
</vars>

<group name='demo' default="var_name">
<group name='audiences*'>
Hello {{ audience }}
</group>
</group>
"""
    parser = ttp(template=template_123, log_level="WARNING")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{"demo": {"audiences": []}}]]


def test_top_group_default_referencing_variable_dictionary():
    template_123 = """
<input load="text">
device-1#
interface Lo0
!
interface Lo1
 description this interface has description
</input>

<input load="text">
device-2#
interface Lo10
!
interface Lo11
 description another interface with description
</input>

<vars>
var_name = {
    "switchport": False,
    "is_l3": True,
    "description": "Undefined"
}
</vars>

<group name="interfaces" default="var_name">
interface {{ interface }}
 description {{ description | ORPHRASE }}
</group>
"""
    parser = ttp(template=template_123, log_level="DEBUG")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "interfaces": [
                    {
                        "description": "Undefined",
                        "interface": "Lo0",
                        "is_l3": True,
                        "switchport": False,
                    },
                    {
                        "description": "this interface has description",
                        "interface": "Lo1",
                        "is_l3": True,
                        "switchport": False,
                    },
                ]
            },
            {
                "interfaces": [
                    {
                        "description": "Undefined",
                        "interface": "Lo10",
                        "is_l3": True,
                        "switchport": False,
                    },
                    {
                        "description": "another interface with description",
                        "interface": "Lo11",
                        "is_l3": True,
                        "switchport": False,
                    },
                ]
            },
        ]
    ]


# test_top_group_default_referencing_variable_dictionary()


def test_group_default():
    template = """
<input load="text">
device-hostame uptime is 27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds
</input>

<group name="uptime**">
device-hostame uptime is {{ uptime | PHRASE }}
<group name="software">
 software version {{ version | default("uncknown") }}
</group>
</group>

<group name="domain" default="Uncknown">
Default domain is {{ fqdn }}
</group>
    """
    parser = ttp(template=template, log_level="WARNING")
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [
        [
            {
                "domain": {"fqdn": "Uncknown"},
                "uptime": {
                    "software": {"version": "uncknown"},
                    "uptime": "27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds",
                },
            }
        ]
    ]


# test_group_default()


def test_child_group_default_referencing_variable():
    template_123 = """
<input load="text">
interface Lo0
 ip address 1.1.1.1 255.255.255.255
!
interface Lo1
 description this interface has description
</input>

<input load="text">
interface Lo10
 ip address 1.1.1.2 255.255.255.255
!
interface Lo11
 description another interface with description
 ip address 1.1.1.3 255.255.255.255
</input>

<vars>
var_name = {
    "L3": True,
    "has_ip": True
}
</vars>

<group name="interfaces">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 <group name="IPv4_addresses" default="var_name">
 ip address {{ IP }} {{ MASK }}
 </group>
</group>
"""
    parser = ttp(template=template_123, log_level="WARNING")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "interfaces": [
                    {
                        "IPv4_addresses": {
                            "IP": "1.1.1.1",
                            "L3": True,
                            "MASK": "255.255.255.255",
                            "has_ip": True,
                        },
                        "interface": "Lo0",
                    },
                    {
                        "description": "this interface has description",
                        "interface": "Lo1",
                    },
                ]
            },
            {
                "interfaces": [
                    {
                        "IPv4_addresses": {
                            "IP": "1.1.1.2",
                            "L3": True,
                            "MASK": "255.255.255.255",
                            "has_ip": True,
                        },
                        "interface": "Lo10",
                    },
                    {
                        "IPv4_addresses": {
                            "IP": "1.1.1.3",
                            "L3": True,
                            "MASK": "255.255.255.255",
                            "has_ip": True,
                        },
                        "description": "another interface with description",
                        "interface": "Lo11",
                    },
                ]
            },
        ]
    ]


# test_child_group_default_referencing_variable()


def test_group_set_function_source_from_global_vars():
    template_123 = """
<input name="cfg" load="text">
hostname router_1
</input>

<input name="intf" load="text">
interface Lo0
 ip address 1.1.1.1 255.255.255.255
!
interface Lo0
 ip address 1.1.1.2 255.255.255.255
</input>

<group input="cfg" record="hostname">
hostname {{ hostname }}
</group>

<group name="interfaces" set="hostname" input="intf">
interface {{ interface }}
 ip address {{ IP }} {{ MASK }}
</group>
"""
    parser = ttp(template=template_123, log_level="WARNING")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [{"hostname": "router_1"}],
            {
                "interfaces": [
                    {
                        "IP": "1.1.1.1",
                        "MASK": "255.255.255.255",
                        "hostname": "router_1",
                        "interface": "Lo0",
                    },
                    {
                        "IP": "1.1.1.2",
                        "MASK": "255.255.255.255",
                        "hostname": "router_1",
                        "interface": "Lo0",
                    },
                ]
            },
        ]
    ]


# test_group_set_function_source_from_global_vars()
