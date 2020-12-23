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

def test_global_output_deepdiff_with_var_before():
    template = """
<vars>
before = [[{'description': 'some info',
             'interface': 'GigabitEthernet1',
             'ip': '10.123.89.56',
             'mask': '255.255.255.255'},
            {'interface': 'GigabitEthernet2',
             'ip': '10.123.89.55',
             'mask': '255.255.255.0'}]]
</vars>

<input name="Cisco_ios" load="text">
r1#show interfaces | inc line protocol:
interface GigabitEthernet1
 description some info
 vrf forwarding MGMT
 ip address 10.123.89.56 255.255.255.0
interface GigabitEthernet2
 ip address 10.123.89.55 255.255.255.0
</input>

<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>

<output deepdiff="var_before='before'"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [{'values_changed': {"root[0][0]['mask']": {'new_value': '255.255.255.0',
                                                              'old_value': '255.255.255.255'}}}]
    
# test_global_output_deepdiff_with_var_before()

def test_group_specific_output_deepdiff_with_var_before():
    template = """
<vars>
before = {"interfaces": [{'description': 'some info',
                          'interface': 'GigabitEthernet1',
                          'ip': '10.123.89.56',
                          'mask': '255.255.255.255'},
                         {'interface': 'GigabitEthernet2',
                          'ip': '10.123.89.55',
                          'mask': '255.255.255.0'}]}
</vars>

<input name="Cisco_ios" load="text">
r1#show interfaces | inc line protocol:
interface GigabitEthernet1
 description some info
 vrf forwarding MGMT
 ip address 10.123.89.56 255.255.255.0
interface GigabitEthernet2
 ip address 10.123.89.55 255.255.255.0
</input>

<group name="interfaces*" output="out_1">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>

<group name="interfaces_2*">
interface {{ interface }}
 vrf forwarding {{ vrf }}
 ip address {{ ip }} {{ mask }}
</group>

<output name="out_1" deepdiff="var_before='before'"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interfaces_2': [{'interface': 'GigabitEthernet1',
                                        'ip': '10.123.89.56',
                                        'mask': '255.255.255.0',
                                        'vrf': 'MGMT'},
                                       {'interface': 'GigabitEthernet2',
                                        'ip': '10.123.89.55',
                                        'mask': '255.255.255.0'}]},
                    {'values_changed': {"root['interfaces'][0]['mask']": {'new_value': '255.255.255.0',
                                                                          'old_value': '255.255.255.255'}}}]]]
                                                              
# test_group_specific_output_deepdiff_with_var_before()

def test_group_specific_output_deepdiff_with_var_before_with_add_field():
    template = """
<vars>
before = {"interfaces": [{'description': 'some info',
                          'interface': 'GigabitEthernet1',
                          'ip': '10.123.89.56',
                          'mask': '255.255.255.255'},
                         {'interface': 'GigabitEthernet2',
                          'ip': '10.123.89.55',
                          'mask': '255.255.255.0'}]}
</vars>

<input name="Cisco_ios" load="text">
r1#show interfaces | inc line protocol:
interface GigabitEthernet1
 description some info
 vrf forwarding MGMT
 ip address 10.123.89.56 255.255.255.0
interface GigabitEthernet2
 ip address 10.123.89.55 255.255.255.0
</input>

<group name="interfaces*" output="out_1">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>

<group name="interfaces_2*">
interface {{ interface }}
 vrf forwarding {{ vrf }}
 ip address {{ ip }} {{ mask }}
</group>

<output name="out_1" deepdiff="var_before='before', add_field='diff'"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interfaces_2': [{'interface': 'GigabitEthernet1',
                                        'ip': '10.123.89.56',
                                        'mask': '255.255.255.0',
                                        'vrf': 'MGMT'},
                                       {'interface': 'GigabitEthernet2',
                                        'ip': '10.123.89.55',
                                        'mask': '255.255.255.0'}]},
                     {'diff': {'values_changed': {"root['interfaces'][0]['mask']": {'new_value': '255.255.255.0',
                                                                                    'old_value': '255.255.255.255'}}},
                      'interfaces': [{'description': 'some info',
                                      'interface': 'GigabitEthernet1',
                                      'ip': '10.123.89.56',
                                      'mask': '255.255.255.0'},
                                     {'interface': 'GigabitEthernet2',
                                      'ip': '10.123.89.55',
                                      'mask': '255.255.255.0'}]}]]]
    
# test_group_specific_output_deepdiff_with_var_before_with_add_field()   

def test_yangson_validate():
    data = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    template = """
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="'./yang_modules/'"
</output>
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [{'comment': '',
  'exception': {},
  'result': [{'ietf-interfaces:interfaces': {'interface': [{'admin-status': 'down',
                                                            'description': 'Customer '
                                                                           '#32148',
                                                            'enabled': False,
                                                            'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                          'netmask': '255.255.255.128',
                                                                                          'origin': 'static'}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/3.251',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'vCPEs '
                                                                           'access '
                                                                           'control',
                                                            'enabled': True,
                                                            'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                          'netmask': '255.255.255.128',
                                                                                          'origin': 'static'}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/4',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'Works '
                                                                           'data',
                                                            'enabled': True,
                                                            'ietf-ip:ipv4': {'mtu': 9000},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/5',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'Works '
                                                                           'data '
                                                                           'v6',
                                                            'enabled': True,
                                                            'ietf-ip:ipv6': {'address': [{'ip': '2001::1',
                                                                                          'origin': 'static',
                                                                                          'prefix-length': 64},
                                                                                         {'ip': '2001:1::1',
                                                                                          'origin': 'static',
                                                                                          'prefix-length': 64}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/7',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'}]}}],
  'valid': {0: True}}]
    
