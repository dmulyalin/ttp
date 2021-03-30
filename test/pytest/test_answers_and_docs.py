import sys
sys.path.insert(0,'../..')
import pprint

import logging
logging.basicConfig(level=logging.DEBUG)

from ttp import ttp

def test_answer_1():
    """https://stackoverflow.com/questions/63522291/parsing-blocks-of-text-within-a-file-into-objects
    """
    data = """
#*Approximate Distance Oracles with Improved Query Time.
#@Christian Wulff-Nilsen
#t2015
#cEncyclopedia of Algorithms
#index555036b37cea80f954149ffc

#*Subset Sum Algorithm for Bin Packing.
#@Julián Mestre
#t2015
#cEncyclopedia of Algorithms
#index555036b37cea80f954149ffd
    """
    template = """
#*{{ info | ORPHRASE }}
#@{{ author | ORPHRASE }}
#t{{ year }}
#c{{ title | ORPHRASE }}
#index{{ index }}
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result(structure="flat_list")
    pprint.pprint(res)
    assert res == [{'author': 'Christian Wulff-Nilsen',
                    'index': '555036b37cea80f954149ffc',
                    'info': 'Approximate Distance Oracles with Improved Query Time.',
                    'title': 'Encyclopedia of Algorithms',
                    'year': '2015'},
                   {'author': 'Julián Mestre',
                    'index': '555036b37cea80f954149ffd',
                    'info': 'Subset Sum Algorithm for Bin Packing.',
                    'title': 'Encyclopedia of Algorithms',
                    'year': '2015'}]
    
# test_answer_1()

def test_answer_2():
    """https://stackoverflow.com/questions/63499479/extract-value-from-text-string-using-format-string-in-python
    """
    data = """
name=username1, age=1001
name=username2, age=1002
name=username3, age=1003
"""
    template = "name={{ name }}, age={{ age }}"
    parser = ttp(data, template)
    parser.parse()
    res = parser.result(structure="flat_list")
    # pprint.pprint(res)
    assert res == [{'age': '1001', 'name': 'username1'},
                   {'age': '1002', 'name': 'username2'},
                   {'age': '1003', 'name': 'username3'}]
 
# test_answer_2()

def test_issue_20_answer():
    data_to_parse="""
(*, 239.100.100.100)    
    LISP0.4200, (192.2.101.65, 232.0.3.1), Forward/Sparse, 1d18h/stopped
    LISP0.4201, (192.2.101.70, 232.0.3.1), Forward/Sparse, 2d05h/stopped

(192.2.31.3, 239.100.100.100), 6d20h/00:02:23, flags: FT
  Incoming interface: Vlan1029, RPF nbr 0.0.0.0
  Outgoing interface list:
    LISP0.4100, (192.2.101.70, 232.0.3.1), Forward/Sparse, 1d18h/stopped

"""

    show_mcast1="""
<template name="mcast" results="per_template">
<group name="mcast_entries.{{ overlay_src }}">
({{ overlay_src | _start_ | replace("*", "'*'")}}, {{ overlay_grp | IP }})
({{ overlay_src | _start_ | IP }}, {{ overlay_grp | IP }}), {{ entry_uptime }}/{{ entry_state_or_timer }}, flags: {{ entry_flags }}
  Incoming interface: {{ incoming_intf }}, RPF nbr {{ rpf_neighbor }}
    <group name="oil_entries*">
    {{ outgoing_intf }}, ({{ underlay_src | IP }}, {{ underlay_grp | IP }}), Forward/Sparse, {{ oil_uptime }}/{{ oil_state_or_timer}}  
    </group>
</group>
</template>
"""
    parser = ttp(template=show_mcast1)
    parser.add_input(data_to_parse, template_name="mcast")
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res, width=100)
    assert res == {'mcast': {'mcast_entries': {"'*'": {'oil_entries': [{'oil_state_or_timer': 'stopped',
                                                                       'oil_uptime': '1d18h',
                                                                       'outgoing_intf': 'LISP0.4200',
                                                                       'underlay_grp': '232.0.3.1',
                                                                       'underlay_src': '192.2.101.65'},
                                                                      {'oil_state_or_timer': 'stopped',
                                                                       'oil_uptime': '2d05h',
                                                                       'outgoing_intf': 'LISP0.4201',
                                                                       'underlay_grp': '232.0.3.1',
                                                                       'underlay_src': '192.2.101.70'}],
                                                      'overlay_grp': '239.100.100.100'},
                                              '192.2.31.3': {'entry_flags': 'FT',
                                                             'entry_state_or_timer': '00:02:23',
                                                             'entry_uptime': '6d20h',
                                                             'incoming_intf': 'Vlan1029',
                                                             'oil_entries': [{'oil_state_or_timer': 'stopped',
                                                                              'oil_uptime': '1d18h',
                                                                              'outgoing_intf': 'LISP0.4100',
                                                                              'underlay_grp': '232.0.3.1',
                                                                              'underlay_src': '192.2.101.70'}],
                                                             'overlay_grp': '239.100.100.100',
                                                             'rpf_neighbor': '0.0.0.0'}}}}
# test_issue_20_answer()

def test_answer_3():
    """
    Fixed bug with results forming - when have two _start_ matches, but 
    one of them is False, TTP was selecting first match without checking 
    if its False, updated decision logic to do that check.
    """
    data = """
/c/slb/virt 12
    dis
    ipver v4
    vip 1.1.1.1
    rtsrcmac ena
    vname "my name"
/c/slb/virt 12/service 443 https
    group 15
    rport 443
    pbind clientip
    dbind forceproxy
/c/slb/virt 12/service 443 https/http
    xforward ena
    httpmod hsts_insert
/c/slb/virt 12/service 443 https/ssl
    srvrcert cert certname
    sslpol ssl-Policy
/c/slb/virt 12/service 80 http
    group 15
    rport 80
    pbind clientip
    dbind forceproxy
/c/slb/virt 12/service 80 http/http
    xforward ena
    
/c/slb/virt 14
    dis
    ipver v4
    vip 1.1.4.4
    rtsrcmac ena
    vname "my name2"
    """
    template="""
<template name="VIP_cfg" results="per_template">
<group name="{{ vip }}">
/c/slb/virt {{ virt_seq | DIGIT }}
    dis {{ config_state | set("dis") }}
    ipver {{ ipver}}
    vip {{ vip }}
    rtsrcmac {{ rtsrcmac }}
    vname "{{ vip_name | ORPHRASE }}"
    
<group name="services.{{ port }}.{{ proto }}">
/c/slb/virt 12/service {{ port | DIGIT }} {{ proto | exclude(ssl) }}
    group {{group_seq }}
    rport {{ real_port }}
    pbind {{ pbind }}
    dbind {{ dbind }}
    xforward {{ xforward }}
    httpmod {{ httpmod }}
</group>    

<group name="ssl_profile">
/c/slb/virt {{ virt_seq }}/service 443 https/ssl
    srvrcert cert {{ ssl_server_cert }}
    sslpol {{ ssl_profile }}    
    {{ ssl | set("https/ssl") }}
</group>   

</group>  
</template> 
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res, width=50)    
    assert res == {'VIP_cfg': {'1.1.1.1': {'config_state': 'dis',
                                           'ipver': 'v4',
                                           'rtsrcmac': 'ena',
                                           'services': {'443': {'https': {'dbind': 'forceproxy',
                                                                          'group_seq': '15',
                                                                          'pbind': 'clientip',
                                                                          'real_port': '443'},
                                                                'https/http': {'httpmod': 'hsts_insert',
                                                                               'xforward': 'ena'}},
                                                        '80': {'http': {'dbind': 'forceproxy',
                                                                        'group_seq': '15',
                                                                        'pbind': 'clientip',
                                                                        'real_port': '80'},
                                                               'http/http': {'xforward': 'ena'}}},
                                           'ssl_profile': {'ssl': 'https/ssl',
                                                           'ssl_profile': 'ssl-Policy',
                                                           'ssl_server_cert': 'certname',
                                                           'virt_seq': '12'},
                                           'vip_name': 'my name',
                                           'virt_seq': '12'},
                               '1.1.4.4': {'config_state': 'dis',
                                           'ipver': 'v4',
                                           'rtsrcmac': 'ena',
                                           'vip_name': 'my name2',
                                           'virt_seq': '14'}}}
                                           
# test_answer_3() 

def test_answer_4():
    data = """
/c/slb/virt 12
    dis
    ipver v4
    vip 1.1.1.1
    rtsrcmac ena
    vname "my name"
/c/slb/virt 12/service 443 https
    group 15
    rport 443
    pbind clientip
    dbind forceproxy
/c/slb/virt 12/service 443 https/http
    xforward ena
    httpmod hsts_insert
/c/slb/virt 12/service 443 https/ssl
    srvrcert cert certname
    sslpol ssl-Policy
/c/slb/virt 12/service 80 http
    group 15
    rport 80
    pbind clientip
    dbind forceproxy
/c/slb/virt 12/service 80 http/http
    xforward ena
    
/c/slb/virt 14
    dis
    ipver v4
    vip 1.1.4.4
    rtsrcmac ena
    vname "my name2"
    """
    template="""
<template name="VIP_cfg" results="per_template">
<group name="{{ vip }}">
/c/slb/virt {{ virt_seq | DIGIT }}
    dis {{ config_state | set("dis") }}
    ipver {{ ipver}}
    vip {{ vip }}
    rtsrcmac {{ rtsrcmac }}
    vname "{{ vip_name | ORPHRASE }}"
    
<group name="services.{{ port }}" contains="dbind, pbind">
/c/slb/virt 12/service {{ port | DIGIT }} {{ proto | exclude(ssl) }}
    group {{group_seq }}
    rport {{ real_port }}
    pbind {{ pbind }}
    dbind {{ dbind }}
    xforward {{ xforward }}
    httpmod {{ httpmod }}
</group>    

<group name="ssl_profile">
/c/slb/virt {{ virt_seq }}/service 443 https/ssl
    srvrcert cert {{ ssl_server_cert }}
    sslpol {{ ssl_profile }}    
    {{ ssl | set("https/ssl") }}
</group>   

</group>  
</template> 
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res, width=50)    
    assert res == {'VIP_cfg': {'1.1.1.1': {'config_state': 'dis',
                                           'ipver': 'v4',
                                           'rtsrcmac': 'ena',
                                           'services': {'443': {'dbind': 'forceproxy',
                                                                'group_seq': '15',
                                                                'pbind': 'clientip',
                                                                'proto': 'https',
                                                                'real_port': '443'},
                                                        '80': {'dbind': 'forceproxy',
                                                               'group_seq': '15',
                                                               'pbind': 'clientip',
                                                               'proto': 'http',
                                                               'real_port': '80'}},
                                           'ssl_profile': {'ssl': 'https/ssl',
                                                           'ssl_profile': 'ssl-Policy',
                                                           'ssl_server_cert': 'certname',
                                                           'virt_seq': '12'},
                                           'vip_name': 'my name',
                                           'virt_seq': '12'},
                               '1.1.4.4': {'config_state': 'dis',
                                           'ipver': 'v4',
                                           'rtsrcmac': 'ena',
                                           'vip_name': 'my name2',
                                           'virt_seq': '14'}}}
    
# test_answer_4()

def test_issue_20_answer_2():
    data_to_parse="""
(*, 239.100.100.101)    
    LISP0.4200, (192.2.101.65, 232.0.3.1), Forward/Sparse, 1d18h/stopped
    LISP0.4201, (192.2.101.70, 232.0.3.1), Forward/Sparse, 2d05h/stopped
    
(192.2.31.3, 239.100.100.100), 2d05h/00:01:19, flags: FT
  Incoming interface: Vlan1029, RPF nbr 0.0.0.0
  Outgoing interface list:
    LISP0.4100, (192.2.101.70, 232.0.3.1), Forward/Sparse, 2d05h/stopped
    LISP0.4101, (192.2.101.70, 232.0.3.1), Forward/Sparse, 2d05h/stopped

(*, 239.100.100.100), 6d20h/00:03:28, RP 192.2.199.1, flags: S
  Incoming interface: Null, RPF nbr 0.0.0.0
  Outgoing interface list:
    Vlan3014, Forward/Sparse, 1d18h/00:03:28
    LISP0.4100, (192.2.101.65, 232.0.3.1), Forward/Sparse, 1d18h/stopped
"""
    show_mcast1="""
<template name="mcast" results="per_template">
<group name="mcast_entries.{{ overlay_src }}">
({{ overlay_src | _start_ | replace("*", "'*'") }}, {{ overlay_grp | IP }})
({{ overlay_src | _start_ | IP }},                  {{ overlay_grp | IP }}), {{ entry_uptime }}/{{ entry_state_or_timer }}, flags: {{ entry_flags }}
({{ overlay_src | _start_ | replace("*", "'*'") }}, {{ overlay_grp | IP }}), {{ entry_uptime }}/{{ entry_state_or_timer }}, RP {{ rp }}, flags: {{ entry_flags }}
  Incoming interface: {{ incoming_intf }}, RPF nbr {{ rpf_neighbor }}
    <group name="oil_entries*">
    {{ outgoing_intf }}, Forward/Sparse,  {{ oil_uptime }}/{{ oil_state_or_timer}}
    {{ outgoing_intf }}, ({{ underlay_src | IP }}, {{ underlay_grp | IP }}), Forward/Sparse, {{ oil_uptime }}/{{ oil_state_or_timer}}  
    </group>
</group>
</template>
"""
    parser = ttp(template=show_mcast1)
    parser.add_input(data_to_parse, template_name="mcast")
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res, width=100)
    assert res  == {'mcast': {'mcast_entries': {"'*'": [{'overlay_grp': '239.100.100.101'},
                                                        {'entry_flags': 'S',
                                                         'entry_state_or_timer': '00:03:28',
                                                         'entry_uptime': '6d20h',
                                                         'incoming_intf': 'Null',
                                                         'oil_entries': [{'oil_state_or_timer': '00:03:28',
                                                                          'oil_uptime': '1d18h',
                                                                          'outgoing_intf': 'Vlan3014',
                                                                          'underlay_grp': '232.0.3.1',
                                                                          'underlay_src': '192.2.101.65'}],
                                                         'overlay_grp': '239.100.100.100',
                                                         'rp': '192.2.199.1',
                                                         'rpf_neighbor': '0.0.0.0'}],
                                                '192.2.31.3': {'entry_flags': 'FT',
                                                               'entry_state_or_timer': '00:01:19',
                                                               'entry_uptime': '2d05h',
                                                               'incoming_intf': 'Vlan1029',
                                                               'overlay_grp': '239.100.100.100',
                                                               'rpf_neighbor': '0.0.0.0'}}}}
# test_issue_20_answer_2()

def test_docs_ttp_dictionary_usage_example():
    template = """
<input load="text">
interface Lo0
 ip address 124.171.238.50/29
!
interface Lo1
 ip address 1.1.1.1/30
</input>

