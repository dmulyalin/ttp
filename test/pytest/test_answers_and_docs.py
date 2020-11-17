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
    parser = ttp(data, template)
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