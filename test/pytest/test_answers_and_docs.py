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