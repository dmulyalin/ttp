import sys
sys.path.insert(0,'../..')
import pprint
from ttp import ttp

def test_group_validate_function():
    template = """
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
hostname="gethostname"
</vars>

<group validate="intf_description_validate, info='{interface} has description', result='validation_result', errors='err_details'">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 {{ hostname | set(hostname) }}
</group>
"""
    parser = ttp(template=template)
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
    
# test_group_chain_attribute_list()