# test_yangson_validate()

def test_yangson_validate_yang_lib_in_output_tag_data():
    data = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    template = """
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output validate_yangson="yang_mod_dir='./yang_modules/'" load="text">
{
  "ietf-yang-library:modules-state": {
    "module-set-id": "",
    "module": [
      {
        "name": "iana-if-type",
        "revision": "2017-01-19",
        "namespace": "urn:ietf:params:xml:ns:yang:iana-if-type",
        "conformance-type": "implement"
      },
      {
        "name": "ietf-inet-types",
        "revision": "2013-07-15",
        "namespace": "urn:ietf:params:xml:ns:yang:ietf-inet-types",
        "conformance-type": "import"
      },
      {
        "name": "ietf-interfaces",
        "revision": "2018-02-20",
        "namespace": "urn:ietf:params:xml:ns:yang:ietf-interfaces",
        "feature": [
          "arbitrary-names",
          "pre-provisioning",
          "if-mib"
        ],
        "conformance-type": "implement"
      },
      {
        "name": "ietf-ip",
        "revision": "2018-02-22",
        "namespace": "urn:ietf:params:xml:ns:yang:ietf-ip",
        "feature": [
          "ipv4-non-contiguous-netmasks",
          "ipv6-privacy-autoconf"
        ],
        "conformance-type": "implement"
      },
      {
        "name": "ietf-yang-types",
        "revision": "2013-07-15",
        "namespace": "urn:ietf:params:xml:ns:yang:ietf-yang-types",
        "conformance-type": "import"
      }
    ]
  }
}
</output>
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [{'comment': '',
  'exception': {},
  'result': [{'ietf-interfaces:interfaces': {'interface': [{'admin-status': 'down',
                                                            'description': 'Customer '
                                                                           '#32148',
                                                            'enabled': False,
                                                            'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                          'netmask': '255.255.255.128',
                                                                                          'origin': 'static'}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/3.251',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'vCPEs '
                                                                           'access '
                                                                           'control',
                                                            'enabled': True,
                                                            'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                          'netmask': '255.255.255.128',
                                                                                          'origin': 'static'}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/4',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'Works '
                                                                           'data',
                                                            'enabled': True,
                                                            'ietf-ip:ipv4': {'mtu': 9000},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/5',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'Works '
                                                                           'data '
                                                                           'v6',
                                                            'enabled': True,
                                                            'ietf-ip:ipv6': {'address': [{'ip': '2001::1',
                                                                                          'origin': 'static',
                                                                                          'prefix-length': 64},
                                                                                         {'ip': '2001:1::1',
                                                                                          'origin': 'static',
                                                                                          'prefix-length': 64}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/7',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'}]}}],
  'valid': {0: True}}]
                    
# test_yangson_validate_yang_lib_in_output_tag_data()

def test_yangson_validate_multiple_inputs_mode_per_input_with_yang_lib_in_file():
    data1 = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    data2 = """