<group macro="add_last_host">
interface {{ interface }}
 ip address {{ ip }}
</group>

<macro>
def add_last_host(data):
    ip_obj, _ = _ttp_["match"]["to_ip"](data["ip"])
    all_ips = list(ip_obj.network.hosts())
    data["last_host"] = str(all_ips[-1])
    return data
</macro>
"""
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interface': 'Lo0',
                      'ip': '124.171.238.50/29',
                      'last_host': '124.171.238.54'},
                     {'interface': 'Lo1', 'ip': '1.1.1.1/30', 'last_host': '1.1.1.2'}]]]
    
# test_docs_ttp_dictionary_usage_example()

def test_github_issue_21_answer():
    data_to_parse="""
R1#sh ip nbar protocol-discovery protocol 

 GigabitEthernet1 

 Last clearing of "show ip nbar protocol-discovery" counters 00:13:45


                              Input                    Output                  
                              -----                    ------                  
 Protocol                     Packet Count             Packet Count            
                              Byte Count               Byte Count              
                              5min Bit Rate (bps)      5min Bit Rate (bps)     
                              5min Max Bit Rate (bps)  5min Max Bit Rate (bps) 
 ---------------------------- ------------------------ ------------------------
 ssh                          191                      134                     
                              24805                    22072                   
                              2000                     1000                    
                              1999                     1001                    
 unknown                      172                      503                     
                              39713                    31378                   
                              0                        0                       
                              3000                     0                       
 ping                         144                      144                     
                              14592                    14592                   
                              0                        0                       
                              1000                     1000                    
 dns                          107                      0                       
                              21149                    0                       
                              0                        0                       
                              2000                     0                       
 vrrp                         0                        738                     
                              0                        39852                   
                              0                        0                       
                              0                        0                       
 ldp                          174                      175                     
                              13224                    13300                   
                              0                        0                       
                              0                        0                       
 ospf                         86                       87                      
                              9460                     9570                    
                              0                        0                       
                              0                        0                       
 Total                        874                      1781                    
                              122943                   130764                  
                              2000                     1000                    
                              8000                     2000 
"""
    show_nbar = """
<template name="nbar" results="per_template">

<vars>C1 = "DIGIT | to_int | to_list | joinmatches"</vars>

<group name="{{ interface }}">
 {{ interface | re('Gig.+') | re('Ten.+') }}
 <group name="{{ protocol }}" macro="map_to_keys">
 {{ protocol }}               {{ in | chain(C1) }} {{ out | chain(C1) }}
{{ ignore(r"\\s+") }}           {{ in | chain(C1) }} {{ out | chain(C1) }} 
 </group>
</group>

<macro>
def map_to_keys(data):
    # uncomment to see data 
    # print(data)
    inp_values = data.pop("in")
    out_values = data.pop("out")
    inp_keys = ["IN Packet Count", "IN Byte Count", "IN 5min Bit Rate (bps)", "IN 5min Max Bit Rate (bps)"]
    out_keys = ["OUT Packet Count", "OUT Byte Count", "OUT 5min Bit Rate (bps)", "OUT 5min Max Bit Rate (bps)"]
    data.update(dict(zip(inp_keys, inp_values)))
    data.update(dict(zip(out_keys, out_values))) 
    return data
</macro>
</template>      
    """
    parser = ttp(template=show_nbar)
    parser.add_input(data_to_parse, template_name="nbar")
    parser.parse()
    res = parser.result(structure="dictionary")
    pprint.pprint(res, width=100)
    assert res == {'nbar': {'GigabitEthernet1 ': {'Total': {'IN 5min Bit Rate (bps)': 2000,
                                          'IN 5min Max Bit Rate (bps)': 8000,
                                          'IN Byte Count': 122943,
                                          'IN Packet Count': 874,
                                          'OUT 5min Bit Rate (bps)': 1000,
                                          'OUT 5min Max Bit Rate (bps)': 2000,
                                          'OUT Byte Count': 130764,
                                          'OUT Packet Count': 1781},
                                'dns': {'IN 5min Bit Rate (bps)': 0,
                                        'IN 5min Max Bit Rate (bps)': 2000,
                                        'IN Byte Count': 21149,
                                        'IN Packet Count': 107,
                                        'OUT 5min Bit Rate (bps)': 0,
                                        'OUT 5min Max Bit Rate (bps)': 0,
                                        'OUT Byte Count': 0,
                                        'OUT Packet Count': 0},
                                'ldp': {'IN 5min Bit Rate (bps)': 0,
                                        'IN 5min Max Bit Rate (bps)': 0,
                                        'IN Byte Count': 13224,
                                        'IN Packet Count': 174,
                                        'OUT 5min Bit Rate (bps)': 0,
                                        'OUT 5min Max Bit Rate (bps)': 0,
                                        'OUT Byte Count': 13300,
                                        'OUT Packet Count': 175},
                                'ospf': {'IN 5min Bit Rate (bps)': 0,
                                         'IN 5min Max Bit Rate (bps)': 0,
                                         'IN Byte Count': 9460,
                                         'IN Packet Count': 86,
                                         'OUT 5min Bit Rate (bps)': 0,
                                         'OUT 5min Max Bit Rate (bps)': 0,
                                         'OUT Byte Count': 9570,
                                         'OUT Packet Count': 87},
                                'ping': {'IN 5min Bit Rate (bps)': 0,
                                         'IN 5min Max Bit Rate (bps)': 1000,
                                         'IN Byte Count': 14592,
                                         'IN Packet Count': 144,
                                         'OUT 5min Bit Rate (bps)': 0,
                                         'OUT 5min Max Bit Rate (bps)': 1000,
                                         'OUT Byte Count': 14592,
                                         'OUT Packet Count': 144},
                                'ssh': {'IN 5min Bit Rate (bps)': 2000,
                                        'IN 5min Max Bit Rate (bps)': 1999,
                                        'IN Byte Count': 24805,
                                        'IN Packet Count': 191,
                                        'OUT 5min Bit Rate (bps)': 1000,
                                        'OUT 5min Max Bit Rate (bps)': 1001,
                                        'OUT Byte Count': 22072,
                                        'OUT Packet Count': 134},
                                'unknown': {'IN 5min Bit Rate (bps)': 0,
                                            'IN 5min Max Bit Rate (bps)': 3000,
                                            'IN Byte Count': 39713,
                                            'IN Packet Count': 172,
                                            'OUT 5min Bit Rate (bps)': 0,
                                            'OUT 5min Max Bit Rate (bps)': 0,
                                            'OUT Byte Count': 31378,
                                            'OUT Packet Count': 503},
                                'vrrp': {'IN 5min Bit Rate (bps)': 0,
                                         'IN 5min Max Bit Rate (bps)': 0,
                                         'IN Byte Count': 0,
                                         'IN Packet Count': 0,
                                         'OUT 5min Bit Rate (bps)': 0,
                                         'OUT 5min Max Bit Rate (bps)': 0,
                                         'OUT Byte Count': 39852,
                                         'OUT Packet Count': 738}}}}
                                         
# test_github_issue_21_answer()

def test_github_issue_22():
    data = """
interface Loopback0
 description Fabric Node Router ID
 ip address 192.2.101.70 255.255.255.255
 ip pim sparse-mode
 ip router isis 
 clns mtu 1400
end
interface Loopback0
 description Fabric Node Router ID
 ip address 192.2.101.71 255.255.255.255
 ip pim sparse-mode
 ip router isis 
 clns mtu 1400
end
    """
    template = """{{ ignore(r"\\s+") }}ip address {{ ip_address }} 255.255.255.255"""
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=100) 
    assert res == [[[{'ip_address': '192.2.101.70'}, {'ip_address': '192.2.101.71'}]]]
    
# test_github_issue_22()

def test_github_issue_24():
    data = """
19: IP4 1.1.1.1,   00:03:b2:78:04:13, vname portal, NO SERVICES UP
    Virtual Services:
    http: rport http, group 11, health http (HTTP), pbind clientip
        Real Servers:
        22: 10.10.10.10, web1, group ena, health  (runtime HTTP), 0 ms, FAILED
            Reason: N/A
        23: 10.11.11.11, web2, group ena, health  (runtime HTTP), 0 ms, FAILED
            Reason: N/A
    https: rport https, group 12, health tcp (TCP), pbind clientip
        Real Servers:
        22: 10.10.10.10, web1, group ena, health  (runtime TCP), 0 ms, FAILED
            Reason: N/A
        23: 10.11.11.11, web2, group ena, health  (runtime TCP), 0 ms, FAILED
            Reason: N/A
    """
    template = """
<template name="VIP_cfg" results="per_template">
<group name="{{ vs_instance }}" default="">
{{ vs_instance }}: IP4 {{ vs_ip }},{{ ignore(".+") }}
<group name="services*" default="">
    {{ vs_service }}: rport {{ rport }},{{ ignore(".+") }}
<group name="pool*" default="">
        {{ node_id }}: {{ node_ip }},{{ ignore(".+") }}
            Reason: {{ reason }}
</group>
</group>
</group>
</template>    
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result(structure="dictionary")
    # pprint.pprint(res, width=100) 
    assert res == {'VIP_cfg': {'19': {'services': [{'pool': [{'node_id': '22',
                                                              'node_ip': '10.10.10.10',
                                                              'reason': 'N/A'},
                                                             {'node_id': '23',
                                                              'node_ip': '10.11.11.11',
                                                              'reason': 'N/A'}],
                                                    'rport': 'http',
                                                    'vs_service': 'http'},
                                                   {'pool': [{'node_id': '22',
                                                              'node_ip': '10.10.10.10',
                                                              'reason': 'N/A'},
                                                             {'node_id': '23',
                                                              'node_ip': '10.11.11.11',
                                                              'reason': 'N/A'}],
                                                    'rport': 'https',
                                                    'vs_service': 'https'}],
                                      'vs_ip': '1.1.1.1'}}}
    
# test_github_issue_24()

def test_reddit_answer_1():
    """
    https://www.reddit.com/r/networking/comments/j106ot/export_custom_lists_from_the_config_aruba_switch/
    
    Hit a bug while was doing this template - join action overridden by ignore indicator add action
    """
    data = """
SWITCH# show vlan port 2/11 detail

Status and Counters - VLAN Information - for ports 2/11

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

60 ABC | Port-based No No Tagged

70 DEF | Port-based No No Tagged

101 GHIJ | Port-based No No Untagged

105 KLMNO | Port-based No No Tagged

116 PQRS | Port-based No No Tagged

117 TVU | Port-based No No Tagged

SWITCH# show vlan port 2/12 detail

Status and Counters - VLAN Information - for ports 2/12

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

61 ABC | Port-based No No Tagged

71 DEF | Port-based No No Tagged

103 GHI | Port-based No No Untagged
    """
    template = """
<vars>
hostname="gethostname"
</vars>

<group name="vlans*">
Status and Counters - VLAN Information - for ports {{ Port_Number }}
{{ Tagged_VLAN | joinmatches(" ") }} {{ ignore }} | {{ ignore }} {{ ignore }} {{ ignore }} Tagged
{{ Untagged_VLAN }}                  {{ ignore }} | {{ ignore }} {{ ignore }} {{ ignore }} Untagged
{{ Hostname | set(hostname) }}
</group>   

<output>
format = "csv"
path = "vlans"
headers = "Hostname, Port_Number, Untagged_VLAN, Tagged_VLAN"
</output>
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    # print(res)
    assert res == ['"Hostname","Port_Number","Untagged_VLAN","Tagged_VLAN"\n"SWITCH","2/11","101","60 70 105 116 117"\n"SWITCH","2/12","103","61 71"']
    
# test_reddit_answer_1()

def test_reddit_answer_2():
    data = """
config router ospf
    set abr-type standard
    set auto-cost-ref-bandwidth 1000
    set distance-external 110
    set distance-inter-area 110
    set distance-intra-area 110
    set database-overflow disable
    set database-overflow-max-lsas 10000
    set database-overflow-time-to-recover 300
    set default-information-originate disable
    set default-information-metric 10
    set default-information-metric-type 2
    set default-information-route-map ''
    set default-metric 10
    set distance 110
    set rfc1583-compatible disable
    set router-id 10.1.1.1
    set spf-timers 5 10
    set bfd disable
    set log-neighbour-changes enable
    set distribute-list-in "OSPF_IMPORT_PREFIX"
    set distribute-route-map-in ''
    set restart-mode none
    set restart-period 120
    config area
        edit 0.0.0.1
            set shortcut disable
            set authentication none
            set default-cost 10
            set nssa-translator-role candidate
            set stub-type summary
            set type nssa
            set nssa-default-information-originate disable
            set nssa-default-information-originate-metric 10
            set nssa-default-information-originate-metric-type 2
            set nssa-redistribution enable
        next
    end
    config ospf-interface
        edit "vlan1-int"
            set interface "Vlan1"
            set ip 0.0.0.0
            set authentication text
            set authentication-key netconanRemoved13
            set prefix-length 0
            set retransmit-interval 5
            set transmit-delay 1
            set cost 0
            set priority 1
            set dead-interval 40
            set hello-interval 10
            set hello-multiplier 0
            set database-filter-out disable
            set mtu 0
            set mtu-ignore disable
            set network-type point-to-point
            set bfd global
            set status enable
            set resync-timeout 40
        next
        edit "vlan2-int"
            set interface "vlan2"
            set ip 0.0.0.0
            set authentication text
            set authentication-key netconanRemoved14
            set prefix-length 0
            set retransmit-interval 5
            set transmit-delay 1
            set cost 0
            set priority 1
            set dead-interval 40
            set hello-interval 10
            set hello-multiplier 0
            set database-filter-out disable
            set mtu 0
            set mtu-ignore disable
            set network-type point-to-point
            set bfd global
            set status enable
            set resync-timeout 40
        next
    end
    config network
        edit 1
            set prefix 10.1.1.1 255.255.255.252
            set area 0.0.0.1
        next
        edit 2
            set prefix 10.1.1.3 255.255.255.252
            set area 0.0.0.1
        next
    end
    config redistribute "connected"
        set status enable
        set metric 0
        set routemap ''
        set metric-type 2
        set tag 0
    end
    config redistribute "static"
        set status enable
        set metric 0
        set routemap ''
        set metric-type 2
        set tag 0
    end
    config redistribute "rip"
        set status disable
        set metric 0
        set routemap ''
        set metric-type 2
        set tag 0
    end
    config redistribute "bgp"
        set status enable
        set metric 0
        set routemap ''
        set metric-type 2
        set tag 0
    end
    config redistribute "isis"
        set status disable
        set metric 0
        set routemap ''
        set metric-type 2
        set tag 0
    end
end
    """
    template = """
