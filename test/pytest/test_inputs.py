import sys
sys.path.insert(0,'../..')
import pprint
import logging

logging.basicConfig(level=logging.DEBUG)

from ttp import ttp

def test_inputs_url_filters_extensions():
    template = """
<input name="in_1">
groups="in_1_group"
url = "./mock_data/dataset_1/"
filters = r"data_\\d"
</input>

<input name="in_2" groups="in_2_group">
url = "./mock_data/dataset_2/"
extensions = ["log"]
</input>

<group name="in_1_group">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {[ ip }} {{ mask }}    
</group>

<group name="in_2_group" input="in_2">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {[ ip }} {{ mask }}    
</group>
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'in_1_group': [{'description': 'data_1 file', 'interface': 'Lo0'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo1'}]},
                    {'in_1_group': [{'description': 'data-2 file', 'interface': 'Lo2'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo3'}]},
                    {'in_2_group': [{'description': 'data_1.log file', 'interface': 'Lo0'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo1'}]}]]
    
# test_inputs_url_filters_extensions()

def test_group_inputs():
    template = """
<input name="in_1">
groups="in_1_group"
url = "./mock_data/dataset_1/"
filters = r"data_\\d"
</input>

<input name="in_2" load="yaml">
url: "./mock_data/dataset_2/"
extensions: ["log"]
</input>

<group name="interfaces" input="in_1">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {[ ip }} {{ mask }}    
</group>

<group name="interfaces" input="in_2">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {[ ip }} {{ mask }}    
</group>
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'interfaces': [{'description': 'data_1 file', 'interface': 'Lo0'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo1'}]},
                    {'interfaces': [{'description': 'data-2 file', 'interface': 'Lo2'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo3'}]},
                    {'interfaces': [{'description': 'data_1.log file', 'interface': 'Lo0'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo1'}]}]]
    
# test_group_inputs()

def test_inputs_with_template_base_path():
    template = """
<template base_path="./mock_data/">

<input name="in_1">
groups="in_1_group"
url = "/dataset_1/"
filters = r"data_\\d"
</input>

<input name="in_2" load="yaml">
url: "/dataset_2/"
extensions: ["log"]
</input>

<group name="interfaces" input="in_1">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {[ ip }} {{ mask }}    
</group>

<group name="interfaces" input="in_2">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {[ ip }} {{ mask }}    
</group>

</template>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'interfaces': [{'description': 'data_1 file', 'interface': 'Lo0'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo1'}]},
                    {'interfaces': [{'description': 'data-2 file', 'interface': 'Lo2'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo3'}]},
                    {'interfaces': [{'description': 'data_1.log file', 'interface': 'Lo0'},
                                    {'description': 'this interface has description',
                                     'interface': 'Lo1'}]}]]
    
# test_inputs_with_template_base_path()

def test_input_to_groups_mapping():
    template = """
<input name="sys_host" load="text">
 Static hostname: localhost.localdomain
         Chassis: vm
      Machine ID: 2a26648f68764152a772fc20c9a3ddb3
Operating System: CentOS Linux 7 (Core)
</input>
    
<group name="system">
 Static hostname: {{ hostname }}
         Chassis: {{ chassis }}
      Machine ID: {{ machine_id }}
Operating System: {{ os | ORPHRASE }}
</group>
    """
    parser = ttp(template=template)
    # import ipdb; ipdb.set_trace()
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'system': {'chassis': 'vm',
                                'hostname': 'localhost.localdomain',
                                'machine_id': '2a26648f68764152a772fc20c9a3ddb3',
                                'os': 'CentOS Linux 7 (Core)'}}]]
                            def test_input_to_groups_mapping():
    template = """
<input name="sys_host" load="text">
 Static hostname: localhost.localdomain
         Chassis: vm
      Machine ID: 2a26648f68764152a772fc20c9a3ddb3
Operating System: CentOS Linux 7 (Core)
</input>
    
<group name="system">
 Static hostname: {{ hostname }}
         Chassis: {{ chassis }}
      Machine ID: {{ machine_id }}
Operating System: {{ os | ORPHRASE }}
</group>
    """
    parser = ttp(template=template)
    # import ipdb; ipdb.set_trace()
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'system': {'chassis': 'vm',
                                'hostname': 'localhost.localdomain',
                                'machine_id': '2a26648f68764152a772fc20c9a3ddb3',
                                'os': 'CentOS Linux 7 (Core)'}}]]
                                
# test_input_to_groups_mapping()