interface GigabitEthernet1/3.254
 description Customer #5618
 encapsulation dot1q 251
 ip address 172.16.33.11 255.255.255.128
 shutdown
!
    """
    template = """
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="yang_mod_dir='./yang_modules/', yang_mod_lib='./yang_modules/library/yang-library.json'"
</output>
    """
    parser = ttp(template=template)
    parser.add_input(data1)
    parser.add_input(data2)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [{'comment': '',
  'exception': {},
  'result': [{'ietf-interfaces:interfaces': {'interface': [{'admin-status': 'down',
                                                            'description': 'Customer '
                                                                           '#32148',
                                                            'enabled': False,
                                                            'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                          'netmask': '255.255.255.128',
                                                                                          'origin': 'static'}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/3.251',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'vCPEs '
                                                                           'access '
                                                                           'control',
                                                            'enabled': True,
                                                            'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                          'netmask': '255.255.255.128',
                                                                                          'origin': 'static'}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/4',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'Works '
                                                                           'data',
                                                            'enabled': True,
                                                            'ietf-ip:ipv4': {'mtu': 9000},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/5',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'},
                                                           {'admin-status': 'up',
                                                            'description': 'Works '
                                                                           'data '
                                                                           'v6',
                                                            'enabled': True,
                                                            'ietf-ip:ipv6': {'address': [{'ip': '2001::1',
                                                                                          'origin': 'static',
                                                                                          'prefix-length': 64},
                                                                                         {'ip': '2001:1::1',
                                                                                          'origin': 'static',
                                                                                          'prefix-length': 64}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/7',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'}]}},
             {'ietf-interfaces:interfaces': {'interface': [{'admin-status': 'down',
                                                            'description': 'Customer '
                                                                           '#5618',
                                                            'enabled': False,
                                                            'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.11',
                                                                                          'netmask': '255.255.255.128',
                                                                                          'origin': 'static'}]},
                                                            'if-index': 1,
                                                            'link-up-down-trap-enable': 'enabled',
                                                            'name': 'GigabitEthernet1/3.254',
                                                            'oper-status': 'unknown',
                                                            'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                            'type': 'iana-if-type:ethernetCsmacd'}]}}],
  'valid': {0: True, 1: True}}]
                    
# test_yangson_validate_multiple_inputs_mode_per_input_with_yang_lib_in_file()


def test_yangson_validate_multiple_inputs_mode_per_template():
    data1 = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    data2 = """
interface GigabitEthernet1/3.254
 description Customer #5618
 encapsulation dot1q 251
 ip address 172.16.33.11 255.255.255.128
 shutdown
!
    """
    template = """