<vars>
clean_phrase = [
    'ORPHRASE',
    'macro(\"clean_str\")'
]
clean_list = [
    'ORPHRASE',
    'macro(\"build_list\")'
]
</vars>
<macro>
def build_list(data):
    if "\\" \\"" in data:
        t = data.split("\\" \\"")
        for i in range(0, len(t)):
            t[i] = t[i].strip("\\"").replace(" ", "_")
            i+=1
        return t
    else:
        return [data.strip("\\"").replace(" ", "_")]
def clean_str(data):
    return data.replace("\\"","").replace(" ", "_")
def match_ip_or_any(data):
    import ipaddress
    if data == \"any\":
        return data
    elif "/" in data:
        return str(data)
    else:    
        t = data.replace(" ", "/")
        return str(ipaddress.IPv4Network(t, strict=False))
def ignore_empty(data):
    if data == "\'\'":
        return bool(False)
    else:
        return data
</macro>
<macro>
def skip_empty(data):
    if data == {}:
        return False
    return data
</macro>
<group name="ospf">
config router ospf {{ _start_ }}
    set auto-cost-ref-bandwidth {{ ref_bw }}
    set default-information-originate {{ default_originate | contains("enable") }}
    set default-information-metric {{ default_originate_metric }}
    set default-information-metric-type {{ default_originate_metric_type }}
    set default-information-route-map {{ default_originate_routemap | chain("clean_phrase") | macro("ignore_empty") }}
    set default-metric {{ default_rt_metric }} 
    set rfc1583-compatible {{ rfc1583_compat | contains("enable") }}
    set router-id {{ router_id }}  
    set distribute-list-in {{ dist_list_in | chain("clean_phrase") | macro("ignore_empty") }} 
    set distribute-route-map-in {{ dist_routemap_in | chain("clean_phrase") | macro("ignore_empty") }} 
    <group name="areas*" macro="skip_empty">
    config area {{ _start_ }}
        <group>
        edit {{ area | _start_ }}
            set stub-type {{ stub_type }}
            set type {{ area_type }}
            set nssa-default-information-originate {{ nssa_default_originate | contains("enable") }}
            set nssa-default-information-originate-metric {{ nssa_default_metric }}
            set nssa-default-information-originate-metric-type {{ nssa_default_metric_type }}
            set nssa-redistribution {{ nssa_redis }}
        next {{ _end_ }}
        </group>
    end {{ _end_ }}
    </group>
    <group name="interfaces*" macro="skip_empty">
    config ospf-interface {{ _start_ }}
        <group contains="status">
        edit {{ name | chain("clean_phrase") | _start_ }}
            set interface {{ interface | chain("clean_phrase")}} 
            set ip {{ ip | exclude("0.0.0.0") }}
            set cost {{ cost | exclude("0") }}
            set priority {{ priority }}
            set mtu {{ mtu | exclude("0") }}
            set network-type {{ network }} 
            set status {{ status | contains("enable") }}
        next {{ _end_ }}
        </group>
    end {{ _end_ }}
    </group>
    <group name="networks*" macro="skip_empty">
    config network {{ _start_ }}
        <group>
        edit {{ id | _start_ }}
            set prefix {{ prefix | ORPHRASE | to_ip | with_prefixlen }} 
            set area {{ area }} 
        next {{ _end_ }}
        </group>
    end {{ _end_ }}
    </group>
    <group name="redistribute*" contains="status">
    config redistribute {{ protocol | chain("clean_phrase") | _start_ }}
        set status {{ status | contains('enable') }}
        set route-map {{ route_map | chain("clean_phrase") | macro("ignore_empty") }}
        set metric-type {{ metric-type }} 
        set metric {{ metric | exclude("0") }}
        set tag {{ tag | exclude("0")}}
    end {{ _end_ }}
    </group>
end {{ _end_ }}
</group>
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'ospf': {'areas': [{'area': '0.0.0.1',
                       'area_type': 'nssa',
                       'nssa_default_metric': '10',
                       'nssa_default_metric_type': '2',
                       'nssa_redis': 'enable',
                       'stub_type': 'summary'}],
            'default_originate_metric': '10',
            'default_originate_metric_type': '2',
            'default_rt_metric': '10',
            'dist_list_in': 'OSPF_IMPORT_PREFIX',
            'interfaces': [{'interface': 'Vlan1',
                            'name': 'vlan1-int',
                            'network': 'point-to-point',
                            'priority': '1',
                            'status': 'enable'},
                           {'interface': 'vlan2',
                            'name': 'vlan2-int',
                            'network': 'point-to-point',
                            'priority': '1',
                            'status': 'enable'}],
            'networks': [{'area': '0.0.0.1',
                          'id': '1',
                          'prefix': '10.1.1.1/30'},
                         {'area': '0.0.0.1',
                          'id': '2',
                          'prefix': '10.1.1.3/30'}],
            'redistribute': [{'metric-type': '2',
                              'protocol': 'connected',
                              'status': 'enable'},
                             {'metric-type': '2',
                              'protocol': 'static',
                              'status': 'enable'},
                             {'metric-type': '2',
                              'protocol': 'bgp',
                              'status': 'enable'}],
            'ref_bw': '1000',
            'router_id': '10.1.1.1'}}]]

# test_reddit_answer_2()

def test_github_issue_32():
    data = """
.id=*c;export-route-targets=65001:48;65001:0;import-route-targets=65001:48;interfaces=lo-ext;vlan56;route-distinguisher=65001:48;routing-mark=VRF_EXT
.id=*10;comment=;export-route-targets=65001:80;import-route-targets=65001:80;65001:0;interfaces=lo-private;route-distinguisher=65001:80;routing-mark=VRF_PRIVATE
    """
    template = """
<group method="table">
.id={{ id | exclude(";") }};export-route-targets={{ export-route-targets }};import-route-targets={{ import-route-targets }};interfaces={{ interfaces }};route-distinguisher={{ route-distinguisher }};routing-mark={{ routing-mark }}
.id={{ id }};comment{{ comment }};export-route-targets={{ export-route-targets }};import-route-targets={{ import-route-targets }};interfaces={{ interfaces }};route-distinguisher={{ route-distinguisher }};routing-mark={{ routing-mark }}
</group>
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result(structure="flat_list")
    # pprint.pprint(res)
    assert res == [{'export-route-targets': '65001:48;65001:0',
                    'id': '*c',
                    'import-route-targets': '65001:48',
                    'interfaces': 'lo-ext;vlan56',
                    'route-distinguisher': '65001:48',
                    'routing-mark': 'VRF_EXT'},
                   {'comment': '=',
                    'export-route-targets': '65001:80',
                    'id': '*10',
                    'import-route-targets': '65001:80;65001:0',
                    'interfaces': 'lo-private',
                    'route-distinguisher': '65001:80',
                    'routing-mark': 'VRF_PRIVATE'}]

# test_github_issue_32()

def test_slack_answer_1():
    data = """
Firmware
Version
----------------
02.1.1 Build 002

Hardware
Version
----------------
V2R4
    """
    template = """
<group name="versions">
Hardware {{ _start_ }}
Firmware {{ _start_ }}
{{ version | PHRASE | let("type", "firmware") }}
{{ version | exclude("---") | exclude("Vers") | let("type", "hardware") }}
{{ _end_ }}
</group>    
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result(structure="flat_list")
    # pprint.pprint(res)
    assert res == [{'versions': [{'type': 'firmware', 'version': '02.1.1 Build 002'},
                                 {'type': 'hardware', 'version': 'V2R4'}]}]
               
# test_slack_answer_1()

def test_group_default_docs():
    template = """
<input load="text">
device-hostame uptime is 27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds
</input>

<group name="uptime**">
device-hostame uptime is {{ uptime | PHRASE }}
    <group name="software">
     software version {{ version | default("uncknown") }}
    </group>
</group>

<group name="domain" default="Uncknown">
Default domain is {{ fqdn }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)  
    assert res == [[{'domain': {'fqdn': 'Uncknown'},
                     'uptime': {'software': {'version': 'uncknown'},
                                'uptime': '27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds'}}]]
              
# test_group_default_docs()

def test_github_issue_34_answer():
    template = """
<input load="text">
Hi World
</input>

<group name='demo'>
<group name='audiences*'>
Hello {{ audience | default([]) }}
</group>
</group>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'demo': {'audiences': [{'audience': []}]}}]]
    
# test_github_issue_34_answer()

def test_github_issue_33_answer_1():
    template = """
<input load="text">
server 1.1.1.1
server 2.2.2.2 3.3.3.3
server 4.4.4.4 5.5.5.5 6.6.6.6
</input>

<group name="servers" method="table">
server {{ server | re(r"\\S+") | let("servers_number", 1 ) }}
server {{ server | re(r"\\S+ \\S+") | let("servers_number", 2) }}
server {{ server | re(r"\\S+ \\S+ \\S+") | let("servers_number", 3) }}
</group>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'servers': [{'server': '1.1.1.1', 'servers_number': 1},
                                 {'server': '2.2.2.2 3.3.3.3', 'servers_number': 2},
                                 {'server': '4.4.4.4 5.5.5.5 6.6.6.6', 'servers_number': 3}]}]]
                    
# test_github_issue_33_answer_1()

def test_issue_36():
    template = """
<input load="text">
ip access-list standard 42
 10 remark machine_A
 10 permit 192.168.200.162
 20 remark machine_B
 20 permit 192.168.200.149
 30 deny   any log
ip access-list standard 98
 10 permit 10.10.10.1
 20 remark toto
 20 permit 30.30.30.1
 30 permit 30.30.30.0 0.0.0.255
ip access-list standard 99
 10 permit 10.20.30.40 log
 20 permit 20.30.40.1 log
 30 remark DEVICE - SNMP RW
 30 permit 50.50.50.128 0.0.0.127
 40 permit 60.60.60.64 0.0.0.63
ip access-list extended 199
 10 remark COLLECTOR - SNMP
 10 permit ip 70.70.70.0 0.0.0.255 any
 20 remark RETURN - Back
 20 permit ip 80.80.80.0 0.0.0.127 any
 30 remark VISUALIZE
 30 permit ip host 90.90.90.138 any
</input>

<group name="ip.{{ acl_type }}.{{ acl_name }}">
ip access-list {{ acl_type }} {{ acl_name }}
 <group name="{{ entry_id }}*" method="table">
 {{ entry_id }} remark {{ remark_name | re(".+") | let("action", "remark") }}
 {{ entry_id }} {{ action }} {{ src_host }}
 {{ entry_id }} {{ action }} {{ src_host | let("log", "log") }} log
 {{ entry_id }} {{ action }} {{ protocol }} host {{ src_host | let("dest_any", "any") }} any
 {{ entry_id }} {{ action }} {{ protocol }} {{ src_ntw | let("dest_any", "any") }} {{ src_wildcard | IP }} any
 {{ entry_id }} {{ action }} {{ src_ntw }} {{ src_wildcard | IP }}
 </group>
</group>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    pprint.pprint(res) 
    assert res == [[{'ip': {'extended': {'199': {'10': [{'action': 'remark',
                                                         'remark_name': 'COLLECTOR - SNMP'},
                                                        {'action': 'permit',
                                                         'dest_any': 'any',
                                                         'protocol': 'ip',
                                                         'src_ntw': '70.70.70.0',
                                                         'src_wildcard': '0.0.0.255'}],
                                                 '20': [{'action': 'remark',
                                                         'remark_name': 'RETURN - Back'},
                                                        {'action': 'permit',
                                                         'dest_any': 'any',
                                                         'protocol': 'ip',
                                                         'src_ntw': '80.80.80.0',
                                                         'src_wildcard': '0.0.0.127'}],
                                                 '30': [{'action': 'remark',
                                                         'remark_name': 'VISUALIZE'},
                                                        {'action': 'permit',
                                                         'dest_any': 'any',
                                                         'protocol': 'ip',
                                                         'src_host': '90.90.90.138'}]}},
                            'standard': {'42': {'10': [{'action': 'remark',
                                                        'remark_name': 'machine_A'},
                                                       {'action': 'permit',
                                                        'src_host': '192.168.200.162'}],
                                                '20': [{'action': 'remark',
                                                        'remark_name': 'machine_B'},
                                                       {'action': 'permit',
                                                        'src_host': '192.168.200.149'}],
                                                '30': [{'action': 'deny',
                                                        'log': 'log',
                                                        'src_host': 'any'}]},
                                         '98': {'10': [{'action': 'permit',
                                                        'src_host': '10.10.10.1'}],
                                                '20': [{'action': 'remark',
                                                        'remark_name': 'toto'},
                                                       {'action': 'permit',
                                                        'src_host': '30.30.30.1'}],
                                                '30': [{'action': 'permit',
                                                        'src_ntw': '30.30.30.0',
                                                        'src_wildcard': '0.0.0.255'}]},
                                         '99': {'10': [{'action': 'permit',
                                                        'log': 'log',
                                                        'src_host': '10.20.30.40'}],
                                                '20': [{'action': 'permit',
                                                        'log': 'log',
                                                        'src_host': '20.30.40.1'}],
                                                '30': [{'action': 'remark',
                                                        'remark_name': 'DEVICE - SNMP RW'},
                                                       {'action': 'permit',
                                                        'src_ntw': '50.50.50.128',
                                                        'src_wildcard': '0.0.0.127'}],
                                                '40': [{'action': 'permit',
                                                        'src_ntw': '60.60.60.64',
                                                        'src_wildcard': '0.0.0.63'}]}}}}]]
    
# test_issue_36()

