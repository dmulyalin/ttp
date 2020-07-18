import sys
sys.path.insert(0,'../..')

from ttp import ttp

template_1 = """
<input load="text">
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32
</input>

<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>
"""

template_2 = """
<template>

<template name="first">
<input load="text">
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32
</input>

<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>

</template>

<template name="second">
<input load="text">
interface Lo2
 ip address 124.171.238.50 32
!
interface Lo3
 description this interface has description
 ip address 2.2.2.2 32
</input>

<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>
</template>
</template>
"""
    
def test_clear_result_all():
    parser = ttp(template=template_1)
    parser.parse()
    parser.clear_result()
    assert parser.result() == [[]] 
    
def test_clear_result_by_name():
    parser = ttp(template=template_2, log_level="info")
    parser.parse()
    parser.clear_result(templates=["first"])
    second_template_expected_tesult = [[[{'ip': '124.171.238.50', 'mask': '32', 'interface': 'Lo2'}, {'ip': '2.2.2.2', 'mask': '32', 'description': 'this interface has description', 'interface': 'Lo3'}]]]
    assert parser.result(templates="first") == [[]] 
    assert parser.result(templates="second") == second_template_expected_tesult 
