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