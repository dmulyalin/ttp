import sys
sys.path.insert(0,'../..')
import pprint

import logging
logging.basicConfig(level="INFO")

from ttp import ttp

def test_lookup_include_csv():
    template = """
<lookup name="ASNs" load="csv" include="./assets/test_lookup_include_csv.csv"/>

<input load="text">
router bgp 65101
</input>

<group name="bgp_config">
router bgp {{ bgp_as | lookup(ASNs, add_field="as_info") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    lookup_data = parser._templates[0].lookups
    res = parser.result()
    assert lookup_data == {'ASNs': {'65100': {'as_description': 'Private ASN for CN451275',
                                              'as_name': 'Customer_1'},
                                    '65101': {'as_description': 'Private ASN for FTTB CPEs',
                                              'as_name': 'CPEs'}}}
    assert res == [[{'bgp_config': {'as_info': {'as_description': 'Private ASN for FTTB CPEs',
                                                'as_name': 'CPEs'},
                                    'bgp_as': '65101'}}]]
    
# test_lookup_include_csv()

def test_lookup_include_yaml():
    template = """
<lookup name="yaml_look" load="yaml" include="./assets/test_lookup_include_yaml.txt">
</lookup>

<input load="text">
router bgp 65100
</input>

<group name="bgp_config">
router bgp {{ bgp_as | lookup("yaml_look", add_field="as_details") }}
</group> 
    """
    parser = ttp(template=template)
    parser.parse()
    lookup_data = parser._templates[0].lookups
    res = parser.result()
    # pprint.pprint(lookup_data)
    # pprint.pprint(res)
    assert lookup_data == {'yaml_look': {'65100': {'as_description': 'Private ASN',
                                                   'as_name': 'Subs',
                                                   'prefix_num': '734'},
                                         '65101': {'as_description': 'Cust-1 ASN',
                                                   'as_name': 'Cust1',
                                                   'prefix_num': '156'}}}
    assert res == [[{'bgp_config': {'as_details': {'as_description': 'Private ASN',
                                                   'as_name': 'Subs',
                                                   'prefix_num': '734'},
                                    'bgp_as': '65100'}}]]
# test_lookup_include_yaml()