def test_github_issue_37_original_data_template():
    template = """
<macro>
import re
def qinq(data):
    data = re.sub(r"\\*", r"qinq", data)
    return data 
</macro>

<group name="service">
    service {{ ignore }}
    <group name="epipe.{{ service_id }}"  default="none">
        epipe {{ service_id | _start_ }} customer {{ customer_id }} create
            description "{{ description | ORPHRASE | default("none") }}"
            service-mtu {{ service_mtu | default("none") }}
            service-name "{{ service_name | ORPHRASE | default("none") }}"
        <group name="endpoint"  default="none">
            endpoint {{ endpoint | _start_ }} create
                revert-time {{ revert_time | default("none") }}
            exit {{ _end_ }}
        </group>     
        <group name="sap.{{ sap_id }}"  default="none">
            sap {{ sap_id | macro("qinq") | _start_ | ORPHRASE }} create
                description "{{ description | ORPHRASE | default("none")}}"
                multi-service-site "{{ mss_name | default("none") }}"
            <group name="ingress" default="default_ingress" >
                ingress {{ _start_ }}
                    qos {{ sap_ingress | default("1") }}                 
                    scheduler-policy {{ scheduler_policy | default("none")}}
                exit {{ _end_ }}
            </group>
            <group name="egress" default="default_egress">
                egress {{ _start_ }}
                    scheduler-policy {{ scheduler_policy | default("none") }}
                    qos {{ sap_egress | default("1)") }}
                exit {{ _end_ }}
            </group>
                no shutdown {{ state | set("enabled") | default("disabled") }}
            exit {{ _end_ }}
        </group>
        <group name="pwr_sdp.{{pwr_spoke_sdp_id}}**" default="none"> 
            spoke-sdp {{ pwr_spoke_sdp_id | default("none")}}:{{vc_id | _start_ | default("none") }} endpoint {{ endpoint | default("none") }} create             
                precedence {{ precedence | default("default_precedence") }}
                no shutdown {{ state | set("enabled") | default("disabled") }}
            exit {{ _end_ }}
        </group> 
        <group name="regular_sdp.{{r_spoke_sdp_id}}**" default="none"> 
            spoke-sdp {{ r_spoke_sdp_id }}:{{vc_id | _start_ }} create             
                no shutdown {{ state | set("enabled") | default("disabled") }}
            exit {{ _end_ }}
        </group> 
            no shutdown {{ state | set("enabled") | default("disabled") }}
        exit {{ _end_ }}
    </group>
    exit {{ _end_ }}
</group>
    """
    data = """
    service foo
        epipe 103076 customer 160 create
            description "vf=EWL:cn=TATA_COM:tl=2C02495918:st=act:"
            service-mtu 1588
            service-name "EPIPE service-103076 DKTN08a-D0105 (63.130.108.41)"
            sap 1/2/12:20.* create
                description "vf=EWL:cn=TATA_COM:tl=2C02495890:st=act:"
                multi-service-site "TATA_VSNL_STRAT_A206_LAN10"
                ingress
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 40 kilobytes
                            rate 10000 cir 10000
                        exit
                    exit
                exit
                egress
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 40 kilobytes
                            rate 10000 cir 10000
                        exit
                    exit
                exit
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8051:103076 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 103206 customer 1904 create
            description "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA UK PLC Stepney Green E1 3DG'"
            service-mtu 1988
            service-name "EPIPE service-103206 DKTN08a-D0105 (63.130.108.41)"
            sap 2/2/3:401.100 create
                description "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA UK PLC Stepney Green E1 3DG'"
                multi-service-site "SKANSKA_E13DG_A825_LAN1"
                ingress
                    qos 11010
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 1188 kilobytes
                            rate max cir 47500
                        exit
                        queue 3 create
                            cbs default
                            mbs 63 kilobytes
                            rate max cir 2500
                        exit
                    exit
                exit
                egress
                    qos 11010
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 1188 kilobytes
                            rate max cir 47500
                        exit
                        queue 3 create
                            cbs default
                            mbs 63 kilobytes
                            rate max cir 2500
                        exit
                    exit
                exit
                collect-stats
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8035:103206 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 103256 customer 160 create
            description "vf=EWL:cn=TATA_COMM:tl=2C02490189:st=act:"
            service-mtu 1988
            service-name "EPIPE service-103256 DKTN08a-D0105 (63.130.108.41)"
            sap 1/2/12:15.* create
                description "vf=EWL:cn=TATA_COMM:tl=2C02490171:st=act:"
                multi-service-site "TATA_VSNL_STRAT_A206_LAN5"
                ingress
                    qos 11000
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 391 kilobytes
                            rate 100000 cir 100000
                        exit
                    exit
                exit
                egress
                    qos 11000
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 391 kilobytes
                            rate 100000 cir 100000
                        exit
                    exit
                exit
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8139:103256 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 103742 customer 160 create
            description "vf=EWL:cn=TATA_COM:tl=2C02410363:st=act:"
            service-mtu 1588
            service-name "EPIPE service-103742 DKTN08a-D0105 (63.130.108.41)"
            sap 5/2/50:20.* create
                description "vf=EWL:cn=TATA_COM:tl=2C02410338:st=act:"
                multi-service-site "TATA_STRAT_LON_A206_LANA"
                ingress
                    qos 11000
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 32 kilobytes
                            rate 8000 cir 8000
                        exit
                    exit
                exit
                egress
                    qos 11000
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 32 kilobytes
                            rate 8000 cir 8000
                        exit
                    exit
                exit
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8061:103742 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 55513386 customer 4 vc-switching create
            description "vf=EAGG:cn=Bulldog:tl=VF"
            service-mtu 1526
            spoke-sdp 78:55513386 create
                control-word
                no shutdown
            exit
            spoke-sdp 8245:55513386 create
                control-word
                no shutdown
            exit
            no shutdown
        exit
        epipe 55517673 customer 4 create
            description "vf=EAGG:cn=Bulldog:tl=2C01291821:st=act:no=NGA EPIPE#BAACTQ#VLAN 901"
            service-mtu 1526
            service-name "epipe service-64585 DKTN08a-D0105 (63.130.108.41)"
            endpoint "SDP" create
                revert-time infinite
            exit
            sap 2/2/3:901.* create
                description "2_2_3,H0505824A,Bulldog,VLAN 901"
                ingress
                    scheduler-policy "NGA-LLU-300M"
                    qos 20010
                exit
                egress
                    scheduler-policy "NGA-LLU-300M"
                    qos 20010
                exit
                no shutdown
            exit
            spoke-sdp 8243:55517673 endpoint "SDP" create
                collect-stats
                precedence 1
                no shutdown
            exit
            spoke-sdp 8245:55517673 endpoint "SDP" create
                collect-stats
                precedence primary
                no shutdown
            exit
            no shutdown
        exit   
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'service': {'epipe': {'103076': {'customer_id': '160',
                                    'description': 'vf=EWL:cn=TATA_COM:tl=2C02495918:st=act:',
                                    'regular_sdp': {'8051': {'state': 'enabled',
                                                             'vc_id': '103076'}},
                                    'sap': {'1/2/12:20.qinq': {'description': 'vf=EWL:cn=TATA_COM:tl=2C02495890:st=act:',
                                                               'egress': {'sap_egress': '1)',
                                                                          'scheduler_policy': 'none'},
                                                               'ingress': {'sap_ingress': '1',
                                                                           'scheduler_policy': 'none'},
                                                               'mss_name': 'TATA_VSNL_STRAT_A206_LAN10',
                                                               'state': 'enabled'}},
                                    'service_mtu': '1588',
                                    'service_name': 'EPIPE service-103076 '
                                                    'DKTN08a-D0105 '
                                                    '(63.130.108.41)',
                                    'state': 'enabled'},
                         '103206': {'customer_id': '1904',
                                    'description': "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA "
                                                   'UK PLC Stepney Green E1 '
                                                   "3DG'",
                                    'regular_sdp': {'8035': {'state': 'enabled',
                                                             'vc_id': '103206'}},
                                    'sap': {'2/2/3:401.100': {'description': "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA "
                                                                             'UK '
                                                                             'PLC '
                                                                             'Stepney '
                                                                             'Green '
                                                                             'E1 '
                                                                             "3DG'",
                                                              'egress': {'sap_egress': '11010',
                                                                         'scheduler_policy': 'none'},
                                                              'ingress': {'sap_ingress': '11010',
                                                                          'scheduler_policy': 'none'},
                                                              'mss_name': 'SKANSKA_E13DG_A825_LAN1',
                                                              'state': 'disabled'}},
                                    'service_mtu': '1988',
                                    'service_name': 'EPIPE service-103206 '
                                                    'DKTN08a-D0105 '
                                                    '(63.130.108.41)',
                                    'state': 'enabled'},
                         '103256': {'customer_id': '160',
                                    'description': 'vf=EWL:cn=TATA_COMM:tl=2C02490189:st=act:',
                                    'regular_sdp': {'8139': {'state': 'enabled',
                                                             'vc_id': '103256'}},
                                    'sap': {'1/2/12:15.qinq': {'description': 'vf=EWL:cn=TATA_COMM:tl=2C02490171:st=act:',
                                                               'egress': {'sap_egress': '11000',
                                                                          'scheduler_policy': 'none'},
                                                               'ingress': {'sap_ingress': '11000',
                                                                           'scheduler_policy': 'none'},
                                                               'mss_name': 'TATA_VSNL_STRAT_A206_LAN5',
                                                               'state': 'disabled'}},
                                    'service_mtu': '1988',
                                    'service_name': 'EPIPE service-103256 '
                                                    'DKTN08a-D0105 '
                                                    '(63.130.108.41)',
                                    'state': 'enabled'},
                         '103742': {'customer_id': '160',
                                    'description': 'vf=EWL:cn=TATA_COM:tl=2C02410363:st=act:',
                                    'regular_sdp': {'8061': {'state': 'enabled',
                                                             'vc_id': '103742'}},
                                    'sap': {'5/2/50:20.qinq': {'description': 'vf=EWL:cn=TATA_COM:tl=2C02410338:st=act:',
                                                               'egress': {'sap_egress': '11000',
                                                                          'scheduler_policy': 'none'},
                                                               'ingress': {'sap_ingress': '11000',
                                                                           'scheduler_policy': 'none'},
                                                               'mss_name': 'TATA_STRAT_LON_A206_LANA',
                                                               'state': 'disabled'}},
                                    'service_mtu': '1588',
                                    'service_name': 'EPIPE service-103742 '
                                                    'DKTN08a-D0105 '
                                                    '(63.130.108.41)',
                                    'state': 'enabled'},
                         '55517673': {'customer_id': '4',
                                      'description': 'vf=EAGG:cn=Bulldog:tl=2C01291821:st=act:no=NGA '
                                                     'EPIPE#BAACTQ#VLAN 901',
                                      'endpoint': {'endpoint': '"SDP"',
                                                   'revert_time': 'infinite'},
                                      'pwr_sdp': {'8243': {'endpoint': '"SDP"',
                                                           'precedence': '1',
                                                           'state': 'enabled',
                                                           'vc_id': '55517673'},
                                                  '8245': {'endpoint': '"SDP"',
                                                           'precedence': 'primary',
                                                           'state': 'enabled',
                                                           'vc_id': '55517673'}},
                                      'sap': {'2/2/3:901.qinq': {'description': '2_2_3,H0505824A,Bulldog,VLAN '
                                                                                '901',
                                                                 'egress': {'sap_egress': '20010',
                                                                            'scheduler_policy': '"NGA-LLU-300M"'},
                                                                 'ingress': {'sap_ingress': '20010',
                                                                             'scheduler_policy': '"NGA-LLU-300M"'},
                                                                 'mss_name': 'none',
                                                                 'state': 'disabled'}},
                                      'service_mtu': '1526',
                                      'service_name': 'epipe service-64585 '
                                                      'DKTN08a-D0105 '
                                                      '(63.130.108.41)',
                                      'state': 'enabled'}}}}]]
    
# test_github_issue_37_original_data_template()

def test_github_issue_37_cleaned_up_data():
    """
    Problem with below template without bug fix, was that
    'no shutdown' statement for sap group was matched by 
    spoke-sdp group as well and added to results causing
    false match. To fix it, added tracking of previously
    started groups in results object, so that before add
    match results to overall results if PATH differ need
    to check that this particular item groups has been 
    started before, previous logic was not checking for that.
    
    Have not noticed any issues with other 200+ tests or
    any performance degradation for single/multi-process
    parsing.
    """
    template = """
<group name="service">
    service {{ ignore }}
    <group name="epipe.{{ service_id }}">
        epipe {{ service_id }} customer {{ customer_id }} create                    
            <group name="regular_sdp.{{r_spoke_sdp_id}}**"> 
            spoke-sdp {{ r_spoke_sdp_id }}:{{vc_id }} create             
                no shutdown {{ state | set("enabled") }}
            </group> 
        </group>
</group>
    """
    data = """
    service foo
        epipe 103076 customer 160 create
            description "vf=EWL:cn=TATA_COM:tl=2C02495918:st=act:"
            service-mtu 1588
            service-name "EPIPE service-103076 DKTN08a-D0105 (63.130.108.41)"
            sap 1/2/12:20.* create
                description "vf=EWL:cn=TATA_COM:tl=2C02495890:st=act:"
                multi-service-site "TATA_VSNL_STRAT_A206_LAN10"
                ingress
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 40 kilobytes
                            rate 10000 cir 10000
                        exit
                    exit
                exit
                egress
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 40 kilobytes
                            rate 10000 cir 10000
                        exit
                    exit
                exit
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8051:103076 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 103206 customer 1904 create
            description "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA UK PLC Stepney Green E1 3DG'"
            service-mtu 1988
            service-name "EPIPE service-103206 DKTN08a-D0105 (63.130.108.41)"
            sap 2/2/3:401.100 create
                description "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA UK PLC Stepney Green E1 3DG'"
                multi-service-site "SKANSKA_E13DG_A825_LAN1"
                ingress
                    qos 11010
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 1188 kilobytes
                            rate max cir 47500
                        exit
                        queue 3 create
                            cbs default
                            mbs 63 kilobytes
                            rate max cir 2500
                        exit
                    exit
                exit
                egress
                    qos 11010
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 1188 kilobytes
                            rate max cir 47500
                        exit
                        queue 3 create
                            cbs default
                            mbs 63 kilobytes
                            rate max cir 2500
                        exit
                    exit
                exit
                collect-stats
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8035:103206 create
                no shutdown
            exit
            no shutdown
        exit
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'service': {'epipe': {'103076': {'customer_id': '160',
                                    'regular_sdp': {'8051': {'state': 'enabled',
                                                             'vc_id': '103076'}}},
                         '103206': {'customer_id': '1904',
                                    'regular_sdp': {'8035': {'state': 'enabled',
                                                             'vc_id': '103206'}}}}}}]]
    
# test_github_issue_37_cleaned_up_data()