<template name="ietf:interfaces" results="per_template">
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="yang_mod_dir='./yang_modules/', yang_mod_lib='./yang_modules/library/yang-library.json'"
</output>
</template>
    """
    parser = ttp(template=template)
    parser.add_input(data1, template_name="ietf:interfaces")
    parser.add_input(data2, template_name="ietf:interfaces")
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res)
    assert res == {'ietf:interfaces': {'comment': '',
                     'exception': {},
                     'result': {'ietf-interfaces:interfaces': {'interface': [{'admin-status': 'down',
                                                                              'description': 'Customer '
                                                                                             '#32148',
                                                                              'enabled': False,
                                                                              'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                                            'netmask': '255.255.255.128',
                                                                                                            'origin': 'static'}]},
                                                                              'if-index': 1,
                                                                              'link-up-down-trap-enable': 'enabled',
                                                                              'name': 'GigabitEthernet1/3.251',
                                                                              'oper-status': 'unknown',
                                                                              'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                              'type': 'iana-if-type:ethernetCsmacd'},
                                                                             {'admin-status': 'up',
                                                                              'description': 'vCPEs '
                                                                                             'access '
                                                                                             'control',
                                                                              'enabled': True,
                                                                              'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                                            'netmask': '255.255.255.128',
                                                                                                            'origin': 'static'}]},
                                                                              'if-index': 1,
                                                                              'link-up-down-trap-enable': 'enabled',
                                                                              'name': 'GigabitEthernet1/4',
                                                                              'oper-status': 'unknown',
                                                                              'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                              'type': 'iana-if-type:ethernetCsmacd'},
                                                                             {'admin-status': 'up',
                                                                              'description': 'Works '
                                                                                             'data',
                                                                              'enabled': True,
                                                                              'ietf-ip:ipv4': {'mtu': 9000},
                                                                              'if-index': 1,
                                                                              'link-up-down-trap-enable': 'enabled',
                                                                              'name': 'GigabitEthernet1/5',
                                                                              'oper-status': 'unknown',
                                                                              'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                              'type': 'iana-if-type:ethernetCsmacd'},
                                                                             {'admin-status': 'up',
                                                                              'description': 'Works '
                                                                                             'data '
                                                                                             'v6',
                                                                              'enabled': True,
                                                                              'ietf-ip:ipv6': {'address': [{'ip': '2001::1',
                                                                                                            'origin': 'static',
                                                                                                            'prefix-length': 64},
                                                                                                           {'ip': '2001:1::1',
                                                                                                            'origin': 'static',
                                                                                                            'prefix-length': 64}]},
                                                                              'if-index': 1,
                                                                              'link-up-down-trap-enable': 'enabled',
                                                                              'name': 'GigabitEthernet1/7',
                                                                              'oper-status': 'unknown',
                                                                              'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                              'type': 'iana-if-type:ethernetCsmacd'},
                                                                             {'admin-status': 'down',
                                                                              'description': 'Customer '
                                                                                             '#5618',
                                                                              'enabled': False,
                                                                              'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.11',
                                                                                                            'netmask': '255.255.255.128',
                                                                                                            'origin': 'static'}]},
                                                                              'if-index': 1,
                                                                              'link-up-down-trap-enable': 'enabled',
                                                                              'name': 'GigabitEthernet1/3.254',
                                                                              'oper-status': 'unknown',
                                                                              'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                              'type': 'iana-if-type:ethernetCsmacd'}]}},
                     'valid': True}}

# test_yangson_validate_multiple_inputs_mode_per_template()


def test_yangson_validate_multiple_inputs_mode_per_input_with_yang_lib_in_file_to_xml():
    data1 = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    data2 = """
interface GigabitEthernet1/3.254
 description Customer #5618
 encapsulation dot1q 251
 ip address 172.16.33.11 255.255.255.128
 shutdown
!
    """
    template = """
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="yang_mod_dir='./yang_modules/', yang_mod_lib='./yang_modules/library/yang-library.json', to_xml=True"
</output>
    """
    parser = ttp(template=template)
    parser.add_input(data1)
    parser.add_input(data2)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [{'comment': '',
                    'exception': {},
                    'result': ['<interfaces '
                               'xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"><interface><description>Customer '
                               '#32148</description><name>GigabitEthernet1/3.251</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>down</admin-status><enabled>False</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                               'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.10</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface><interface><description>vCPEs '
                               'access '
                               'control</description><name>GigabitEthernet1/4</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                               'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.10</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface><interface><description>Works '
                               'data</description><name>GigabitEthernet1/5</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                               'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><mtu>9000</mtu></ipv4></interface><interface><description>Works '
                               'data '
                               'v6</description><name>GigabitEthernet1/7</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv6 '
                               'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>2001::1</ip><prefix-length>64</prefix-length><origin>static</origin></address><address><ip>2001:1::1</ip><prefix-length>64</prefix-length><origin>static</origin></address></ipv6></interface></interfaces>',
                               '<interfaces '
                               'xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"><interface><description>Customer '
                               '#5618</description><name>GigabitEthernet1/3.254</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>down</admin-status><enabled>False</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                               'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.11</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface></interfaces>'],
                    'valid': {0: True, 1: True}}]
  
# test_yangson_validate_multiple_inputs_mode_per_input_with_yang_lib_in_file_to_xml()


def test_yangson_validate_multiple_inputs_mode_per_template_to_xml():
    data1 = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    data2 = """
interface GigabitEthernet1/3.254
 description Customer #5618
 encapsulation dot1q 251
 ip address 172.16.33.11 255.255.255.128
 shutdown
!
    """
    template = """
