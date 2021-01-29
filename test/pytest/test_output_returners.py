import sys
sys.path.insert(0,'../..')
import pprint

import logging
logging.basicConfig(level="ERROR")

from ttp import ttp

def test_file_returner_format_raw():
    template_1 = """
<input load="text">
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
</input>

<group>
interface {{ interface }}
  vlan {{ vlan | to_int }}
</group>

<output
returner="file"
url="./Output/"
filename="out_test_file_returner.txt"
/>
"""
    parser = ttp(template=template_1)
    parser.parse()
    # res=parser.result()
    # pprint.pprint(res)
    with open("./Output/out_test_file_returner.txt", "r") as f:
        assert f.read() == "[[{'vlan': 10, 'interface': 'Port-Chanel11'}, {'vlan': 20, 'interface': 'Loopback0'}]]"
        
# test_file_returner()

def test_file_returner_format_raw_incomplete_url():
    template_1 = """
<input load="text">
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
</input>

<group>
interface {{ interface }}
  vlan {{ vlan | to_int }}
</group>

<output
returner="file"
url="./Output"
filename="out_test_file_returner_2.txt"
/>
"""
    parser = ttp(template=template_1)
    parser.parse()
    # res=parser.result()
    # pprint.pprint(res)
    with open("./Output/out_test_file_returner_2.txt", "r") as f:
        assert f.read() == "[[{'vlan': 10, 'interface': 'Port-Chanel11'}, {'vlan': 20, 'interface': 'Loopback0'}]]"
        
# test_file_returner_format_raw_incomplete_url()

def test_file_returner_format_raw_1():
    template_1 = """
<input load="text">
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
</input>

<group>
interface {{ interface }}
  vlan {{ vlan | to_int }}
</group>

<output>
returner="file"
url="./Output/"
filename="out_test_file_returner_1.txt"
</output>
"""
    parser = ttp(template=template_1)
    parser.parse()
    # res=parser.result()
    # pprint.pprint(res)
    with open("./Output/out_test_file_returner_1.txt", "r") as f:
        assert f.read() == "[[{'vlan': 10, 'interface': 'Port-Chanel11'}, {'vlan': 20, 'interface': 'Loopback0'}]]"
        
def test_file_returner_filename_format():
    template_1 = """
<input load="text">
switch-sw1# show run interfaces
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
</input>

<input load="text">
switch-sw2# show run interfaces
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
</input>

<vars>
host_name = "gethostname"
</vars>

<group>
interface {{ interface }}
  vlan {{ vlan | to_int }}
{{ hostname | set(host_name) }}
</group>

<output>
returner="file"
url="./Output/"
filename="out_test_file_returner_{host_name}.txt"
</output>
"""
    parser = ttp(template=template_1)
    parser.parse()
    # res=parser.result()
    # pprint.pprint(res)
    with open("./Output/out_test_file_returner_switch-sw2.txt", "r") as f:
        assert f.read() == "[[{'vlan': 10, 'interface': 'Port-Chanel11', 'hostname': 'switch-sw1'}, {'vlan': 20, 'interface': 'Loopback0', 'hostname': 'switch-sw1'}], [{'vlan': 10, 'interface': 'Port-Chanel11', 'hostname': 'switch-sw2'}, {'vlan': 20, 'interface': 'Loopback0', 'hostname': 'switch-sw2'}]]"
    
# test_file_returner_filename_format()

def test_file_returner_filename_format_group_specific_output():
    template_1 = """
<input load="text">
switch-sw1# show run interfaces
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
</input>

<input load="text">
switch-sw2# show run interfaces
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
</input>

<vars>
host_name = "gethostname"
</vars>

<group output="save_to_file">
interface {{ interface }}
  vlan {{ vlan | to_int }}
</group>

<output name="save_to_file">
returner="file"
url="./Output/"
filename="out_test_file_returner_{host_name}_group_specific_outputter.txt"
</output>
"""
    parser = ttp(template=template_1)
    parser.parse()
    with open("./Output/out_test_file_returner_switch-sw1_group_specific_outputter.txt", "r") as f:
        assert f.read() == "{'_anonymous_': [{'vlan': 10, 'interface': 'Port-Chanel11'}, {'vlan': 20, 'interface': 'Loopback0'}]}"
    with open("./Output/out_test_file_returner_switch-sw2_group_specific_outputter.txt", "r") as f:
        assert f.read() == "{'_anonymous_': [{'vlan': 10, 'interface': 'Port-Chanel11'}, {'vlan': 20, 'interface': 'Loopback0'}]}"
        
# test_file_returner_filename_format_group_specific_output()