def test_github_issue_37_cleaned_data_template():
    template = """
<group name="service">
    service {{ ignore }}
    <group name="epipe.{{ service_id }}"  default="none">
        epipe {{ service_id }} customer {{ customer_id }} create
            description "{{ description | ORPHRASE }}"
            service-mtu {{ service_mtu }}
            service-name "{{ service_name | ORPHRASE }}"
        <group name="endpoint"  default="none">
            endpoint {{ endpoint }} create
                revert-time {{ revert_time }}
            exit {{ _end_ }}
        </group>     
        <group name="sap.{{ sap_id }}"  default="none">
            sap {{ sap_id | resub(r"\\*", "qinq") | ORPHRASE }} create
                description "{{ description | ORPHRASE }}"
                multi-service-site "{{ mss_name }}"
            <group name="ingress">
                ingress {{ _start_ }}
                    qos {{ sap_ingress | default("1") }}                 
                    scheduler-policy {{ scheduler_policy | default("none")}}
                exit {{ _end_ }}
            </group>
            <group name="egress">
                egress {{ _start_ }}
                    scheduler-policy {{ scheduler_policy | default("none") }}
                    qos {{ sap_egress | default("1)") }}
                exit {{ _end_ }}
            </group>
                no shutdown {{ state | set("enabled") | default("disabled") }}
            exit {{ _end_ }}
        </group>
        <group name="pwr_sdp.{{pwr_spoke_sdp_id}}**" default="none"> 
            spoke-sdp {{ pwr_spoke_sdp_id }}:{{vc_id }} endpoint {{ endpoint }} create             
                precedence {{ precedence | default("default_precedence") }}
                no shutdown {{ state | set("enabled") | default("disabled") }}
            exit {{ _end_ }}
        </group> 
        <group name="regular_sdp.{{r_spoke_sdp_id}}**" default="none"> 
            spoke-sdp {{ r_spoke_sdp_id }}:{{vc_id }} create             
                no shutdown {{ state | set("enabled") | default("disabled") }}
            exit {{ _end_ }}
        </group> 
            no shutdown {{ state | set("enabled") | default("disabled") }}
        exit {{ _end_ }}
    </group>
    exit {{ _end_ }}
</group>
    """
    data = """
    service foo
        epipe 103076 customer 160 create
            description "vf=EWL:cn=TATA_COM:tl=2C02495918:st=act:"
            service-mtu 1588
            service-name "EPIPE service-103076 DKTN08a-D0105 (63.130.108.41)"
            sap 1/2/12:20.* create
                description "vf=EWL:cn=TATA_COM:tl=2C02495890:st=act:"
                multi-service-site "TATA_VSNL_STRAT_A206_LAN10"
                ingress
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 40 kilobytes
                            rate 10000 cir 10000
                        exit
                    exit
                exit
                egress
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 40 kilobytes
                            rate 10000 cir 10000
                        exit
                    exit
                exit
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8051:103076 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 103206 customer 1904 create
            description "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA UK PLC Stepney Green E1 3DG'"
            service-mtu 1988
            service-name "EPIPE service-103206 DKTN08a-D0105 (63.130.108.41)"
            sap 2/2/3:401.100 create
                description "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA UK PLC Stepney Green E1 3DG'"
                multi-service-site "SKANSKA_E13DG_A825_LAN1"
                ingress
                    qos 11010
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 1188 kilobytes
                            rate max cir 47500
                        exit
                        queue 3 create
                            cbs default
                            mbs 63 kilobytes
                            rate max cir 2500
                        exit
                    exit
                exit
                egress
                    qos 11010
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 1188 kilobytes
                            rate max cir 47500
                        exit
                        queue 3 create
                            cbs default
                            mbs 63 kilobytes
                            rate max cir 2500
                        exit
                    exit
                exit
                collect-stats
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8035:103206 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 103256 customer 160 create
            description "vf=EWL:cn=TATA_COMM:tl=2C02490189:st=act:"
            service-mtu 1988
            service-name "EPIPE service-103256 DKTN08a-D0105 (63.130.108.41)"
            sap 1/2/12:15.* create
                description "vf=EWL:cn=TATA_COMM:tl=2C02490171:st=act:"
                multi-service-site "TATA_VSNL_STRAT_A206_LAN5"
                ingress
                    qos 11000
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 391 kilobytes
                            rate 100000 cir 100000
                        exit
                    exit
                exit
                egress
                    qos 11000
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 391 kilobytes
                            rate 100000 cir 100000
                        exit
                    exit
                exit
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8139:103256 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 103742 customer 160 create
            description "vf=EWL:cn=TATA_COM:tl=2C02410363:st=act:"
            service-mtu 1588
            service-name "EPIPE service-103742 DKTN08a-D0105 (63.130.108.41)"
            sap 5/2/50:20.* create
                description "vf=EWL:cn=TATA_COM:tl=2C02410338:st=act:"
                multi-service-site "TATA_STRAT_LON_A206_LANA"
                ingress
                    qos 11000
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 32 kilobytes
                            rate 8000 cir 8000
                        exit
                    exit
                exit
                egress
                    qos 11000
                    queue-override
                        queue 1 create
                            cbs default
                            mbs 32 kilobytes
                            rate 8000 cir 8000
                        exit
                    exit
                exit
                accounting-policy 4
                no shutdown
            exit
            spoke-sdp 8061:103742 create
                no shutdown
            exit
            no shutdown
        exit
        epipe 55513386 customer 4 vc-switching create
            description "vf=EAGG:cn=Bulldog:tl=VF"
            service-mtu 1526
            spoke-sdp 78:55513386 create
                control-word
                no shutdown
            exit
            spoke-sdp 8245:55513386 create
                control-word
                no shutdown
            exit
            no shutdown
        exit
        epipe 55517673 customer 4 create
            description "vf=EAGG:cn=Bulldog:tl=2C01291821:st=act:no=NGA EPIPE#BAACTQ#VLAN 901"
            service-mtu 1526
            service-name "epipe service-64585 DKTN08a-D0105 (63.130.108.41)"
            endpoint "SDP" create
                revert-time infinite
            exit
            sap 2/2/3:901.* create
                description "2_2_3,H0505824A,Bulldog,VLAN 901"
                ingress
                    scheduler-policy "NGA-LLU-300M"
                    qos 20010
                exit
                egress
                    scheduler-policy "NGA-LLU-300M"
                    qos 20010
                exit
                no shutdown
            exit
            spoke-sdp 8243:55517673 endpoint "SDP" create
                collect-stats
                precedence 1
                no shutdown
            exit
            spoke-sdp 8245:55517673 endpoint "SDP" create
                collect-stats
                precedence primary
                no shutdown
            exit
            no shutdown
        exit   
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'service': {'epipe': {'103076': {'customer_id': '160',
                                    'description': 'vf=EWL:cn=TATA_COM:tl=2C02495918:st=act:',
                                    'regular_sdp': {'8051': {'state': 'enabled',
                                                             'vc_id': '103076'}},
                                    'sap': {'1/2/12:20.qinq': {'description': 'vf=EWL:cn=TATA_COM:tl=2C02495890:st=act:',
                                                               'egress': {'sap_egress': '1)',
                                                                          'scheduler_policy': 'none'},
                                                               'ingress': {'sap_ingress': '1',
                                                                           'scheduler_policy': 'none'},
                                                               'mss_name': 'TATA_VSNL_STRAT_A206_LAN10',
                                                               'state': 'enabled'}},
                                    'service_mtu': '1588',
                                    'service_name': 'EPIPE service-103076 '
                                                    'DKTN08a-D0105 '
                                                    '(63.130.108.41)',
                                    'state': 'enabled'},
                         '103206': {'customer_id': '1904',
                                    'description': "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA "
                                                   'UK PLC Stepney Green E1 '
                                                   "3DG'",
                                    'regular_sdp': {'8035': {'state': 'enabled',
                                                             'vc_id': '103206'}},
                                    'sap': {'2/2/3:401.100': {'description': "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA "
                                                                             'UK '
                                                                             'PLC '
                                                                             'Stepney '
                                                                             'Green '
                                                                             'E1 '
                                                                             "3DG'",
                                                              'egress': {'sap_egress': '11010',
                                                                         'scheduler_policy': 'none'},
                                                              'ingress': {'sap_ingress': '11010',
                                                                          'scheduler_policy': 'none'},
                                                              'mss_name': 'SKANSKA_E13DG_A825_LAN1',
                                                              'state': 'disabled'}},
                                    'service_mtu': '1988',
                                    'service_name': 'EPIPE service-103206 '
                                                    'DKTN08a-D0105 '
                                                    '(63.130.108.41)',
                                    'state': 'enabled'},
                         '103256': {'customer_id': '160',
                                    'description': 'vf=EWL:cn=TATA_COMM:tl=2C02490189:st=act:',
                                    'regular_sdp': {'8139': {'state': 'enabled',
                                                             'vc_id': '103256'}},
                                    'sap': {'1/2/12:15.qinq': {'description': 'vf=EWL:cn=TATA_COMM:tl=2C02490171:st=act:',
                                                               'egress': {'sap_egress': '11000',
                                                                          'scheduler_policy': 'none'},
                                                               'ingress': {'sap_ingress': '11000',
                                                                           'scheduler_policy': 'none'},
                                                               'mss_name': 'TATA_VSNL_STRAT_A206_LAN5',
                                                               'state': 'disabled'}},
                                    'service_mtu': '1988',
                                    'service_name': 'EPIPE service-103256 '
                                                    'DKTN08a-D0105 '
                                                    '(63.130.108.41)',
                                    'state': 'enabled'},
                         '103742': {'customer_id': '160',
                                    'description': 'vf=EWL:cn=TATA_COM:tl=2C02410363:st=act:',
                                    'regular_sdp': {'8061': {'state': 'enabled',
                                                             'vc_id': '103742'}},
                                    'sap': {'5/2/50:20.qinq': {'description': 'vf=EWL:cn=TATA_COM:tl=2C02410338:st=act:',
                                                               'egress': {'sap_egress': '11000',
                                                                          'scheduler_policy': 'none'},
                                                               'ingress': {'sap_ingress': '11000',
                                                                           'scheduler_policy': 'none'},
                                                               'mss_name': 'TATA_STRAT_LON_A206_LANA',
                                                               'state': 'disabled'}},
                                    'service_mtu': '1588',
                                    'service_name': 'EPIPE service-103742 '
                                                    'DKTN08a-D0105 '
                                                    '(63.130.108.41)',
                                    'state': 'enabled'},
                         '55517673': {'customer_id': '4',
                                      'description': 'vf=EAGG:cn=Bulldog:tl=2C01291821:st=act:no=NGA '
                                                     'EPIPE#BAACTQ#VLAN 901',
                                      'endpoint': {'endpoint': '"SDP"',
                                                   'revert_time': 'infinite'},
                                      'pwr_sdp': {'8243': {'endpoint': '"SDP"',
                                                           'precedence': '1',
                                                           'state': 'enabled',
                                                           'vc_id': '55517673'},
                                                  '8245': {'endpoint': '"SDP"',
                                                           'precedence': 'primary',
                                                           'state': 'enabled',
                                                           'vc_id': '55517673'}},
                                      'sap': {'2/2/3:901.qinq': {'description': '2_2_3,H0505824A,Bulldog,VLAN '
                                                                                '901',
                                                                 'egress': {'sap_egress': '20010',
                                                                            'scheduler_policy': '"NGA-LLU-300M"'},
                                                                 'ingress': {'sap_ingress': '20010',
                                                                             'scheduler_policy': '"NGA-LLU-300M"'},
                                                                 'mss_name': 'none',
                                                                 'state': 'disabled'}},
                                      'service_mtu': '1526',
                                      'service_name': 'epipe service-64585 '
                                                      'DKTN08a-D0105 '
                                                      '(63.130.108.41)',
                                      'state': 'enabled'}}}}]]
    
# test_github_issue_37_cleaned_data_template()

def test_github_issue_42():
    data = """
vrf xyz
 address-family ipv4 unicast
  import route-target
   65000:3507
   65000:3511
   65000:5453
   65000:5535
  !
  export route-target
   65000:5453
   65000:5535
  !
 !
!    
    """
    template = """
<group name="vrfs">
vrf {{name}}
  <group name="route-targets">
  import route-target {{ _start_ }}
   {{ import | to_list | joinmatches }}
  </group>
  !
  <group name="route-targets">
  export route-target {{ _start_ }}
   {{ export | to_list | joinmatches }}
  </group>
</group>
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'vrfs': {'name': 'xyz',
                     'route-targets': [{'import': ['65000:3507',
                                                   '65000:3511',
                                                   '65000:5453',
                                                   '65000:5535']},
                                       {'export': ['65000:5453', '65000:5535']}]}}]]

# test_github_issue_42()

def test_github_issue_42_answer():
    data = """
vrf xyz
 address-family ipv4 unicast
  import route-target
   65000:3507
   65000:3511
   65000:5453
   65000:5535
  !
  export route-target
   65000:5453
   65000:5535
  !
 !
!    
    """
    template = """
<group name="vrfs">
vrf {{name}}
  <group name="import_rts">
  import route-target {{ _start_ }}
   {{ import_rt | _start_ }}
  </group>
  !
  <group name="export_rts">
  export route-target {{ _start_ }}
   {{ export_rt | _start_ }}
  </group>
</group>
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'vrfs': {'export_rts': [{'export_rt': '65000:5453'},
                                 {'export_rt': '65000:5535'}],
                     'import_rts': [{'import_rt': '65000:3507'},
                                 {'import_rt': '65000:3511'},
                                 {'import_rt': '65000:5453'},
                                 {'import_rt': '65000:5535'}],
                     'name': 'xyz'}}]]
    
# test_github_issue_42_answer()


def test_issue_45():
    data = """
    vrf2 {
        forwarding-options {
            dhcp-relay {
                server-group {
                    IN_MEDIA_SIGNALING {
                        10.154.6.147;
                    }
                    DHCP-NGN-SIG {
                        10.154.6.147;
                    }
                }
                group group2 {
                    active-server-group IN_MEDIA_SIGNALING;
                    overrides {
                        trust-option-82;
                    }
                }
                group NGN-SIG {
                    active-server-group DHCP-NGN-SIG;
                    overrides {
                        trust-option-82;
                    }
                }
            }
        }
    }
    """
    template = """
<group name="vrfs*">
    {{ name | _start_ }} {
        <group name="forwarding_options">
        forwarding-options { {{ _start_ }}
            <group name="dhcp_relay">
            dhcp-relay { {{ _start_ }}
            
                <group name="server_group">
                server-group { {{ _start_ }}
                    <group name="dhcp*">
                    {{ server_group_name1 | _start_ }} {
                        <group name="helper_addresses*">
                        {{ helper_address | IP }};
                        </group>
                    } {{ _end_ }}
                    </group>
                } {{ _end_ }}
                </group>
                
                <group name="groups*">
                group {{ group_name | _start_ }} {
                    active-server-group {{server_group_name2}};
                } {{ _end_ }}
                </group>
                
            } {{ _end_ }}
            </group>
        } {{ _end_ }}
        </group>
    } {{ _end_ }}
</group>    
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'vrfs': [{'forwarding_options': {'dhcp_relay': {'groups': [{'group_name': 'group2',
                                                                                 'server_group_name2': 'IN_MEDIA_SIGNALING'},
                                                                                {'group_name': 'NGN-SIG',
                                                                                 'server_group_name2': 'DHCP-NGN-SIG'}],
                                                                     'server_group': {'dhcp': [{'helper_addresses': [{'helper_address': '10.154.6.147'}],
                                                                                                'server_group_name1': 'IN_MEDIA_SIGNALING'},
                                                                                               {'helper_addresses': [{'helper_address': '10.154.6.147'}],
                                                                                                'server_group_name1': 'DHCP-NGN-SIG'},
                                                                                               {'server_group_name1': 'overrides'},
                                                                                               {'server_group_name1': 'overrides'}]}}},
                               'name': 'vrf2'}]}]]
             
# test_issue_45()