<template name="ietf:interfaces" results="per_template">
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="yang_mod_dir='./yang_modules/', yang_mod_lib='./yang_modules/library/yang-library.json', to_xml=True"
</output>
</template>
    """
    parser = ttp(template=template)
    parser.add_input(data1, template_name="ietf:interfaces")
    parser.add_input(data2, template_name="ietf:interfaces")
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res)
    assert res == {'ietf:interfaces': {'comment': '',
                                       'exception': {},
                                       'result': '<interfaces '
                                                 'xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"><interface><description>Customer '
                                                 '#32148</description><name>GigabitEthernet1/3.251</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>down</admin-status><enabled>False</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                                                 'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.10</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface><interface><description>vCPEs '
                                                 'access '
                                                 'control</description><name>GigabitEthernet1/4</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                                                 'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.10</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface><interface><description>Works '
                                                 'data</description><name>GigabitEthernet1/5</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                                                 'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><mtu>9000</mtu></ipv4></interface><interface><description>Works '
                                                 'data '
                                                 'v6</description><name>GigabitEthernet1/7</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv6 '
                                                 'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>2001::1</ip><prefix-length>64</prefix-length><origin>static</origin></address><address><ip>2001:1::1</ip><prefix-length>64</prefix-length><origin>static</origin></address></ipv6></interface><interface><description>Customer '
                                                 '#5618</description><name>GigabitEthernet1/3.254</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>down</admin-status><enabled>False</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                                                 'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.11</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface></interfaces>',
                                       'valid': True}}
    
# test_yangson_validate_multiple_inputs_mode_per_template_to_xml()

    
def test_yangson_validate_invalid_data_in_first_input_item():
    data1 = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    data2 = """
interface GigabitEthernet1/3.254
 description Customer #5618
 encapsulation dot1q 251
 ip address 172.16.33.11 255.255.255.128
 shutdown
!
    """
    template = """
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="yang_mod_dir='./yang_modules/', yang_mod_lib='./yang_modules/library/yang-library.json'"
</output>
    """
    parser = ttp(template=template)
    parser.add_input(data1)
    parser.add_input(data2)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res[0]["valid"][0] == False
    
# test_yangson_validate_invalid_data_in_first_input_item()

def test_yangson_validate_metadata_false_validation_successful():
    data = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    template = """
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="'./yang_modules/', metadata=False"
</output>
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'ietf-interfaces:interfaces': {'interface': [{'admin-status': 'down',
                                                                   'description': 'Customer '
                                                                                  '#32148',
                                                                   'enabled': False,
                                                                   'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                                 'netmask': '255.255.255.128',
                                                                                                 'origin': 'static'}]},
                                                                   'if-index': 1,
                                                                   'link-up-down-trap-enable': 'enabled',
                                                                   'name': 'GigabitEthernet1/3.251',
                                                                   'oper-status': 'unknown',
                                                                   'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                   'type': 'iana-if-type:ethernetCsmacd'},
                                                                  {'admin-status': 'up',
                                                                   'description': 'vCPEs access '
                                                                                  'control',
                                                                   'enabled': True,
                                                                   'ietf-ip:ipv4': {'address': [{'ip': '172.16.33.10',
                                                                                                 'netmask': '255.255.255.128',
                                                                                                 'origin': 'static'}]},
                                                                   'if-index': 1,
                                                                   'link-up-down-trap-enable': 'enabled',
                                                                   'name': 'GigabitEthernet1/4',
                                                                   'oper-status': 'unknown',
                                                                   'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                   'type': 'iana-if-type:ethernetCsmacd'},
                                                                  {'admin-status': 'up',
                                                                   'description': 'Works data',
                                                                   'enabled': True,
                                                                   'ietf-ip:ipv4': {'mtu': 9000},
                                                                   'if-index': 1,
                                                                   'link-up-down-trap-enable': 'enabled',
                                                                   'name': 'GigabitEthernet1/5',
                                                                   'oper-status': 'unknown',
                                                                   'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                   'type': 'iana-if-type:ethernetCsmacd'},
                                                                  {'admin-status': 'up',
                                                                   'description': 'Works data v6',
                                                                   'enabled': True,
                                                                   'ietf-ip:ipv6': {'address': [{'ip': '2001::1',
                                                                                                 'origin': 'static',
                                                                                                 'prefix-length': 64},
                                                                                                {'ip': '2001:1::1',
                                                                                                 'origin': 'static',
                                                                                                 'prefix-length': 64}]},
                                                                   'if-index': 1,
                                                                   'link-up-down-trap-enable': 'enabled',
                                                                   'name': 'GigabitEthernet1/7',
                                                                   'oper-status': 'unknown',
                                                                   'statistics': {'discontinuity-time': '1970-01-01T00:00:00+00:00'},
                                                                   'type': 'iana-if-type:ethernetCsmacd'}]}}]]
                                                                   
