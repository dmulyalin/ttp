import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

import logging
logging.basicConfig(level=logging.ERROR)

def test_cerberus_validate_per_input():
    template = """
<input load="text">
csw1# show run | sec ntp
hostname csw1
ntp peer 1.2.3.4
ntp peer 1.2.3.5
</input>

<input load="text">
csw2# show run | sec ntp
hostname csw2
ntp peer 1.2.3.4
ntp peer 3.3.3.3
</input>

<vars>
ntp_schema = {
    "ntp_peers": {
        'type': 'list',
        'schema': {
            'type': 'dict', 
            'schema': {
                'peer': {
                    'type': 'string', 
                    'allowed': ['1.2.3.4', '1.2.3.5']
                }
            }
        }
    }
}
</vars>

<group name="_">
hostname {{ host_name }}
</group>

<group name="ntp_peers*">
ntp peer {{ peer }}
</group>

<output validate="ntp_schema, info='{host_name} NTP peers valid', errors='errors'"/>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'errors': {}, 'info': 'csw1 NTP peers valid', 'valid': True},
                   {'errors': {'ntp_peers': [{1: [{'peer': ['unallowed value 3.3.3.3']}]}]},
                    'info': 'csw2 NTP peers valid',
                    'valid': False}]]
    
# test_cerberus_validate_per_input()

def test_cerberus_validate_per_template():
    template = """
<template results="per_template">
<input load="text">
csw1# show run | sec ntp
ntp peer 1.2.3.4
ntp peer 1.2.3.5
</input>

<input load="text">
csw1# show run | sec ntp
ntp peer 1.2.3.4
ntp peer 3.3.3.3
</input>

<vars>
ntp_schema = {
    "ntp_peers": {
        'type': 'list',
        'schema': {
            'type': 'dict', 
            'schema': {
                'peer': {
                    'type': 'string', 
                    'allowed': ['1.2.3.4', '1.2.3.5']
                }
            }
        }
    }
}
hostname = "gethostname"
</vars>

<group name="ntp_peers*">
ntp peer {{ peer }}
</group>

<output validate="ntp_schema, info='{hostname} NTP peers valid', errors='errors'"/>
</template>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [{'errors': {'ntp_peers': [{3: [{'peer': ['unallowed value 3.3.3.3']}]}]},
                    'info': 'csw1 NTP peers valid',
                    'valid': False}]
    
# test_cerberus_validate_per_template()