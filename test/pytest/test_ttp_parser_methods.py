import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

import logging
logging.basicConfig(level=logging.ERROR)


def test_clear_result_all():
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
    parser = ttp(template=template_1)
    parser.parse()
    parser.clear_result()
    assert parser.result() == [[]] 
    
def test_clear_result_by_name():
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
    parser = ttp(template=template_2)
    parser.parse()
    parser.clear_result(templates=["first"])
    second_template_expected_tesult = [[[{'ip': '124.171.238.50', 'mask': '32', 'interface': 'Lo2'}, {'ip': '2.2.2.2', 'mask': '32', 'description': 'this interface has description', 'interface': 'Lo3'}]]]
    assert parser.result(templates="first") == [[]] 
    assert parser.result(templates="second") == second_template_expected_tesult 

def test_add_input_with_default_options():
    data_1 = """
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32    
"""
    data_2 = """
interface Lo2
 ip address 124.171.238.22 32
!
interface Lo3
 description this interface has description
 ip address 2.2.2.2 32    
"""
    template_1 = """
<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
"""
    parser = ttp(template=template_1)
    parser.add_input(data_1, input_name='Default_Input', template_name="_root_template_", groups=['all'])
    parser.add_input(data_2, input_name='Default_Input', template_name="_root_template_", groups=['all'])
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}
    # pprint.pprint(datums_added)
    assert datums_added == {'_root_template_:Default_Input': [('text_data',
                                                               '\n'
                                                               'interface Lo0\n'
                                                               ' ip address 124.171.238.50 32\n'
                                                               '!\n'
                                                               'interface Lo1\n'
                                                               ' description this interface has '
                                                               'description\n'
                                                               ' ip address 1.1.1.1 32    \n'),
                                                              ('text_data',
                                                               '\n'
                                                               'interface Lo2\n'
                                                               ' ip address 124.171.238.22 32\n'
                                                               '!\n'
                                                               'interface Lo3\n'
                                                               ' description this interface has '
                                                               'description\n'
                                                               ' ip address 2.2.2.2 32    \n')]}
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo1',
                      'ip': '1.1.1.1',
                      'mask': '32'}],
                    [{'interface': 'Lo2', 'ip': '124.171.238.22', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo3',
                      'ip': '2.2.2.2',
                      'mask': '32'}]]]
    

def test_add_input_to_non_existing_template():
    data_1 = """
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32    
"""
    data_2 = """
interface Lo2
 ip address 124.171.238.22 32
!
interface Lo3
 description this interface has description
 ip address 2.2.2.2 32    
"""
    template_1 = """
<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
"""
    parser = ttp(template=template_1)
    parser.add_input(data_1, input_name='Default_Input', template_name="_root_template_", groups=['all'])
    parser.add_input(data_2, input_name='Default_Input', template_name="does_not_exists", groups=['all'])
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}
    # pprint.pprint(datums_added)
    assert datums_added == {'_root_template_:Default_Input': [('text_data',
                                                               '\n'
                                                               'interface Lo0\n'
                                                               ' ip address 124.171.238.50 32\n'
                                                               '!\n'
                                                               'interface Lo1\n'
                                                               ' description this interface has '
                                                               'description\n'
                                                               ' ip address 1.1.1.1 32    \n')]}
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo1',
                      'ip': '1.1.1.1',
                      'mask': '32'}]]]


def test_add_input_to_non_default_root_template():
    data_1 = """
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32    
"""
    data_2 = """
interface Lo2
 ip address 124.171.238.22 32
!
interface Lo3
 description this interface has description
 ip address 2.2.2.2 32    
"""
    template_1 = """
<template name="template_1">
<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
</template>
"""
    parser = ttp(template=template_1)
    parser.add_input(data_1, input_name='Default_Input', template_name="_root_template_", groups=['all'])
    parser.add_input(data_2, input_name='Default_Input', template_name="template_1", groups=['all'])
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}
    # pprint.pprint(datums_added)
    assert datums_added == {'template_1:Default_Input': [('text_data',
                                                          '\n'
                                                          'interface Lo2\n'
                                                          ' ip address 124.171.238.22 32\n'
                                                          '!\n'
                                                          'interface Lo3\n'
                                                          ' description this interface has description\n'
                                                          ' ip address 2.2.2.2 32    \n')]}
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo2', 'ip': '124.171.238.22', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo3',
                      'ip': '2.2.2.2',
                      'mask': '32'}]]]