# test_yangson_validate_metadata_false_validation_successful()

def test_yangson_validate_metadata_false_validation_unsuccessful():
    data = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    template = """
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(1) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="'./yang_modules/', metadata=False"
</output>
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [False]

# test_yangson_validate_metadata_false_validation_unsuccessful()

def test_yangson_validate_metadata_false_multiple_inputs_mode_per_input_to_xml():
    data1 = """
interface GigabitEthernet1/3.251
 description Customer #32148
 encapsulation dot1q 251
 ip address 172.16.33.10 255.255.255.128
 shutdown
!
interface GigabitEthernet1/4
 description vCPEs access control
 ip address 172.16.33.10 255.255.255.128
!
interface GigabitEthernet1/5
 description Works data
 ip mtu 9000
!
interface GigabitEthernet1/7
 description Works data v6
 ipv6 address 2001::1/64
 ipv6 address 2001:1::1/64
!
    """
    data2 = """
interface GigabitEthernet1/3.254
 description Customer #5618
 encapsulation dot1q 251
 ip address 172.16.33.11 255.255.255.128
 shutdown
!
    """
    template = """
<macro>
def add_iftype(data):
    if "eth" in data.lower():
        return data, {"type": "iana-if-type:ethernetCsmacd"}
    return data, {"type": None}
</macro>

<group name="ietf-interfaces:interfaces.interface*">
interface {{ name | macro(add_iftype) }}
 description {{ description | re(".+") }}
 shutdown {{ enabled | set(False) | let("admin-status", "down") }}
 {{ link-up-down-trap-enable | set(enabled) }}
 {{ admin-status | set(up) }}
 {{ enabled | set(True) }}
 {{ if-index | set(1) }}
 {{ statistics | set({"discontinuity-time": "1970-01-01T00:00:00+00:00"}) }}
 {{ oper-status | set(unknown) }}
 
 <group name="ietf-ip:ipv4">
 ip mtu {{ mtu | to_int }} 
 </group>
 
 <group name="ietf-ip:ipv4.address*">
 ip address {{ ip | _start_ }} {{ netmask }}
 ip address {{ ip | _start_ }} {{ netmask }} secondary
 {{ origin | set(static) }}  
 </group>

 <group name="ietf-ip:ipv6.address*">
 ipv6 address {{ ip | _start_ }}/{{ prefix-length | to_int }}
 {{ origin | set(static) }}  
 </group>
 
</group>

<output>
validate_yangson="yang_mod_dir='./yang_modules/', yang_mod_lib='./yang_modules/library/yang-library.json', to_xml=True, metadata=False"
</output>
    """
    parser = ttp(template=template)
    parser.add_input(data1)
    parser.add_input(data2)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [['<interfaces '
                    'xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"><interface><description>Customer '
                    '#32148</description><name>GigabitEthernet1/3.251</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>down</admin-status><enabled>False</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                    'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.10</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface><interface><description>vCPEs '
                    'access '
                    'control</description><name>GigabitEthernet1/4</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                    'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.10</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface><interface><description>Works '
                    'data</description><name>GigabitEthernet1/5</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                    'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><mtu>9000</mtu></ipv4></interface><interface><description>Works '
                    'data '
                    'v6</description><name>GigabitEthernet1/7</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>up</admin-status><enabled>True</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv6 '
                    'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>2001::1</ip><prefix-length>64</prefix-length><origin>static</origin></address><address><ip>2001:1::1</ip><prefix-length>64</prefix-length><origin>static</origin></address></ipv6></interface></interfaces>',
                    '<interfaces '
                    'xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"><interface><description>Customer '
                    '#5618</description><name>GigabitEthernet1/3.254</name><type>iana-if-type:ethernetCsmacd</type><link-up-down-trap-enable>enabled</link-up-down-trap-enable><admin-status>down</admin-status><enabled>False</enabled><if-index>1</if-index><statistics><discontinuity-time>1970-01-01T00:00:00+00:00</discontinuity-time></statistics><oper-status>unknown</oper-status><ipv4 '
                    'xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"><address><ip>172.16.33.11</ip><netmask>255.255.255.128</netmask><origin>static</origin></address></ipv4></interface></interfaces>']]
    
# test_yangson_validate_multiple_inputs_mode_per_input_with_yang_lib_in_file_to_xml_metadata_false()