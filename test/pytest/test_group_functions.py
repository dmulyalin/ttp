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


def test_group_macro_returns_false():
    template_123 = """
<input load="text">
interface Lo0
!
interface Lo1
 description this interface has description
</input>

<macro>
def check(data):
    if not "description" in data:
        return False
</macro>

<group macro="check">
interface {{ interface }}
 description {{ description | ORPHRASE }}
</group>
"""
    parser = ttp(template=template_123)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'description': 'this interface has description', 'interface': 'Lo1'}]]]
    
# test_group_macro_returns_false()


def test_group_macro_returns_true():
    template_123 = """
<input load="text">
interface Lo0
!
interface Lo1
 description this interface has description
</input>

<macro>
def check(data):
    if "description" in data:
        return True
</macro>

<group macro="check">
interface {{ interface }}
 description {{ description | ORPHRASE }}
</group>
"""
    parser = ttp(template=template_123)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo0'},
                     {'description': 'this interface has description', 'interface': 'Lo1'}]]]
    
# test_group_macro_returns_true()


def test_group_macro_returns_none():
    template_123 = """
<input load="text">
interface Lo0
!
interface Lo1
 description this interface has description
</input>

<macro>
def check(data):
    return None
</macro>

<group macro="check">
interface {{ interface }}
 description {{ description | ORPHRASE }}
</group>
"""
    parser = ttp(template=template_123)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo0'},
                     {'description': 'this interface has description', 'interface': 'Lo1'}]]]
    
# test_group_macro_returns_none()


def test_group_macro_chaining():
    template_123 = """
<input load="text">
interface Lo0
!
interface Lo1
 description this interface has description
</input>

<macro>
def check_1(data):
    if not "description" in data:
        data["has_description"] = False
    else:
        data["has_description"] = True

def check_2(data):
    if "Lo" in data["interface"]:
        data["is_loopback"] = True
</macro>

<group macro="check_1, check_2">
interface {{ interface }}
 description {{ description | ORPHRASE }}
</group>
"""
    parser = ttp(template=template_123)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'has_description': False, 'interface': 'Lo0', 'is_loopback': True},
                     {'description': 'this interface has description',
                      'has_description': True,
                      'interface': 'Lo1',
                      'is_loopback': True}]]]
    
# test_group_macro_chaining()


def test_group_macro_chaining_returns_dictionary():
    template_123 = """
<input load="text">
interface Lo0
!
interface Lo1
 description this interface has description
</input>

<macro>
def check_1(data):
    if not "description" in data:
        return {"completely_new_data": True}

def check_2(data):
    if "Lo" in data.get("interface", ""):
        data["is_loopback"] = True
    else:
        data.update({"completely_new_data_2": True})
        return data
</macro>

<group macro="check_1, check_2">
interface {{ interface }}
 description {{ description | ORPHRASE }}
</group>
"""
    parser = ttp(template=template_123)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'completely_new_data': True, 'completely_new_data_2': True},
                     {'description': 'this interface has description',
                      'interface': 'Lo1',
                      'is_loopback': True}]]]
    
# test_group_macro_chaining_returns_dictionary()

def test_itemize():
    template = """
<input load="text">
interface Vlan778
 description some description 1
 ip address 2002:fd37::91/124
!
interface Vlan779
 description some description 2
!
interface Vlan780
 switchport port-security mac 4
 ip address 192.168.1.1/124
!
interface Vlan790
 description some description 790
 switchport port-security mac 4
 ip address 192.168.190.1/124
!
</input>

<group name="interfaces_list**" functions="contains('ip') | itemize(key='interface')">
interface {{ interface | upper | append("a") }}
 ip address {{ ip }}
</group>

<group name="ips_list" functions="contains('description') | itemize(key='ip')">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }}
 !{{ _end_ }}
</group>

<group name="bla" functions="contains('ip') | itemize(key='interface', path='interfaces.l3')">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }}
 !{{ _end_ }}
</group>
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'bla': [{'description': 'some description 1',
                              'interface': 'Vlan778',
                              'ip': '2002:fd37::91/124'},
                             {'interface': 'Vlan780', 'ip': '192.168.1.1/124'},
                             {'description': 'some description 790',
                              'interface': 'Vlan790',
                              'ip': '192.168.190.1/124'}],
                     'interfaces': {'l3': ['Vlan778', 'Vlan780', 'Vlan790']},
                     'interfaces_list': ['VLAN778a', 'VLAN780a', 'VLAN790a'],
                     'ips_list': ['2002:fd37::91/124', '192.168.190.1/124']}]]
   
# test_itemize()


def test_itemize_dynamic_path():
    template = """
<input load="text">
interface Loopback0
 ip address 2002:fd37::91/124
!
interface Vlan779
!
interface Loopback1
 switchport port-security mac 4
 ip address 192.168.1.1/124
!
interface Vlan790
 switchport port-security mac 4
 ip address 192.168.190.1/124
!
</input>

<group name="l3_interfaces_list.{{ intf_type }}" itemize="interface">
interface {{ interface | contains("Vlan") | let("intf_type", "vlans") }}
 ip address {{ ip }}
</group>

<group name="l3_interfaces_list.{{ intf_type }}" itemize="interface">
interface {{ interface | contains("Loop") | let("intf_type", "loopbacks") }}
 ip address {{ ip }}
</group>
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'l3_interfaces_list': {'loopbacks': ['Loopback0', 'Loopback1'],
                                            'vlans': ['Vlan779', 'Vlan790']}}]]     

# test_itemize_dynamic_path()

def test_itemize_dynamic_path_attribute():
    template = """
<input load="text">
interface Loopback0
 ip address 2002:fd37::91/124
!
interface Vlan779
!
interface Loopback1
 switchport port-security mac 4
 ip address 192.168.1.1/124
!
interface Vlan790
 switchport port-security mac 4
 ip address 192.168.190.1/124
!
</input>

<group name="interfaces" itemize="interface, 'l3_interfaces_list.{{ intf_type }}'">
interface {{ interface | contains("Vlan") | let("intf_type", "vlans") }}
 ip address {{ ip }}
</group>

<group name="interfaces" itemize="interface, 'l3_interfaces_list.{{ intf_type }}'">
interface {{ interface | contains("Loop") | let("intf_type", "loopbacks") }}
 ip address {{ ip }}
</group>
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'interfaces': [{'interface': 'Vlan779'},
                                    {'interface': 'Vlan790', 'ip': '192.168.190.1/124'},
                                    {'interface': 'Loopback0', 'ip': '2002:fd37::91/124'},
                                    {'interface': 'Loopback1', 'ip': '192.168.1.1/124'}],
                     'l3_interfaces_list': {'loopbacks': ['Loopback0', 'Loopback1'],
                                            'vlans': ['Vlan779', 'Vlan790']}}]] 

# test_itemize_dynamic_path_attribute()