def test_add_inputs_to_child_templates_default_input():
    data_1 = """
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32    
"""
    data_2 = """
interface Lo2
 ip address 124.171.238.22 32
!
interface Lo3
 description this interface has description
 ip address 2.2.2.2 32    
"""
    data_3 = """
interface Lo4
 ip address 124.171.238.33 32
!
interface Lo5
 description this interface has description
 ip address 3.3.3.3 32    
"""
    template_1 = """
<template name="template_1">
<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
</template>

<template name="template_2">
<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
</template>
"""
    parser = ttp(template=template_1)
    parser.add_input(data_1, input_name='Default_Input', template_name="template_1", groups=['all'])
    parser.add_input(data_2, input_name='Default_Input', template_name="template_2", groups=['all'])
    parser.add_input(data_3, input_name='Default_Input', template_name="template_2", groups=['all'])
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}
    # pprint.pprint(datums_added)
    assert datums_added == {'template_1:Default_Input': [('text_data',
                                                          '\n'
                                                          'interface Lo0\n'
                                                          ' ip address 124.171.238.50 32\n'
                                                          '!\n'
                                                          'interface Lo1\n'
                                                          ' description this interface has description\n'
                                                          ' ip address 1.1.1.1 32    \n')],
                            'template_2:Default_Input': [('text_data',
                                                          '\n'
                                                          'interface Lo2\n'
                                                          ' ip address 124.171.238.22 32\n'
                                                          '!\n'
                                                          'interface Lo3\n'
                                                          ' description this interface has description\n'
                                                          ' ip address 2.2.2.2 32    \n'),
                                                         ('text_data',
                                                          '\n'
                                                          'interface Lo4\n'
                                                          ' ip address 124.171.238.33 32\n'
                                                          '!\n'
                                                          'interface Lo5\n'
                                                          ' description this interface has description\n'
                                                          ' ip address 3.3.3.3 32    \n')]}
    parser.parse()
    dict_res = parser.result(structure="dictionary")
    # pprint.pprint(dict_res)
    assert dict_res == {'template_1': [[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                 {'description': 'this interface has description',
                  'interface': 'Lo1',
                  'ip': '1.1.1.1',
                  'mask': '32'}]],
 'template_2': [[{'interface': 'Lo2', 'ip': '124.171.238.22', 'mask': '32'},
                 {'description': 'this interface has description',
                  'interface': 'Lo3',
                  'ip': '2.2.2.2',
                  'mask': '32'}],
                [{'interface': 'Lo4', 'ip': '124.171.238.33', 'mask': '32'},
                 {'description': 'this interface has description',
                  'interface': 'Lo5',
                  'ip': '3.3.3.3',
                  'mask': '32'}]]}
    flat_list_res = parser.result(structure="flat_list")
    # pprint.pprint(flat_list_res)
    assert flat_list_res == [{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
 {'description': 'this interface has description',
  'interface': 'Lo1',
  'ip': '1.1.1.1',
  'mask': '32'},
 {'interface': 'Lo2', 'ip': '124.171.238.22', 'mask': '32'},
 {'description': 'this interface has description',
  'interface': 'Lo3',
  'ip': '2.2.2.2',
  'mask': '32'},
 {'interface': 'Lo4', 'ip': '124.171.238.33', 'mask': '32'},
 {'description': 'this interface has description',
  'interface': 'Lo5',
  'ip': '3.3.3.3',
  'mask': '32'}]
      

def test_add_inputs_to_child_templates_non_default_input():
    data_1 = """
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32    
"""
    data_2 = """
interface Lo2
 ip address 124.171.238.22 32
!
interface Lo3
 description this interface has description
 ip address 2.2.2.2 32    
"""
    data_3 = """
interface Lo4
 ip address 124.171.238.33 32
!
interface Lo5
 description this interface has description
 ip address 3.3.3.3 32    
"""
    template_1 = """
<template name="template_1">
<input name="input1"/>
<group input="input1">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
</template>

<template name="template_2">
<input name="input2"/>
<group input="input2">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
</template>
"""
    parser = ttp(template=template_1)
    parser.add_input(data_1, input_name='input1', template_name="template_1", groups=['all'])
    parser.add_input(data_2, input_name='input2', template_name="template_2", groups=['all'])
    parser.add_input(data_3, input_name='input2', template_name="template_2", groups=['all'])
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}   
    # pprint.pprint(datums_added)
    assert datums_added == {'template_1:input1': [('text_data',
                                                   '\n'
                                                   'interface Lo0\n'
                                                   ' ip address 124.171.238.50 32\n'
                                                   '!\n'
                                                   'interface Lo1\n'
                                                   ' description this interface has description\n'
                                                   ' ip address 1.1.1.1 32    \n')],
                            'template_2:input2': [('text_data',
                                                   '\n'
                                                   'interface Lo2\n'
                                                   ' ip address 124.171.238.22 32\n'
                                                   '!\n'
                                                   'interface Lo3\n'
                                                   ' description this interface has description\n'
                                                   ' ip address 2.2.2.2 32    \n'),
                                                  ('text_data',
                                                   '\n'
                                                   'interface Lo4\n'
                                                   ' ip address 124.171.238.33 32\n'
                                                   '!\n'
                                                   'interface Lo5\n'
                                                   ' description this interface has description\n'
                                                   ' ip address 3.3.3.3 32    \n')]}
    parser.parse()
    dict_res = parser.result(structure="dictionary")
    # pprint.pprint(dict_res)
    assert dict_res == {'template_1': [[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                 {'description': 'this interface has description',
                  'interface': 'Lo1',
                  'ip': '1.1.1.1',
                  'mask': '32'}]],
 'template_2': [[{'interface': 'Lo2', 'ip': '124.171.238.22', 'mask': '32'},
                 {'description': 'this interface has description',
                  'interface': 'Lo3',
                  'ip': '2.2.2.2',
                  'mask': '32'}],
                [{'interface': 'Lo4', 'ip': '124.171.238.33', 'mask': '32'},
                 {'description': 'this interface has description',
                  'interface': 'Lo5',
                  'ip': '3.3.3.3',
                  'mask': '32'}]]}


