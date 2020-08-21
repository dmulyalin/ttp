import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

def test_simple_anonymous_template():
    template_1 = """interface {{ interface }}
  description {{ description | ORPHRASE }}"""

    data_1 = """
interface Port-Chanel11
  description Storage Management
interface Loopback0
  description RID
"""
    parser = ttp(template=template_1, data=data_1)
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}
    # pprint.pprint(datums_added)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    # assert res == [[[{'description': 'Storage Management', 'interface': 'Port-Chanel11'}, {'description': 'RID', 'interface': 'Loopback0'}]]]
    
# test_simple_anonymous_template()

def test_anonymous_group_with_vars():
    template = """
<input load="text">
interface Port-Chanel11
  description Storage Management
interface Loopback0
  description RID
</input>

<vars name="my.var.s">
a = 1
b = 2
</vars>

<group>
interface {{ interface }}
  description {{ description | ORPHRASE }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'description': 'Storage Management', 'interface': 'Port-Chanel11'},
   {'description': 'RID', 'interface': 'Loopback0'},
   {'my': {'var': {'s': {'a': 1, 'b': 2}}}}]]]
   
# test_anonymous_group_with_vars()