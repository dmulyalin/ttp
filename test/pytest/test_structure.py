import sys
sys.path.insert(0,'../..')

from ttp import ttp

template_1 = """
<input load="text">
interface Lo0
 ip address 192.168.0.1 32
!
interface Lo1
 ip address 1.1.1.1 32
</input>

<input load="text">
interface Lo2
 ip address 2.2.2.2 32
!
interface Lo3
 ip address 3.3.3.3 32
</input>

<group>
interface {{ interface }}
 ip address {{ ip }} {{ mask }}
</group>
"""

template_2 =  """
<template>

<template name="first">
<input load="text">
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 ip address 1.1.1.1 32
</input>

<group>
interface {{ interface }}
 ip address {{ ip }} {{ mask }}
</group>

</template>

<template name="second">
<input load="text">
interface Lo2
 ip address 124.171.238.50 32
!
interface Lo3
 ip address 2.2.2.2 32
</input>

<group>
interface {{ interface }}
 ip address {{ ip }} {{ mask }}
</group>
</template>
</template>
"""


list_structure = [[[{'interface': 'Lo0', 'ip': '192.168.0.1', 'mask': '32'},
                    {'interface': 'Lo1', 'ip': '1.1.1.1', 'mask': '32'}],
                   [{'interface': 'Lo2', 'ip': '2.2.2.2', 'mask': '32'},
                    {'interface': 'Lo3', 'ip': '3.3.3.3', 'mask': '32'}]]]
                         
dictionary_structure = {'first': [[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                                   {'interface': 'Lo1', 'ip': '1.1.1.1', 'mask': '32'}]],
                        'second': [[{'interface': 'Lo2', 'ip': '124.171.238.50', 'mask': '32'},
                                    {'interface': 'Lo3', 'ip': '2.2.2.2', 'mask': '32'}]]}
                                    
flat_list_structure = [{'interface': 'Lo0', 'ip': '192.168.0.1', 'mask': '32'},
                       {'interface': 'Lo1', 'ip': '1.1.1.1', 'mask': '32'},
                       {'interface': 'Lo2', 'ip': '2.2.2.2', 'mask': '32'},
                       {'interface': 'Lo3', 'ip': '3.3.3.3', 'mask': '32'}]

def test_list_structure():
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    assert res == list_structure
    
def test_list_structure_with_outputter():
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result(returner="self")
    assert res == list_structure
    
def test_dictionary_structure():
    parser = ttp(template=template_2)
    parser.parse()
    res = parser.result(structure="dictionary")
    assert res == dictionary_structure
    
def test_dictionary_structure_with_outputter():
    parser = ttp(template=template_2)
    parser.parse()
    res = parser.result(structure="dictionary", returner="self")
    assert res == dictionary_structure
    
def test_flat_list_structure():
    parser = ttp(template=template_1)
    parser.parse()
    # just return the results
    res = parser.result(structure="flat_list")
    assert res == flat_list_structure
    
def test_flat_list_structure_with_outputter():
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result(structure="flat_list", returner="self")
    assert res == flat_list_structure