def test_set_input_for_child_template():
    data_1 = """
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32    
"""
    data_2 = """
interface Lo2
 ip address 124.171.238.22 32
!
interface Lo3
 description this interface has description
 ip address 2.2.2.2 32    
"""
    data_3 = """
interface Lo4
 ip address 124.171.238.33 32
!
interface Lo5
 description this interface has description
 ip address 3.3.3.3 32    
"""
    template_1 = """
<template name="template_1">
<input name="input1"/>
<group input="input1">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
</template>

<template name="template_2">
<input name="input2"/>
<group input="input2">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>    
</template>
"""
    parser = ttp(template=template_1)
    # parse first set of data
    parser.add_input(data_1, input_name='input1', template_name="template_1", groups=['all'])
    parser.add_input(data_2, input_name='input2', template_name="template_2", groups=['all'])
    parser.parse()
    dict_res_first = parser.result(structure="dictionary")
    # pprint.pprint(dict_res_first)
    assert dict_res_first == {'template_1': [[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                                              {'description': 'this interface has description',
                                               'interface': 'Lo1',
                                               'ip': '1.1.1.1',
                                               'mask': '32'}]],
                              'template_2': [[{'interface': 'Lo2', 'ip': '124.171.238.22', 'mask': '32'},
                                              {'description': 'this interface has description',
                                               'interface': 'Lo3',
                                               'ip': '2.2.2.2',
                                               'mask': '32'}]]}
    # parse second set of data
    parser.clear_result()
    parser.set_input(data_2, input_name='input1', template_name="template_1", groups=['all'])
    parser.set_input(data_3, input_name='input2', template_name="template_2", groups=['all'])
    parser.parse()
    dict_res_second = parser.result(structure="dictionary")
    # pprint.pprint(dict_res_second)
    assert dict_res_second == {'template_1': [[{'interface': 'Lo2', 'ip': '124.171.238.22', 'mask': '32'},
                                               {'description': 'this interface has description',
                                                'interface': 'Lo3',
                                                'ip': '2.2.2.2',
                                                'mask': '32'}]],
                               'template_2': [[{'interface': 'Lo4', 'ip': '124.171.238.33', 'mask': '32'},
                                               {'description': 'this interface has description',
                                                'interface': 'Lo5',
                                                'ip': '3.3.3.3',
                                                'mask': '32'}]]}
    