def test_issue_45_1():
    data = """
    vrf2 {
        forwarding-options {
            dhcp-relay {
                server-group {
                    IN_MEDIA_SIGNALING {
                        10.154.6.147;
                    }
                group NGN-SIG {
                    active-server-group DHCP-NGN-SIG;
                    overrides {
                        trust-option-82;
                    }
                }
            }
        }
    }
    """
    template = """
<group name="vrfs*">
    {{ name | _start_ }} {
        <group name="forwarding_options">
        forwarding-options { {{ _start_ }}
            <group name="dhcp_relay">
            dhcp-relay { {{ _start_ }}
            
                <group name="server_group">
                server-group { {{ _start_ }}
                    <group name="dhcp*">
                    {{ server_group_name | _start_ }} {
                    </group>
                </group>
                
                <group name="groups*">
                group {{ group_name | _start_ }} {
                </group>
                
            </group>
        </group>
</group>    
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'vrfs': [{'forwarding_options': {'dhcp_relay': {'groups': [{'group_name': 'NGN-SIG'}],
                                                                     'server_group': {'dhcp': [{'server_group_name': 'IN_MEDIA_SIGNALING'},
                                                                                               {'server_group_name': 'overrides'}]}}},
                               'name': 'vrf2'}]}]]
             
# test_issue_45_1()

def test_issue_45_filtering_fix():
    data = """
    vrf2 {
        forwarding-options {
            dhcp-relay {
                server-group {
                    IN_MEDIA_SIGNALING {
                        10.154.6.147;
                    }
                    DHCP-NGN-SIG {
                        10.154.6.147;
                    }
                }
                group group2 {
                    active-server-group IN_MEDIA_SIGNALING;
                    overrides {
                        trust-option-82;
                    }
                }
                group NGN-SIG {
                    active-server-group DHCP-NGN-SIG;
                    overrides {
                        trust-option-82;
                    }
                }
            }
        }
    }
    """
    template = """
<group name="vrfs*">
    {{ name | _start_ }} {
        <group name="forwarding_options">
        forwarding-options { {{ _start_ }}
            <group name="dhcp_relay">
            dhcp-relay { {{ _start_ }}
            
                <group name="server_group">
                server-group { {{ _start_ }}
                    <group name="dhcp*">
                    {{ server_group_name1 | _start_ | exclude("overrides") }} {
                        <group name="helper_addresses*">
                        {{ helper_address | IP }};
                        </group>
                    } {{ _end_ }}
                    </group>
                } {{ _end_ }}
                </group>
                
                <group name="groups*">
                group {{ group_name | _start_ }} {
                    active-server-group {{server_group_name2}};
                } {{ _end_ }}
                </group>
                
            } {{ _end_ }}
            </group>
        } {{ _end_ }}
        </group>
    } {{ _end_ }}
</group>    
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res) 
    assert res == [[{'vrfs': [{'forwarding_options': {'dhcp_relay': {'groups': [{'group_name': 'group2',
                                                                                 'server_group_name2': 'IN_MEDIA_SIGNALING'},
                                                                                {'group_name': 'NGN-SIG',
                                                                                 'server_group_name2': 'DHCP-NGN-SIG'}],
                                                                     'server_group': {'dhcp': [{'helper_addresses': [{'helper_address': '10.154.6.147'}],
                                                                                                'server_group_name1': 'IN_MEDIA_SIGNALING'},
                                                                                               {'helper_addresses': [{'helper_address': '10.154.6.147'}],
                                                                                                'server_group_name1': 'DHCP-NGN-SIG'}]}}},
                               'name': 'vrf2'}]}]]
             
# test_issue_45_filtering_fix()

def test_issue_47_answer():
    data = """
Some text which indicates that below block should be included in results ABC
interface Loopback0
 description Router-id-loopback
 ip address 192.168.0.113/24
!
Some text which indicates that below block should be included in results DEF
interface Loopback2
 description Router-id-loopback 2
 ip address 192.168.0.114/24
!
Some text which indicates that below block should NOT be included in results
interface Vlan778
 description CPE_Acces_Vlan
 ip address 2002::fd37/124
 ip vrf CPE1
!
Some text which indicates that below block should be included in results GKL
interface Loopback3
 description Router-id-loopback 3
 ip address 192.168.0.115/24
!
"""
    template = """
Some text which indicates that below block should be included in results ABC {{ _start_ }}
Some text which indicates that below block should be included in results DEF {{ _start_ }}
Some text which indicates that below block should be included in results GKL {{ _start_ }}
interface {{ interface }}
 ip address {{ ip }}/{{ mask }}
 description {{ description | re(".+") }}
 ip vrf {{ vrf }}
! {{ _end_ }}
"""
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150) 
    assert res == [[[{'description': 'Router-id-loopback', 'interface': 'Loopback0', 'ip': '192.168.0.113', 'mask': '24'},
                     {'description': 'Router-id-loopback 2', 'interface': 'Loopback2', 'ip': '192.168.0.114', 'mask': '24'},
                     {'description': 'Router-id-loopback 3', 'interface': 'Loopback3', 'ip': '192.168.0.115', 'mask': '24'}]]]
   
# test_issue_47_answer()


def test_issue_48_answer():
    data = """
ECON*3400 The Economics of Personnel Management U (3-0) [0.50]
In this course, we examine the economics of personnel management in organizations.
Using mainstream microeconomic and behavioural economic theory, we will consider
such issues as recruitment, promotion, financial and non-financial incentives,
compensation, job performance, performance evaluation, and investment in personnel.
The interplay between theoretical models and empirical evidence will be emphasized in
considering different approaches to the management of personnel.
Prerequisite(s): ECON*2310 or ECON*2200
Department(s): Department of Economics and Finance    

ECON*4400 The Economics of Personnel Management U (7-1) [0.90]
In this course, we examine the economics of personnel management in organizations.
Using mainstream microeconomic and behavioural economic theory, we will consider
such issues as recruitment, promotion, financial and non-financial incentives,
compensation, job performance, performance evaluation, and investment in personnel.
Prerequisite(s): ECON*2310
Department(s): Department of Economics
    """
    template = """
<vars>
descr_chain = [
    "PHRASE",
    "exclude('Prerequisite(s)')",
    "exclude('Department(s)')",
    "joinmatches"
]
</vars>

<group>
{{ course }}*{{ code }} {{ name | PHRASE }} {{ semester }} ({{ lecture_lab_time }}) [{{ weight }}]
{{ description | chain(descr_chain) }}
Prerequisite(s): {{ prereqs | ORPHRASE }}
Department(s): {{ department | ORPHRASE }}   
</group>
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)     
    assert res == [[[{'code': '3400',
                      'course': 'ECON',
                      'department': 'Department of Economics and Finance',
                      'description': 'In this course, we examine the economics of personnel management in organizations.\n'
                                     'Using mainstream microeconomic and behavioural economic theory, we will consider\n'
                                     'such issues as recruitment, promotion, financial and non-financial incentives,\n'
                                     'compensation, job performance, performance evaluation, and investment in personnel.\n'
                                     'The interplay between theoretical models and empirical evidence will be emphasized in\n'
                                     'considering different approaches to the management of personnel.',
                      'lecture_lab_time': '3-0',
                      'name': 'The Economics of Personnel Management',
                      'prereqs': 'ECON*2310 or ECON*2200',
                      'semester': 'U',
                      'weight': '0.50'},
                     {'code': '4400',
                      'course': 'ECON',
                      'department': 'Department of Economics',
                      'description': 'In this course, we examine the economics of personnel management in organizations.\n'
                                     'Using mainstream microeconomic and behavioural economic theory, we will consider\n'
                                     'such issues as recruitment, promotion, financial and non-financial incentives,\n'
                                     'compensation, job performance, performance evaluation, and investment in personnel.',
                      'lecture_lab_time': '7-1',
                      'name': 'The Economics of Personnel Management',
                      'prereqs': 'ECON*2310',
                      'semester': 'U',
                      'weight': '0.90'}]]]
    
# test_issue_48_answer()

def test_issue_48_answer_more():
    data = """
IBIO*4521 Thesis in Integrative Biology F (0-12) [1.00]
This course is the first part of the two-semester course IBIO*4521/2. This course is
a two-semester (F,W) undergraduate project in which students conduct a comprehensive,
independent research project in organismal biology under the supervision of a faculty
member in the Department of Integrative Biology. Projects involve a thorough literature
review, a research proposal, original research communicated in oral and poster
presentations, and in a written, publication quality document. This two-semester course
offers students the opportunity to pursue research questions and experimental designs
that cannot be completed in the single semester research courses. Students must make
arrangements with both a faculty supervisor and the course coordinator at least one
semester in advance. A departmental registration form must be obtained from the course
coordinator and submitted no later than the second class day of the fall semester. This is
a twosemester course offered over consecutive semesters F-W. When you select this
course, you must select IBIO*4521 in the Fall semester and IBIO*4522 in the Winter
semester.A grade will not be assigned to IBIO*4521 until IBIO*4522 has been completed.
Prerequisite(s): 12.00 credits
Restriction(s): Normally a minimum cumulative average of 70%. Permission of course
coordinator.
Department(s): Department of Integrative Biology

IBIO*4533 Thesis in Integrative Biology F (0-14) [2.00]
This course is the first part of the two-semester course IBIO*4521/2. This course is
a two-semester (F,W) undergraduate project in which students conduct a comprehensive,
independent research project in organismal biology under the supervision of a faculty
member in the Department of Integrative Biology. 
Restriction(s): Normally a minimum cumulative average of 80%. Permission of course
coordinator. Normally a minimum cumulative average of 90%. Permission of course
coordinator. 
Department(s): Department of Integrative Biology
    """
    template = """
<vars>
chain_1 = [
    "ORPHRASE",
    "exclude('Prerequisite(s)')",
    "exclude('Department(s)')",
    "exclude('Restriction(s)')",
    "joinmatches"
]
</vars>

<group>
{{ course }}*{{ code }} {{ name | PHRASE }} {{ semester }} ({{ lecture_lab_time }}) [{{ weight }}]
{{ description | chain(chain_1) }}
Prerequisite(s): {{ prereqs | ORPHRASE }}
Department(s): {{ department | ORPHRASE }}   

<group name="_">
Restriction(s): {{ restrictions | PHRASE | joinmatches }}
{{ restrictions | chain(chain_1) }}
</group>

</group>
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)    
    assert res == [[[{'code': '4521',
                      'course': 'IBIO',
                      'department': 'Department of Integrative Biology',
                      'description': 'This course is the first part of the two-semester course IBIO*4521/2. This course is\n'
                                     'a two-semester (F,W) undergraduate project in which students conduct a comprehensive,\n'
                                     'independent research project in organismal biology under the supervision of a faculty\n'
                                     'member in the Department of Integrative Biology. Projects involve a thorough literature\n'
                                     'review, a research proposal, original research communicated in oral and poster\n'
                                     'presentations, and in a written, publication quality document. This two-semester course\n'
                                     'offers students the opportunity to pursue research questions and experimental designs\n'
                                     'that cannot be completed in the single semester research courses. Students must make\n'
                                     'arrangements with both a faculty supervisor and the course coordinator at least one\n'
                                     'semester in advance. A departmental registration form must be obtained from the course\n'
                                     'coordinator and submitted no later than the second class day of the fall semester. This is\n'
                                     'a twosemester course offered over consecutive semesters F-W. When you select this\n'
                                     'course, you must select IBIO*4521 in the Fall semester and IBIO*4522 in the Winter\n'
                                     'semester.A grade will not be assigned to IBIO*4521 until IBIO*4522 has been completed.',
                      'lecture_lab_time': '0-12',
                      'name': 'Thesis in Integrative Biology',
                      'prereqs': '12.00 credits',
                      'restrictions': 'Normally a minimum cumulative average of 70%. Permission of course\ncoordinator.',
                      'semester': 'F',
                      'weight': '1.00'},
                     {'code': '4533',
                      'course': 'IBIO',
                      'department': 'Department of Integrative Biology',
                      'description': 'This course is the first part of the two-semester course IBIO*4521/2. This course is\n'
                                     'a two-semester (F,W) undergraduate project in which students conduct a comprehensive,\n'
                                     'independent research project in organismal biology under the supervision of a faculty\n'
                                     'member in the Department of Integrative Biology.',
                      'lecture_lab_time': '0-14',
                      'name': 'Thesis in Integrative Biology',
                      'restrictions': 'Normally a minimum cumulative average of 80%. Permission of course\n'
                                      'coordinator. Normally a minimum cumulative average of 90%. Permission of course\n'
                                      'coordinator.',
                      'semester': 'F',
                      'weight': '2.00'}]]]
    
# test_issue_48_answer_more()

