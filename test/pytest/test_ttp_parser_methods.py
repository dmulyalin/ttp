import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp


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