def test_add_template():
    data_1 = """
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32    
"""
    data_2 = """
interface Lo2
 ip address 124.171.238.22 32
!
interface Lo3
 description this interface has description
 ip address 2.2.2.2 32    
"""
    template_1 = """
<template name="template_1_name">
<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
 {{ template | set(template_1_name) }}
</group>    
</template>
"""    
    template_2 = """
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
"""
    parser = ttp()
    parser.add_template(template_1)
    parser.add_template(template_2)
    parser.add_input(data_1)
    parser.add_input(data_2, template_name="template_1_name")
    parser.add_input(data_2)
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}   
    # pprint.pprint(datums_added)
    assert datums_added == {'_root_template_:Default_Input': [('text_data',
                                                               '\n'
                                                               'interface Lo0\n'
                                                               ' ip address 124.171.238.50 32\n'
                                                               '!\n'
                                                               'interface Lo1\n'
                                                               ' description this interface has '
                                                               'description\n'
                                                               ' ip address 1.1.1.1 32    \n'),
                                                              ('text_data',
                                                               '\n'
                                                               'interface Lo2\n'
                                                               ' ip address 124.171.238.22 32\n'
                                                               '!\n'
                                                               'interface Lo3\n'
                                                               ' description this interface has '
                                                               'description\n'
                                                               ' ip address 2.2.2.2 32    \n')],
                            'template_1_name:Default_Input': [('text_data',
                                                               '\n'
                                                               'interface Lo2\n'
                                                               ' ip address 124.171.238.22 32\n'
                                                               '!\n'
                                                               'interface Lo3\n'
                                                               ' description this interface has '
                                                               'description\n'
                                                               ' ip address 2.2.2.2 32    \n')]}
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo2',
                      'ip': '124.171.238.22',
                      'mask': '32',
                      'template': 'template_1_name'},
                     {'description': 'this interface has description',
                      'interface': 'Lo3',
                      'ip': '2.2.2.2',
                      'mask': '32',
                      'template': 'template_1_name'}]],
                   [[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo1',
                      'ip': '1.1.1.1',
                      'mask': '32'}],
                    [{'interface': 'Lo2', 'ip': '124.171.238.22', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo3',
                      'ip': '2.2.2.2',
                      'mask': '32'}]]]
    
    
def test_adding_data_from_files():
    template_1 = """
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
"""
    parser = ttp(template=template_1)
    parser.add_input(data="./mock_data/dataset_1/")
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}   
    # pprint.pprint(datums_added)    
    assert datums_added == {'_root_template_:Default_Input': [('file_name',
                                    './mock_data/dataset_1/data_1.txt'),
                                   ('file_name',
                                    './mock_data/dataset_1/data_2.txt'),
                                   ('file_name',
                                    './mock_data/dataset_1/data_XYZ.txt')]}
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'description': 'data_1 file',
                      'interface': 'Lo0',
                      'ip': '1.0.0.0',
                      'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo1',
                      'ip': '1.1.1.1',
                      'mask': '32'}],
                    [{'description': 'data-2 file',
                      'interface': 'Lo2',
                      'ip': '2.2.2.2',
                      'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo3',
                      'ip': '3.3.3.3',
                      'mask': '32'}],
                    [{'interface': 'Lo10', 'ip': '1.100.0.0', 'mask': '32'},
                     {'description': 'this interface from XYZ dataset',
                      'interface': 'Lo11',
                      'ip': '1.11.1.1',
                      'mask': '32'}]]]

# test_adding_data_from_files()