def test_slack_channel_answer_for_Noif():
    data = """
# not disabled and no comment
/ip address add address=10.4.1.245 interface=lo0 network=10.4.1.245
/ip address add address=10.4.1.246 interface=lo1 network=10.4.1.246
# not disabled and comment with no quotes
/ip address add address=10.9.48.241/29 comment=SITEMON interface=ether2 network=10.9.48.240
/ip address add address=10.9.48.233/29 comment=Camera interface=vlan205@bond1 network=10.9.48.232
/ip address add address=10.9.49.1/24 comment=SM-Management interface=vlan200@bond1 network=10.9.49.0
# not disabled and comment with quotes
/ip address add address=10.4.1.130/30 comment="to core01" interface=vlan996@bond4 network=10.4.1.128
/ip address add address=10.4.250.28/29 comment="BH 01" interface=vlan210@bond1 network=10.4.250.24
/ip address add address=10.9.50.13/30 comment="Cust: site01-PE" interface=vlan11@bond1 network=10.9.50.12
# disabled no comment
/ip address add address=10.0.0.2/30 disabled=yes interface=bridge:customer99 network=10.0.0.0
# disabled with comment
/ip address add address=169.254.1.100/24 comment=Cambium disabled=yes interface=vlan200@bond1 network=169.254.1.0
# disabled with comment with quotes
/ip address add address=10.4.248.20/29 comment="Backhaul to AGR (Test Segment)" disabled=yes interface=vlan209@bond1 network=10.4.248.16
    """
    template = """
<vars>
default_values = {
    "comment": "",
    "disabled": False
}
</vars>

<group default="default_values">
## not disabled and no comment
/ip address add address={{ ip | _start_ }} interface={{ interface }} network={{ network }}

## not disabled and comment with/without quotes
/ip address add address={{ ip | _start_ }}/{{ mask }} comment={{ comment | ORPHRASE | exclude("disabled=") | strip('"')}} interface={{ interface }} network={{ network }}

## disabled no comment
/ip address add address={{ ip | _start_ }}/{{ mask }} disabled={{ disabled }} interface={{ interface }} network={{ network }}

## disabled with comment with/without quotes
/ip address add address={{ ip | _start_ }}/{{ mask }} comment={{ comment | ORPHRASE | exclude("disabled=") | strip('"') }} disabled={{ disabled }} interface={{ interface }} network={{ network }}
</group>
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result(structure="flat_list")
    # pprint.pprint(res, width=200)  
    assert res == [{'comment': '', 'disabled': False, 'interface': 'lo0', 'ip': '10.4.1.245', 'network': '10.4.1.245'},
                   {'comment': '', 'disabled': False, 'interface': 'lo1', 'ip': '10.4.1.246', 'network': '10.4.1.246'},
                   {'comment': 'SITEMON', 'disabled': False, 'interface': 'ether2', 'ip': '10.9.48.241', 'mask': '29', 'network': '10.9.48.240'},
                   {'comment': 'Camera', 'disabled': False, 'interface': 'vlan205@bond1', 'ip': '10.9.48.233', 'mask': '29', 'network': '10.9.48.232'},
                   {'comment': 'SM-Management', 'disabled': False, 'interface': 'vlan200@bond1', 'ip': '10.9.49.1', 'mask': '24', 'network': '10.9.49.0'},
                   {'comment': 'to core01', 'disabled': False, 'interface': 'vlan996@bond4', 'ip': '10.4.1.130', 'mask': '30', 'network': '10.4.1.128'},
                   {'comment': 'BH 01', 'disabled': False, 'interface': 'vlan210@bond1', 'ip': '10.4.250.28', 'mask': '29', 'network': '10.4.250.24'},
                   {'comment': 'Cust: site01-PE', 'disabled': False, 'interface': 'vlan11@bond1', 'ip': '10.9.50.13', 'mask': '30', 'network': '10.9.50.12'},
                   {'comment': '', 'disabled': 'yes', 'interface': 'bridge:customer99', 'ip': '10.0.0.2', 'mask': '30', 'network': '10.0.0.0'},
                   {'comment': 'Cambium', 'disabled': 'yes', 'interface': 'vlan200@bond1', 'ip': '169.254.1.100', 'mask': '24', 'network': '169.254.1.0'},
                   {'comment': 'Backhaul to AGR (Test Segment)', 'disabled': 'yes', 'interface': 'vlan209@bond1', 'ip': '10.4.248.20', 'mask': '29', 'network': '10.4.248.16'}]

# test_slack_channel_answer_for_Noif()

def test_slack_answer_2():
    data_to_parse = """
    port 1/1/1
        description "port 1 description"
        ethernet
            mode hybrid
            encap-type dot1q
            crc-monitor
                sd-threshold 5 multiplier 5
                sf-threshold 3 multiplier 5
                window-size 60
            exit
            network
                queue-policy "ncq-only"
                accounting-policy 12
                collect-stats
                egress
                    queue-group "qos-policy-for-router1" instance 1 create
                        accounting-policy 1
                        collect-stats
                        agg-rate
                            rate 50000
                        exit
                    exit
                exit
            exit
            access
                egress
                    queue-group "policer-output-queues" instance 1 create
                        accounting-policy 1
                        collect-stats
                    exit
                exit
            exit
            lldp
                dest-mac nearest-bridge
                    admin-status tx-rx
                    notification
                    tx-tlvs port-desc sys-name sys-desc sys-cap
                    tx-mgmt-address system
                exit
            exit
            down-on-internal-error
        exit
        no shutdown
    exit
    port 1/1/2
        description "another port to a another router"
        ethernet
            mode hybrid
            encap-type dot1q
            egress-scheduler-policy "qos-port-scheduler"
            crc-monitor
                sd-threshold 5 multiplier 5
                sf-threshold 3 multiplier 5
                window-size 60
            exit
            access
                egress
                    queue-group "policer-output-queues" instance 1 create
                        accounting-policy 1
                        collect-stats
                    exit
                exit
            exit
            down-on-internal-error
        exit
        no shutdown
    exit
    port 1/1/3
        description "port 3 to some third router"
        ethernet
            mode access
            encap-type dot1q
            mtu 2000
            egress-scheduler-policy "strict-scheduler"
            network
                queue-policy "ncq-only"
                accounting-policy 12
                collect-stats
                egress
                    queue-group "some-shaping-policy" instance 1 create
                        accounting-policy 1
                        collect-stats
                        agg-rate
                            rate 50000
                        exit
                    exit
                    queue-group "another-shaping-policy" instance 1 create
                        accounting-policy 1
                        collect-stats
                        agg-rate
                            rate 50000
                        exit
                    exit
                    queue-group "this-shaper-is-cool" instance 1 create
                        agg-rate
                            rate 1000000
                        exit
                    exit
                exit
            exit
        exit
        no shutdown
    exit
    """
    template = """
    <group name="system.ports">
    port {{ id }}
        shutdown {{ admin_enabled | set(false) }}
        description "{{ description | ORPHRASE | strip('"') }}"
        <group name="ethernet">
        ethernet {{ _start_ }}
            mode {{ mode }}
            encap-type {{ encap_type }}
            mtu {{ mtu | DIGIT }}
            egress-scheduler-policy {{ egress_sched_policy | strip('"') }}
            loopback internal persistent {{ loop_internal | set(true) }}
            <group name="network">
            network {{ _start_ }}
                queue-policy {{ queue_policy | ORPHRASE | strip('"') }}
                accounting-policy {{ accounting_policy | DIGIT }}
                collect-stats {{ collect_stats | set(true) }}
                <group name="egress">
                egress {{ _start_ }}
                    <group name="queuegroups*">
                    queue-group {{ name | strip('"') }} instance 1 create
                            rate {{ agg_rate | DIGIT }}
                    exit {{_end_}}
                    </group>
## this "exit {{ _end_ }}" had wrong indentation level, leading to 
## group name="egress" finishing too early
                exit {{_end_}}
                </group>
            exit {{_end_}}
            </group>
            lldp {{ lldp_enabled | set(true) }}
        exit {{_end_}}
        </group>
        no shutdown {{admin_enabled | set(true)}}
    exit {{_end_}}
    </group>
    """
    parser = ttp(data=data_to_parse, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    pprint.pprint(res, width=150) 
    assert res == [[{'system': {'ports': [{'admin_enabled': True,
                                           'description': 'port 1 description',
                                           'ethernet': {'encap_type': 'dot1q',
                                                        'lldp_enabled': True,
                                                        'mode': 'hybrid',
                                                        'network': {'accounting_policy': '12',
                                                                    'collect_stats': True,
                                                                    'egress': {'queuegroups': [{'agg_rate': '50000', 'name': 'qos-policy-for-router1'}]},
                                                                    'queue_policy': 'ncq-only'}},
                                           'id': '1/1/1'},
                                          {'admin_enabled': True,
                                           'description': 'another port to a another router',
                                           'ethernet': {'egress_sched_policy': 'qos-port-scheduler', 'encap_type': 'dot1q', 'mode': 'hybrid'},
                                           'id': '1/1/2'},
                                          {'admin_enabled': True,
                                           'description': 'port 3 to some third router',
                                           'ethernet': {'egress_sched_policy': 'strict-scheduler',
                                                        'encap_type': 'dot1q',
                                                        'mode': 'access',
                                                        'mtu': '2000',
                                                        'network': {'accounting_policy': '12',
                                                                    'collect_stats': True,
                                                                    'egress': {'queuegroups': [{'agg_rate': '50000', 'name': 'some-shaping-policy'},
                                                                                               {'agg_rate': '50000', 'name': 'another-shaping-policy'},
                                                                                               {'agg_rate': '1000000', 'name': 'this-shaper-is-cool'}]},
                                                                    'queue_policy': 'ncq-only'}},
                                           'id': '1/1/3'}]}}]]
    
# test_slack_answer_2()

def test_slack_answer_3():
    """
    Problem was that interfaces were matched by regexes from both ospf and ospfv3
    groups, decision logic was not able to properly work out to which group result
    should belong, changed behavior to check if match is a child of current record 
    group and use it if so. Also had to change how group id encoded from string to 
    tuple of two elements ("group path", "group index",)
    
    Here is some debug output until problem was fixed:
    self.record["GRP_ID"]:  service.vprns*.{{id}}**.ospf3**::1
    re_["GROUP"].group_id:  service.vprns*.{{id}}**.ospf**.interfaces*::0
    re_idex: 0
    
    self.record["GRP_ID"]:  service.vprns*.{{id}}**.ospf3**::1
    re_["GROUP"].group_id:  service.vprns*.{{id}}**.ospf3**.interfaces*::0
    re_idex: 1
    
    # problem was happening because logic was not able to decide that need to use this match
    self.record["GRP_ID"]:  service.vprns*.{{id}}**.ospf**::0
    re_["GROUP"].group_id:  service.vprns*.{{id}}**.ospf**.interfaces*::0
    re_idex: 0
    
    # problem was happening because logic was picking up this match
    self.record["GRP_ID"]:  service.vprns*.{{id}}**.ospf**::0
    re_["GROUP"].group_id:  service.vprns*.{{id}}**.ospf3**.interfaces*::0
    re_idex: 1
    
    Wrong results:
    [[{'service': {'vprns': [{'4': {'name': 'ospf_version3_vprn',
                                    'ospf': {'area': '0.0.0.0', 'interfaces': [{'name': 'interface-one'}]},
                                    'ospf3': {'area': '0.0.0.0', 'interfaces': [{'name': 'interface-two'}]}},
                              '5': {'name': 'vprn5', 'ospf': {'area': '0.0.0.0'}, 
                                                     'ospf3': {'interfaces': [{'name': 'interface-three'}]}}}]}}]]
    """
    data = """
    service
        vprn 4 name "ospf_version3_vprn" customer 40 create
            ospf
                area 0.0.0.0
                    interface "interface-one"
            ospf3 0
                area 0.0.0.0
                    interface "interface-two"
        vprn 5 name "vprn5" customer 50 create
            ospf
                area 0.0.0.0
                    interface "interface-three"
    """
    template="""
        <group name="service.vprns*.{{id}}**">
        vprn {{ id }} name {{ name | ORPHRASE | strip('"') }} customer {{ ignore }} create
            <group name="ospf**">
            ospf {{ _start_ }}
                area {{ area }}
                    <group name="interfaces*">
                    interface {{ name | ORPHRASE | strip('"') }}
                    </group>
            </group>
            <group name="ospf3**">
            ospf3 0 {{ _start_ }}
                area {{ area }}
                    <group name="interfaces*">
                    interface {{ name | ORPHRASE | strip('"') }}
                    </group>
            </group>
        </group>
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=100) 
    assert res == [[{'service': {'vprns': [{'4': {'name': 'ospf_version3_vprn',
                                                  'ospf': {'area': '0.0.0.0',
                                                           'interfaces': [{'name': 'interface-one'}]},
                                                  'ospf3': {'area': '0.0.0.0',
                                                            'interfaces': [{'name': 'interface-two'}]}},
                                            '5': {'name': 'vprn5',
                                                  'ospf': {'area': '0.0.0.0',
                                                           'interfaces': [{'name': 'interface-three'}]}}}]}}]]
    
# test_slack_answer_3()

