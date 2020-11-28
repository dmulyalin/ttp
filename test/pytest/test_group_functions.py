import sys
sys.path.insert(0,'../..')
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
    assert res == [[[{'err_details': {'description': ['required field']},
                      'hostname': 'device-1',
                      'info': 'Lo0 has description',
                      'interface': 'Lo0',
                      'validation_result': False},
                     {'description': 'this interface has description',
                      'err_details': {},
                      'hostname': 'device-1',
                      'info': 'Lo1 has description',
                      'interface': 'Lo1',
                      'validation_result': True}],
                    [{'err_details': {'description': ['required field']},
                      'hostname': 'device-2',
                      'info': 'Lo10 has description',
                      'interface': 'Lo10',
                      'validation_result': False},
                     {'description': 'another interface with description',
                      'err_details': {},
                      'hostname': 'device-2',
                      'info': 'Lo11 has description',
                      'interface': 'Lo11',
                      'validation_result': True}]]]
    
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
    assert res == [[{'demo': {'audiences': []}},
                    {'demo': {'audiences': [{'audience': 'World'}]}}]]
    
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
    assert res == [[{'demo': {'audiences': []}}]]
    

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
    assert res == [[{'interfaces': [{'description': 'Undefined',
                                      'interface': 'Lo0',
                                      'is_l3': True,
                                      'switchport': False},
                                     {'description': 'this interface has description',
                                      'interface': 'Lo1',
                                      'is_l3': True,
                                      'switchport': False}]},
                     {'interfaces': [{'description': 'Undefined',
                                      'interface': 'Lo10',
                                      'is_l3': True,
                                      'switchport': False},
                                     {'description': 'another interface with description',
                                      'interface': 'Lo11',
                                      'is_l3': True,
                                      'switchport': False}]}]]
                   
# test_top_group_default_referencing_variable_dictionary()

def test_child_group_default_referencing_variable_dictionary():
    template_123 = """
<input load="text">
device-1#
interface Lo0
 ip address 1.1.1.1 255.255.255.255
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
    "IP": False,
	"MASK": False
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
    parser = ttp(template=template_123, log_level="DEBUG")
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
	
test_child_group_default_referencing_variable_dictionary()