def test_get_input_load_default_template():
    template = """
<input name="my_input" load="yaml">
my_params:
  key1: val1
  key2: val2
  
more_params:
  - item1
  - item2
  - item3
</input>

<group name = "{{ timestamp }}.{{ interface }}">
{{ interface }} is up, line protocol is up
     {{ in_pkts}} packets input, 25963 bytes, 0 no buffer
     {{ out_pkts }} packets output, 26812 bytes, 0 underruns
</group>
"""
    parser = ttp(template=template)
    load = parser.get_input_load()
    assert load == {'_root_template_': {'my_input': {'more_params': ['item1', 'item2', 'item3'],
                                                     'my_params': {'key1': 'val1',
                                                                   'key2': 'val2'}}}}
 
def test_get_input_load_child_templates():
    template = """
<template name="template_1">
<input name="my_input" load="yaml">
my_params:
  key1: val1
  key2: val2
</input>

<group name = "{{ timestamp }}.{{ interface }}">
{{ interface }} is up, line protocol is up
     {{ in_pkts}} packets input, 25963 bytes, 0 no buffer
     {{ out_pkts }} packets output, 26812 bytes, 0 underruns
</group>
</template>

<template name="template_2">
<input name="my_input" load="yaml"> 
more_params:
  - item1
  - item2
  - item3
</input>

<group name = "{{ timestamp }}.{{ interface }}">
{{ interface }} is up, line protocol is up
     {{ in_pkts}} packets input, 25963 bytes, 0 no buffer
     {{ out_pkts }} packets output, 26812 bytes, 0 underruns
</group>
</template>
"""
    parser = ttp(template=template)
    load = parser.get_input_load()
    # pprint.pprint(load)
    assert load == {'template_1': {'my_input': {'my_params': {'key1': 'val1', 'key2': 'val2'}}},
                    'template_2': {'my_input': {'more_params': ['item1', 'item2', 'item3']}}}

def test_default_behaviour_with_named_templates():
    """
    This templates testthat datacorrectly added to all templates if 
    data and template supplied on TTP parser object instantiation
    """
    data = """
    # show service
     Name                         Protocol     Dst-Port/Type
     DISCARD                           UDP                 9
     DNS                                   UDP                53  
                                              TCP                 53
      ECHO                               UDP                   7 
"""
    template = """
<template name="services" results="per_template">
<group name="{{ name }}.{{ proto }}" method="table">
{{ ignore(r"\\s+") }}{{ name }}  {{ proto }}  {{ port | DIGIT }}
{{ ignore(r"\\s+") }}            {{ proto }}  {{ port | DIGIT }}
</group>
</template>
"""
    parser = ttp(data, template)
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res)
    assert res == {'services': {'DISCARD': {'UDP': {'port': '9'}},
                                'DNS': {'TCP': {'port': '53'}, 'UDP': {'port': '53'}},
                                'ECHO': {'UDP': {'port': '7'}}}}
                                
def match_var_cust_fun(data):
    data = data.upper()
    return data, None
    
def test_add_function_method_match_var():
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
interface {{ interface | myFun }}
 description {{ description | ORPHRASE | myFun }}
 ip address {{ ip }} {{ mask }}
</group>
"""
    parser = ttp(template=template_1)
    parser.add_function(match_var_cust_fun, scope="match", name="myFun")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert parser.result() == [[[{'interface': 'LO0', 'ip': '124.171.238.50', 'mask': '32'},
                                 {'description': 'THIS INTERFACE HAS DESCRIPTION',
                                  'interface': 'LO1',
                                  'ip': '1.1.1.1',
                                  'mask': '32'}]]] 

# test_add_function_method_match_var()

def test_add_function_method_match_var_multiproc():
    template_1 = """
<input load="text">
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32
</input>

<input load="text">
interface Lo10
 ip address 124.171.238.50 32
!
interface Lo11
 description this interface has description
 ip address 1.1.1.1 32
</input>

<input load="text">
interface Lo12
 ip address 124.171.238.50 32
!
interface Lo13
 description this interface has description
 ip address 1.1.1.1 32
</input>

<group>
interface {{ interface | myFun }}
 description {{ description | ORPHRASE | myFun }}
 ip address {{ ip }} {{ mask }}