def test_slack_answer_3_full():
    data = """
    service
        vprn 1 name "vprn1" customer 10 create
            interface "loopback" create
            exit
            interface "interface-one" create
            exit
            interface "interface-two" create
            exit
            interface "bgp-interface" create
            exit
        exit
        vprn 2 name "vprn2" customer 20 create
            interface "loopback" create
            exit
            interface "interface-two" create
            exit
            interface "bgp-interface" create
            exit
        exit
        vprn 3 name "vprn3" customer 30 create
            interface "loopback" create
            exit
            interface "interface-two" create
            exit
        exit
        vprn 4 name "ospf_version3_vprn" customer 40 create
            interface "loopback" create
            exit
            interface "interface-two" create
            exit
        exit
        vprn 5 name "vprn5" customer 50 create
            interface "loopback" create
            exit
            interface "interface-two" create
            exit
            interface "bgp-interface" create
            exit
        exit
        vprn 1 name "vprn1" customer 10 create
            interface "loopback" create
                address 10.10.10.1/32
                loopback
            exit
            interface "interface-one" create
                address 10.10.10.10/30
                sap 1/1/1:10 create
                exit
            exit
            interface "interface-two" create
                address 10.10.10.100/31
                sap lag-5:80 create
                exit
            exit
            interface "bgp-interface" create
                address 10.10.10.200/31
                sap lag-4:100 create
                exit
            exit
            ospf
                area 0.0.0.0
                    interface "interface-two"
                        passive
                        no shutdown
                    exit
                exit
                no shutdown
            exit
            no shutdown
        exit
        vprn 2 name "vprn2" customer 20 create
            interface "interface-two" create
                address 10.11.11.10/31
                sap lag-1:50 create
                exit
            exit
            ospf
                area 0.0.0.0
                    interface "interface-two"
                        passive
                        no shutdown
                    exit
                exit
                no shutdown
            exit
            no shutdown
        exit
        vprn 3 name "vprn3" customer 30 create
            interface "loopback" create
                address 10.12.12.12/32
                loopback
            exit
            interface "interface-two" create
                address 10.12.12.100/31
                sap lag-5:33 create
                exit
            exit
            ospf
                area 0.0.0.0
                    interface "interface-two"
                        passive
                        no shutdown
                    exit
                exit
                no shutdown
            exit
            no shutdown
        exit
        vprn 4 name "ospf_version3_vprn" customer 40 create
            interface "loopback" create
                address 10.40.40.10/32
                ipv6
                    address 1500:1000:460e::a03:ae46/128
                exit
                loopback
            exit
            interface "interface-two" create
                address 10.40.40.100/31
                ipv6
                    address 1500:1000:460e::2222:1111/64
                exit
                sap lag-5:800 create
                exit
            exit
            ospf
                area 0.0.0.0
                    interface "interface-two"
                        passive
                        no shutdown
                    exit
                exit
                no shutdown
            exit
            ospf3 0
                area 0.0.0.0
                    interface "interface-two"
                        passive
                        no shutdown
                    exit
                exit
                no shutdown
            exit
            no shutdown
        exit
        vprn 5 name "vprn5" customer 50 create
            interface "loopback" create
                address 10.50.50.50/32
                loopback
            exit
            interface "interface-two" create
                address 10.50.50.100/31
                sap lag-5:5 create
                exit
            exit
            interface "bgp-interface" create
                address 10.50.50.200/31
                sap lag-1:602 create
                exit
            exit
            bgp
                group "eBGP"
                    peer-as 4444
                    neighbor 10.50.50.201
                    exit
                exit
                no shutdown
            exit
            ospf
                area 0.0.0.0
                    interface "interface-two"
                        passive
                        no shutdown
                    exit
                exit
                no shutdown
            exit
            no shutdown
        exit
    exit
    """
    template = """
#-------------------------------------------------- {{ ignore }}
echo "Service Configuration" {{ ignore }}
#-------------------------------------------------- {{ ignore }}
    service {{ ignore }}
<group name="service.vprns*.{{id}}**">
        vprn {{ id }} name {{ name | ORPHRASE | strip('"') }} customer {{ ignore }} create
            shutdown {{ admin_enabled | set("False") }}
            description {{ description | ORPHRASE | strip('"') }}
            vrf-import {{ import_policy | ORPHRASE | strip('"') }}
            router-id {{ router_id }}
            autonomous-system {{ local_as }}
            route-distinguisher {{ loopback_ip }}:{{ vrf_routedist }}
            vrf-target target:{{ ignore }}:{{ vrf_routetarget }}
            vrf-target {{ vrf_export }} target:{{ ignore }}:{{ vrf_routetarget }}
        <group name="interfaces*.{{name}}**">
            interface {{ name | ORPHRASE | strip('"') }} create
                shutdown {{ admin_enabled | set("False") }}
                description {{ description | ORPHRASE | strip('"') }}
                address {{ address | IP }}/{{ mask | DIGIT }}
                ip-mtu {{ mtu }}
                bfd {{ bfd_timers }} receive {{ ignore }} multiplier {{ bfd_interval }}
            <group name="vrrp">
                vrrp {{ instance }}
                    backup {{ backup }}
                    priority {{ priority }}
                    policy {{ policy }}
                    ping-reply {{ pingreply | set("True") }}
                    traceroute-reply {{ traceroute_reply | set("True") }}
                    init-delay {{ initdelay }}
                    message-interval {{ message_int_seconds }}
                    message-interval  milliseconds {{ message_int_milliseconds }}
                    bfd-enable 1 interface {{ bfd_interface | ORPHRASE | strip('"')}} dst-ip {{ bfd_dst_ip }}
                exit {{ _end_ }}
            </group>
            <group name="ipv6">
                ipv6 {{ _start_ }}
                    address {{ address | IPV6 }}/{{ mask | DIGIT }}
                    address {{ address | _start_ | IPV6 }}/{{ mask | DIGIT }} dad-disable
                    link-local-address {{ linklocal_address | IPV6 }} dad-disable
                <group name="vrrp">
                    vrrp {{ instance | _start_ }}
                    <group name="backup*">
                        backup {{ ip }}
                    </group>
                        priority {{ priority }}
                        policy {{ policy }}
                        ping-reply {{ pingreplay | set("True") }}
                        traceroute-reply {{ traceroute_reply | set("True") }}
                        init-delay {{ initdelay }}
                        message-interval milliseconds {{ message_int_milliseconds }}
                    exit {{ _end_ }}
                </group>
                exit {{ _end_ }}
            </group>
            <group name="vpls">
                vpls {{ vpls_name | ORPHRASE | strip('"') | _start_ }}
                exit {{ _end_ }}
            </group>
            <group name="sap**">
                sap {{ port | _start_ }}:{{ vlan | DIGIT }} create
                    ingress {{ _exact_ }}
                        qos {{ qos_sap_ingress }}
                <group name="_">
                    egress {{ _start_ }}
                        qos {{ qos_sap_egress }}
                </group>
                    collect-stats {{ collect_stats | set("True") }}
                    accounting-policy {{ accounting_policy }}
                exit {{ _end_}}
            </group>
            exit {{ _end_}}
        </group>
        <group name="staticroutes*">
            static-route-entry {{ prefix | PREFIX | _start_ }}
                black-hole {{ blackhole | set("True") }}
                next-hop {{ nexthop | IP }}
                    shutdown {{ admin_enabled | set("False") }}
                    no shutdown {{ admin_enabled | set("True") }}
            exit {{ _end_ }}
        </group>
        <group name="aggregates">
            aggregate {{ agg_block | PREFIX | _start_ }} summary-only
        </group>
        <group name="router_advertisement">
            router-advertisement {{ _start_ }}
                interface {{ interface | ORPHRASE | strip('"') }}
                    use-virtual-mac {{ use_virtualmac | set("True") }}
                    no shutdown {{ admin_enabled | set("True") }}
            exit {{ _end_ }}
        </group>
        <group name="bgp**">
            bgp {{ _start_ }}
                min-route-advertisement {{ min_route_advertisement | DIGIT }}
                <group name="peergroups*">
                group {{ name | ORPHRASE | strip('"') }}
                    family {{ family | ORPHRASE | split(" ") }}
                    type {{ peer_type | ORPHRASE }}
                    import {{ importpolicy | ORPHRASE | strip('"') }}
                    export {{ exportpolicy | ORPHRASE | strip('"') }}
                    peer-as {{ remote_as }}
                    bfd-enable {{ bfd_enabled | set("True") }}
                    <group name="neighbors*">
                    neighbor {{ address | IP | _start_ }}
                    neighbor {{ address | IPV6 | _start_ }}
                        shutdown {{ admin_enabled | set("False") }}
                        keepalive {{ keepalive }}
                        hold-time {{ holdtime }}
                        bfd-enable {{ bfd_enabled | set("True") }}
                        as-override {{ as_override | set("True") }}
                    exit {{ _end_ }}
                    </group>
                exit {{ _end_ }}
                </group>
                no shutdown {{ admin_enabled | set("True") | _start_ }}
            exit {{ _end_ }}
        </group>
        <group name="ospf**">
            ospf {{ _start_ }}{{ _exact_ }}
                area {{ area }}
                <group name="interfaces*">
                    interface {{ name | ORPHRASE | strip('"') | _start_ }}
                        passive {{ passive | set("True") }}
                    exit {{ _end_ }}
                </group>
                no shutdown {{ admin_enabled | set("True") }}
            exit {{ _end_ }}
        </group>
        <group name="ospf3**">
            ospf3 0 {{ _start_ }}{{ _exact_ }}
                area {{ area }}
                <group name="interfaces*">
                    interface {{ name | ORPHRASE | strip('"') | _start_ }}
                        passive {{ passive | set("True") }}
                    exit {{ _end_ }}
                </group>
                no shutdown {{ admin_enabled | set("True") }}
            exit {{ _end_ }}
        </group>
            no shutdown {{ admin_enabled | set("True") }}
        exit {{ _end_ }}
</group>    
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=100) 
    assert res == [[{'service': {'vprns': [{'1': {'admin_enabled': 'True',
                                'interfaces': [{'bgp-interface': {'address': '10.10.10.200',
                                                                  'mask': '31',
                                                                  'sap': {'port': 'lag-4',
                                                                          'vlan': '100'}},
                                                'interface-one': {'address': '10.10.10.10',
                                                                  'mask': '30',
                                                                  'sap': {'port': '1/1/1',
                                                                          'vlan': '10'}},
                                                'interface-two': {'address': '10.10.10.100',
                                                                  'mask': '31',
                                                                  'sap': {'port': 'lag-5',
                                                                          'vlan': '80'}},
                                                'loopback': {'address': '10.10.10.1',
                                                             'mask': '32'}}],
                                'name': 'vprn1',
                                'ospf': {'admin_enabled': 'True',
                                         'area': '0.0.0.0',
                                         'interfaces': [{'name': 'interface-two',
                                                         'passive': 'True'}]}},
                          '2': {'admin_enabled': 'True',
                                'interfaces': [{'bgp-interface': {},
                                                'interface-two': {'address': '10.11.11.10',
                                                                  'mask': '31',
                                                                  'sap': {'port': 'lag-1',
                                                                          'vlan': '50'}},
                                                'loopback': {}}],
                                'name': 'vprn2',
                                'ospf': {'admin_enabled': 'True',
                                         'area': '0.0.0.0',
                                         'interfaces': [{'name': 'interface-two',
                                                         'passive': 'True'}]}},
                          '3': {'admin_enabled': 'True',
                                'interfaces': [{'interface-two': {'address': '10.12.12.100',
                                                                  'mask': '31',
                                                                  'sap': {'port': 'lag-5',
                                                                          'vlan': '33'}},
                                                'loopback': {'address': '10.12.12.12',
                                                             'mask': '32'}}],
                                'name': 'vprn3',
                                'ospf': {'admin_enabled': 'True',
                                         'area': '0.0.0.0',
                                         'interfaces': [{'name': 'interface-two',
                                                         'passive': 'True'}]}},
                          '4': {'admin_enabled': 'True',
                                'interfaces': [{'interface-two': {'address': '10.40.40.100',
                                                                  'ipv6': {'address': '1500:1000:460e::2222:1111',
                                                                           'mask': '64'},
                                                                  'mask': '31',
                                                                  'sap': {'port': 'lag-5',
                                                                          'vlan': '800'}},
                                                'loopback': {'address': '10.40.40.10',
                                                             'ipv6': {'address': '1500:1000:460e::a03:ae46',
                                                                      'mask': '128'},
                                                             'mask': '32'}}],
                                'name': 'ospf_version3_vprn',
                                'ospf': {'admin_enabled': 'True',
                                         'area': '0.0.0.0',
                                         'interfaces': [{'name': 'interface-two',
                                                         'passive': 'True'}]},
                                'ospf3': {'admin_enabled': 'True',
                                          'area': '0.0.0.0',
                                          'interfaces': [{'name': 'interface-two',
                                                          'passive': 'True'}]}},
                          '5': {'admin_enabled': 'True',
                                'bgp': {'admin_enabled': 'True',
                                        'peergroups': [{'name': 'eBGP',
                                                        'neighbors': [{'address': '10.50.50.201'}],
                                                        'remote_as': '4444'}]},
                                'interfaces': [{'bgp-interface': {'address': '10.50.50.200',
                                                                  'mask': '31',
                                                                  'sap': {'port': 'lag-1',
                                                                          'vlan': '602'}},
                                                'interface-two': {'address': '10.50.50.100',
                                                                  'mask': '31',
                                                                  'sap': {'port': 'lag-5',
                                                                          'vlan': '5'}},
                                                'loopback': {'address': '10.50.50.50',
                                                             'mask': '32'}}],
                                'name': 'vprn5',
                                'ospf': {'area': '0.0.0.0',
                                         'interfaces': [{'name': 'interface-two',
                                                         'passive': 'True'}]}}}]}}]]
    
# test_slack_answer_3_full()

def test_issue_45_for_junos_cfg():
    data = """
system {
    host-name LAB-MX-1;
    time-zone some/time;
    default-address-selection;
    no-redirects;
    no-ping-record-route;
    no-ping-time-stamp;
    tacplus-server {
        1.1.1.1 {
            port 49;
            secret "<SECRET_HASH>"; ## SECRET-DATA
            source-address 5.5.5.5;
        }
        2.2.2.2 {
            port 49;
            secret "<SECRET_HASH>"; ## SECRET-DATA
            source-address 5.5.5.5;
        }
        4.4.4.4 {
            port 49;
            secret "<SECRET_HASH>"; ## SECRET-DATA
            source-address 5.5.5.5;
        }
    }
    services {
        ssh {
            root-login deny;
            no-tcp-forwarding;
            protocol-version v2;
            max-sessions-per-connection 32;
            client-alive-count-max 3;
            client-alive-interval 10;
            connection-limit 10;
            rate-limit 5;
        }
        netconf {
            ssh {
                connection-limit 10;
                rate-limit 4;
            }
        }
    }
}
    """
    template = """
<group name="system_level">
system { {{ _start_ }}
    host-name {{ HOSTNAME }};
    time-zone {{ TZ }};
    default-address-selection; {{ default_address_selection | set(True) }}
    no-redirects; {{ no_redirects | set(True) }}
    no-ping-record-route; {{ no_ping_record_route | set(True) }}
    no-ping-time-stamp; {{ no_ping_time_stamp | set(True) }}
    
 <group name="services">
    services { {{ _start_ }}
    <group name="{{ service }}">
        {{ service }} {
            http; {{ http | set(true) }}
            https; {{ https | set(true) }}
            no-tcp-forwarding; {{ no-tcp-fwding | set(true) }}
            protocol-version {{ ssh-proto }};
            connection-limit {{ connection-limit | DIGIT }};
            rate-limit {{rate-limit | DIGIT }};
            root-login deny; {{ root-login | set(false) }}
            max-sessions-per-connection {{ max-sessions | DIGIT }};
            client-alive-count-max {{ client-alive-count-max | DIGIT }};
            client-alive-interval {{ client-alive-interval | DIGIT }};
          <group name="ssh">
            ssh; {{ ssh | set(true) }}
          </group>
          <group name="ssh">
            ssh { {{ _start_ }}
                connection-limit {{ connection-limit | DIGIT }};
                rate-limit {{ rate-limit | DIGIT }};
            } {{ _end_ }}
          </group>
        } {{ _end_ }}
    </group>
    } {{ _end_ }}
 </group>
 <group name="internet-options">
    internet-options { {{ _start_ }}
        icmpv4-rate-limit packet-rate {{ packet-rate| DIGIT }};
        icmpv6-rate-limit packet-rate {{ packet-rate| DIGIT }};
        no-source-quench; {{ no-source-quench | set(true) }}
        tcp-drop-synfin-set; {{ tcp-drop-synfin-set | set(true) }}
        no-tcp-reset {{ no-tcp-reset }};
    } {{ _end_ }}
 </group>
    authentication-order [{{ authentication-order }}];
 <group name="ports">
    ports { {{ _start_ }}
        auxiliary disable; {{ auxiliary | set(false) }}
    } {{ _end_ }}
 </group>
 <group name="root-authentication">
    root-authentication { {{ _start_ }}
        encrypted-password "{{ encrypted-password }}"; ## SECRET-DATA
    } {{ _end_ }}
 </group>
 <group name="dns" itemize="name_server">
    name-server {  {{ _start_ }}
        {{ name_server | IP | _line_ | to_list }};
    } {{ _end_ }}
 </group>
 <group name="commit">
    commit { {{ _start_ }}
        synchronize; {{ commit_sync | set(true) }}
        persist-groups-inheritance; {{ commit_persist-groups-inherit | set(true) }}
    } {{ _end_ }}
 </group> 
 <group name="tacacs">
    tacplus-server { {{ _start_ }}
       <group name="tacacs-servers.{{ tac_server }}">
        {{ tac_server | IP }} {
            port {{ tac_port }};
            secret "{{ tac_secret }}"; ## SECRET-DATA
            source-address {{ tac_source | IP }};
        } {{ end }}
        </group>
    } {{ end }}
 </group>
} {{ end }}
</group>
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=100)
    assert res == [[{'system_level': {'HOSTNAME': 'LAB-MX-1',
                                      'TZ': 'some/time',
                                      'default_address_selection': True,
                                      'no_ping_record_route': True,
                                      'no_ping_time_stamp': True,
                                      'no_redirects': True,
                                      'services': {'netconf': {'ssh': {'connection-limit': '10', 'rate-limit': '4'}},
                                                   'ssh': {'client-alive-count-max': '3',
                                                           'client-alive-interval': '10',
                                                           'connection-limit': '10',
                                                           'max-sessions': '32',
                                                           'no-tcp-fwding': True,
                                                           'rate-limit': '5',
                                                           'root-login': False,
                                                           'ssh-proto': 'v2'}},
                                      'tacacs': {'tacacs-servers': {'1.1.1.1': {'tac_port': '49',
                                                                                'tac_secret': '<SECRET_HASH>',
                                                                                'tac_source': '5.5.5.5'},
                                                                    '2.2.2.2': {'tac_port': '49',
                                                                                'tac_secret': '<SECRET_HASH>',
                                                                                'tac_source': '5.5.5.5'},
                                                                    '4.4.4.4': {'tac_port': '49',
                                                                                'tac_secret': '<SECRET_HASH>',
                                                                                'tac_source': '5.5.5.5'}}}}}]]
    
# test_issue_45_for_junos_cfg()