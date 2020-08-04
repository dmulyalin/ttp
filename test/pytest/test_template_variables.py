import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

def test_include_attribute_with_yaml_loader():
    template = """
<vars name="loaded_vars" load="yaml" include="./assets/yaml_vars.txt"/>

<input load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.1        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.13.2        98   0950.5785.5cd2  ARPA   Loopback0
Internet  10.12.13.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
Internet  10.12.13.4       198   0950.5C8A.5c41  ARPA   GigabitEthernet2.17
</input>

<group name="arp_test">
Internet  {{ ip }}  {{ age }}   {{ mac }}  ARPA   {{ interface | re("INTF_RE") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [[{'arp_test': [{'age': '98',
                                   'interface': 'FastEthernet2.13',
                                   'ip': '10.12.13.1',
                                   'mac': '0950.5785.5cd1'},
                                  {'age': '131',
                                   'interface': 'GigabitEthernet2.13',
                                   'ip': '10.12.13.3',
                                   'mac': '0150.7685.14d5'},
                                  {'age': '198',
                                   'interface': 'GigabitEthernet2.17',
                                   'ip': '10.12.13.4',
                                   'mac': '0950.5C8A.5c41'}],
                     'loaded_vars': {'INTF_RE': 'GigabitEthernet\\S+|Fast\\S+',
                                     'var_1': 'value_1',
                                     'var_2': [1, 2, 3, 4, 'a']}}]]
    
# test_include_attribute_with_yaml_loader()