</group>
"""
    parser = ttp(template=template_1)
    parser.add_function(match_var_cust_fun, scope="match", name="myFun")
    parser.parse(multi=True)
    res = parser.result()
    # pprint.pprint(res)
    # as it runs in multiprocessing, order of input results
    # returned by processes is non deterministic, hence list items
    # can change, as a result need to check if each item in a 
    # results list
    i1 = [{'interface': 'LO0', 'ip': '124.171.238.50', 'mask': '32'},
          {'description': 'THIS INTERFACE HAS DESCRIPTION',
           'interface': 'LO1',
           'ip': '1.1.1.1',
           'mask': '32'}]
    i2 = [{'interface': 'LO10', 'ip': '124.171.238.50', 'mask': '32'},
          {'description': 'THIS INTERFACE HAS DESCRIPTION',
           'interface': 'LO11',
           'ip': '1.1.1.1',
           'mask': '32'}]
    i3 = [{'interface': 'LO12', 'ip': '124.171.238.50', 'mask': '32'},
          {'description': 'THIS INTERFACE HAS DESCRIPTION',
           'interface': 'LO13',
           'ip': '1.1.1.1',
           'mask': '32'}]
    assert i1 in res[0] and i2 in res[0] and i3 in res[0]

# if __name__ == '__main__':
#     test_add_function_method_match_var_multiproc()

def group_cust_fun(data, *args, **kwargs):
    if kwargs.get("upper") == True:
        if "description" in data:
            data["description"] = data["description"].upper()
        else:
            data["description"] = "UNDEFINED"
    return data, None
    
def test_add_function_method_group():
    template_1 = """
<input load="text">
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32
</input>

<group myFun="upper=True">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>
"""
    parser = ttp(template=template_1, log_level="ERROR")
    parser.add_function(group_cust_fun, scope="group", name="myFun")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'description': 'UNDEFINED',
                      'interface': 'Lo0',
                      'ip': '124.171.238.50',
                      'mask': '32'},
                     {'description': 'THIS INTERFACE HAS DESCRIPTION',
                      'interface': 'Lo1',
                      'ip': '1.1.1.1',
                      'mask': '32'}]]]

# test_add_function_method_group()

def myInputFunReplace(data, *args):
    data = data.replace(args[0], args[1])
    return data, None
    
def test_add_function_method_input():
    template_1 = """
<input load="text" myInputFunReplace="'Lo', 'Loopback'">
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
    parser = ttp(log_level="ERROR")
    parser.add_function(myInputFunReplace, scope="input")
    parser.add_template(template=template_1, )
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Loopback0', 'ip': '124.171.238.50', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Loopback1',
                      'ip': '1.1.1.1',
                      'mask': '32'}]]]

# test_add_function_method_input()
    
def myOutputFun(data, work=False):
    if work == True:
        return str(data).upper()
    return data
    
def test_add_function_method_output():
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

<output myOutputFun="work=True"/>
"""
    parser = ttp(log_level="ERROR")
    parser.add_function(myOutputFun, scope="output")
    parser.add_template(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == ["[[{'IP': '124.171.238.50', 'MASK': '32', 'INTERFACE': 'LO0'}, {'IP': "
 "'1.1.1.1', 'MASK': '32', 'DESCRIPTION': 'THIS INTERFACE HAS DESCRIPTION', "
 "'INTERFACE': 'LO1'}]]"]
    
# test_add_function_method_output()
    
def custom_returner(data, *args, **kwargs):
    with open("./Output/custom_returner_test.txt", "w") as f:
        f.write(str(data))
    
def test_add_function_method_output_returner():
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

<output returner="custom_returner"/>
"""
    parser = ttp(log_level="ERROR")
    parser.add_function(custom_returner, scope="returners")
    parser.add_template(template=template_1)
    parser.parse()
    # res = parser.result()
    # pprint.pprint(res)
    with open("./Output/custom_returner_test.txt", "r") as f:
        assert f.read() == "[[{'ip': '124.171.238.50', 'mask': '32', 'interface': 'Lo0'}, {'ip': '1.1.1.1', 'mask': '32', 'description': 'this interface has description', 'interface': 'Lo1'}]]"
        
# test_add_function_method_output_returner()
    
def custom_formatter(data, *arg, **kwarg):
    return str(data).upper()
    
def test_add_function_method_output_formatter():
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

<output format="custom_formatter"/>
"""
    parser = ttp(log_level="ERROR")
    parser.add_function(custom_formatter, scope="formatters")
    parser.add_template(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == ["[[{'IP': '124.171.238.50', 'MASK': '32', 'INTERFACE': 'LO0'}, {'IP': "
 "'1.1.1.1', 'MASK': '32', 'DESCRIPTION': 'THIS INTERFACE HAS DESCRIPTION', "
 "'INTERFACE': 'LO1'}]]"]

# test_add_function_method_output_formatter()

def custom_getter(*args):
    return 12345
    
def test_add_function_method_variable_getter():
    template_1 = """
<vars name="var_check">var_1 = "custom_getter"</vars>

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
    parser = ttp(log_level="ERROR")
    parser.add_function(custom_getter, scope="variable")
    parser.add_template(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                      {'description': 'this interface has description',
                       'interface': 'Lo1',
                       'ip': '1.1.1.1',
                       'mask': '32'},
                      {'var_check': {'var_1': 12345}}]]]
    
# test_add_function_method_variable_getter()

def custom_macro(data):
    return data.upper()
    
def test_add_function_method_macro_match_var():
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
interface {{ interface | macro("custM") }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>
"""
    parser = ttp(log_level="ERROR")
    parser.add_function(custom_macro, scope="macro", name="custM")
    parser.add_template(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'LO0', 'ip': '124.171.238.50', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'LO1',
                      'ip': '1.1.1.1',
                      'mask': '32'}]]]

# test_add_function_method_macro_match_var()

def custom_macro_output(data):
    return str(data).upper()
    
def test_add_function_method_macro_output():
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

<output macro="custM_out"/>
"""
    parser = ttp(log_level="ERROR")
    parser.add_function(custom_macro_output, scope="macro", name="custM_out")
    parser.add_template(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == ["[[{'IP': '124.171.238.50', 'MASK': '32', 'INTERFACE': 'LO0'}, {'IP': "
 "'1.1.1.1', 'MASK': '32', 'DESCRIPTION': 'THIS INTERFACE HAS DESCRIPTION', "
 "'INTERFACE': 'LO1'}]]"]

# test_add_function_method_macro_output()

def test_get_input_load_anonymous_template():
    template = """
{{ interface }} is up, line protocol is up
     {{ in_pkts}} packets input, 25963 bytes, 0 no buffer
     {{ out_pkts }} packets output, 26812 bytes, 0 underruns
"""
    data = """
some data
    """
    parser = ttp(data, template=template)
    load = parser.get_input_load()
    # pprint.pprint(load)
    assert load == {'_root_template_': {'Default_Input': {}}}
    
# test_get_input_load_anonymous_template()

def to_test_globals_injection(data):
	if "_ttp_" in globals():
		return data, True
	return data, False
	
def test_add_function_method_group_globals_injection():
    template_1 = """
<input load="text">
interface Lo0
 ip address 124.171.238.50 32
!
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32
</input>

<group myFun="">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>
"""
    parser = ttp(template=template_1, log_level="ERROR")
    parser.add_function(to_test_globals_injection, scope="group", name="myFun", add_ttp=True)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                     {'description': 'this interface has description',
                      'interface': 'Lo1',
                      'ip': '1.1.1.1',
                      'mask': '32'}]]]

# test_add_function_method_group_globals_injection()

def test_add_input_structured_data_list():
    data_list = ["""
interface Lo0
 ip address 124.171.238.50 32
""",
"""
interface Lo1
 description this interface has description
 ip address 1.1.1.1 32
"""]

    template = """
<input macro="pre_process"/>

<macro>
def pre_process(data):
    return r'\\n'.join(data)
</macro>

<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>
"""
    parser = ttp(template=template, log_level="ERROR")
    parser.add_input(data_list)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
                     {'description': 'this interface has description', 'interface': 'Lo1'}]]]
    
test_add_input_structured_data_list()