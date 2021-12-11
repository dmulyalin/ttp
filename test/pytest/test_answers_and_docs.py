import sys

sys.path.insert(0, "../..")
import pprint
import pytest
import logging

logging.basicConfig(level=logging.DEBUG)

from ttp import ttp


def test_answer_1():
    """https://stackoverflow.com/questions/63522291/parsing-blocks-of-text-within-a-file-into-objects"""
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
    assert res == [
        {
            "author": "Christian Wulff-Nilsen",
            "index": "555036b37cea80f954149ffc",
            "info": "Approximate Distance Oracles with Improved Query Time.",
            "title": "Encyclopedia of Algorithms",
            "year": "2015",
        },
        {
            "author": "Julián Mestre",
            "index": "555036b37cea80f954149ffd",
            "info": "Subset Sum Algorithm for Bin Packing.",
            "title": "Encyclopedia of Algorithms",
            "year": "2015",
        },
    ]


# test_answer_1()


def test_answer_2():
    """https://stackoverflow.com/questions/63499479/extract-value-from-text-string-using-format-string-in-python"""
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
    assert res == [
        {"age": "1001", "name": "username1"},
        {"age": "1002", "name": "username2"},
        {"age": "1003", "name": "username3"},
    ]


# test_answer_2()


def test_issue_20_answer():
    data_to_parse = """
(*, 239.100.100.100)    
    LISP0.4200, (192.2.101.65, 232.0.3.1), Forward/Sparse, 1d18h/stopped
    LISP0.4201, (192.2.101.70, 232.0.3.1), Forward/Sparse, 2d05h/stopped

(192.2.31.3, 239.100.100.100), 6d20h/00:02:23, flags: FT
  Incoming interface: Vlan1029, RPF nbr 0.0.0.0
  Outgoing interface list:
    LISP0.4100, (192.2.101.70, 232.0.3.1), Forward/Sparse, 1d18h/stopped

"""

    show_mcast1 = """
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
    assert res == {
        "mcast": {
            "mcast_entries": {
                "'*'": {
                    "oil_entries": [
                        {
                            "oil_state_or_timer": "stopped",
                            "oil_uptime": "1d18h",
                            "outgoing_intf": "LISP0.4200",
                            "underlay_grp": "232.0.3.1",
                            "underlay_src": "192.2.101.65",
                        },
                        {
                            "oil_state_or_timer": "stopped",
                            "oil_uptime": "2d05h",
                            "outgoing_intf": "LISP0.4201",
                            "underlay_grp": "232.0.3.1",
                            "underlay_src": "192.2.101.70",
                        },
                    ],
                    "overlay_grp": "239.100.100.100",
                },
                "192.2.31.3": {
                    "entry_flags": "FT",
                    "entry_state_or_timer": "00:02:23",
                    "entry_uptime": "6d20h",
                    "incoming_intf": "Vlan1029",
                    "oil_entries": [
                        {
                            "oil_state_or_timer": "stopped",
                            "oil_uptime": "1d18h",
                            "outgoing_intf": "LISP0.4100",
                            "underlay_grp": "232.0.3.1",
                            "underlay_src": "192.2.101.70",
                        }
                    ],
                    "overlay_grp": "239.100.100.100",
                    "rpf_neighbor": "0.0.0.0",
                },
            }
        }
    }


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
    template = """
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
    assert res == {
        "VIP_cfg": {
            "1.1.1.1": {
                "config_state": "dis",
                "ipver": "v4",
                "rtsrcmac": "ena",
                "services": {
                    "443": {
                        "https": {
                            "dbind": "forceproxy",
                            "group_seq": "15",
                            "pbind": "clientip",
                            "real_port": "443",
                        },
                        "https/http": {"httpmod": "hsts_insert", "xforward": "ena"},
                    },
                    "80": {
                        "http": {
                            "dbind": "forceproxy",
                            "group_seq": "15",
                            "pbind": "clientip",
                            "real_port": "80",
                        },
                        "http/http": {"xforward": "ena"},
                    },
                },
                "ssl_profile": {
                    "ssl": "https/ssl",
                    "ssl_profile": "ssl-Policy",
                    "ssl_server_cert": "certname",
                    "virt_seq": "12",
                },
                "vip_name": "my name",
                "virt_seq": "12",
            },
            "1.1.4.4": {
                "config_state": "dis",
                "ipver": "v4",
                "rtsrcmac": "ena",
                "vip_name": "my name2",
                "virt_seq": "14",
            },
        }
    }


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
    template = """
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
    assert res == {
        "VIP_cfg": {
            "1.1.1.1": {
                "config_state": "dis",
                "ipver": "v4",
                "rtsrcmac": "ena",
                "services": {
                    "443": {
                        "dbind": "forceproxy",
                        "group_seq": "15",
                        "pbind": "clientip",
                        "proto": "https",
                        "real_port": "443",
                    },
                    "80": {
                        "dbind": "forceproxy",
                        "group_seq": "15",
                        "pbind": "clientip",
                        "proto": "http",
                        "real_port": "80",
                    },
                },
                "ssl_profile": {
                    "ssl": "https/ssl",
                    "ssl_profile": "ssl-Policy",
                    "ssl_server_cert": "certname",
                    "virt_seq": "12",
                },
                "vip_name": "my name",
                "virt_seq": "12",
            },
            "1.1.4.4": {
                "config_state": "dis",
                "ipver": "v4",
                "rtsrcmac": "ena",
                "vip_name": "my name2",
                "virt_seq": "14",
            },
        }
    }


# test_answer_4()


def test_issue_20_answer_2():
    data_to_parse = """
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
    show_mcast1 = """
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
    assert res == {
        "mcast": {
            "mcast_entries": {
                "'*'": [
                    {"overlay_grp": "239.100.100.101"},
                    {
                        "entry_flags": "S",
                        "entry_state_or_timer": "00:03:28",
                        "entry_uptime": "6d20h",
                        "incoming_intf": "Null",
                        "oil_entries": [
                            {
                                "oil_state_or_timer": "00:03:28",
                                "oil_uptime": "1d18h",
                                "outgoing_intf": "Vlan3014",
                                "underlay_grp": "232.0.3.1",
                                "underlay_src": "192.2.101.65",
                            }
                        ],
                        "overlay_grp": "239.100.100.100",
                        "rp": "192.2.199.1",
                        "rpf_neighbor": "0.0.0.0",
                    },
                ],
                "192.2.31.3": {
                    "entry_flags": "FT",
                    "entry_state_or_timer": "00:01:19",
                    "entry_uptime": "2d05h",
                    "incoming_intf": "Vlan1029",
                    "overlay_grp": "239.100.100.100",
                    "rpf_neighbor": "0.0.0.0",
                },
            }
        }
    }


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
    assert res == [
        [
            [
                {
                    "interface": "Lo0",
                    "ip": "124.171.238.50/29",
                    "last_host": "124.171.238.54",
                },
                {"interface": "Lo1", "ip": "1.1.1.1/30", "last_host": "1.1.1.2"},
            ]
        ]
    ]


# test_docs_ttp_dictionary_usage_example()


def test_github_issue_21_answer():
    data_to_parse = """
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
    assert res == {
        "nbar": {
            "GigabitEthernet1 ": {
                "Total": {
                    "IN 5min Bit Rate (bps)": 2000,
                    "IN 5min Max Bit Rate (bps)": 8000,
                    "IN Byte Count": 122943,
                    "IN Packet Count": 874,
                    "OUT 5min Bit Rate (bps)": 1000,
                    "OUT 5min Max Bit Rate (bps)": 2000,
                    "OUT Byte Count": 130764,
                    "OUT Packet Count": 1781,
                },
                "dns": {
                    "IN 5min Bit Rate (bps)": 0,
                    "IN 5min Max Bit Rate (bps)": 2000,
                    "IN Byte Count": 21149,
                    "IN Packet Count": 107,
                    "OUT 5min Bit Rate (bps)": 0,
                    "OUT 5min Max Bit Rate (bps)": 0,
                    "OUT Byte Count": 0,
                    "OUT Packet Count": 0,
                },
                "ldp": {
                    "IN 5min Bit Rate (bps)": 0,
                    "IN 5min Max Bit Rate (bps)": 0,
                    "IN Byte Count": 13224,
                    "IN Packet Count": 174,
                    "OUT 5min Bit Rate (bps)": 0,
                    "OUT 5min Max Bit Rate (bps)": 0,
                    "OUT Byte Count": 13300,
                    "OUT Packet Count": 175,
                },
                "ospf": {
                    "IN 5min Bit Rate (bps)": 0,
                    "IN 5min Max Bit Rate (bps)": 0,
                    "IN Byte Count": 9460,
                    "IN Packet Count": 86,
                    "OUT 5min Bit Rate (bps)": 0,
                    "OUT 5min Max Bit Rate (bps)": 0,
                    "OUT Byte Count": 9570,
                    "OUT Packet Count": 87,
                },
                "ping": {
                    "IN 5min Bit Rate (bps)": 0,
                    "IN 5min Max Bit Rate (bps)": 1000,
                    "IN Byte Count": 14592,
                    "IN Packet Count": 144,
                    "OUT 5min Bit Rate (bps)": 0,
                    "OUT 5min Max Bit Rate (bps)": 1000,
                    "OUT Byte Count": 14592,
                    "OUT Packet Count": 144,
                },
                "ssh": {
                    "IN 5min Bit Rate (bps)": 2000,
                    "IN 5min Max Bit Rate (bps)": 1999,
                    "IN Byte Count": 24805,
                    "IN Packet Count": 191,
                    "OUT 5min Bit Rate (bps)": 1000,
                    "OUT 5min Max Bit Rate (bps)": 1001,
                    "OUT Byte Count": 22072,
                    "OUT Packet Count": 134,
                },
                "unknown": {
                    "IN 5min Bit Rate (bps)": 0,
                    "IN 5min Max Bit Rate (bps)": 3000,
                    "IN Byte Count": 39713,
                    "IN Packet Count": 172,
                    "OUT 5min Bit Rate (bps)": 0,
                    "OUT 5min Max Bit Rate (bps)": 0,
                    "OUT Byte Count": 31378,
                    "OUT Packet Count": 503,
                },
                "vrrp": {
                    "IN 5min Bit Rate (bps)": 0,
                    "IN 5min Max Bit Rate (bps)": 0,
                    "IN Byte Count": 0,
                    "IN Packet Count": 0,
                    "OUT 5min Bit Rate (bps)": 0,
                    "OUT 5min Max Bit Rate (bps)": 0,
                    "OUT Byte Count": 39852,
                    "OUT Packet Count": 738,
                },
            }
        }
    }


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
    assert res == [[[{"ip_address": "192.2.101.70"}, {"ip_address": "192.2.101.71"}]]]


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
    assert res == {
        "VIP_cfg": {
            "19": {
                "services": [
                    {
                        "pool": [
                            {
                                "node_id": "22",
                                "node_ip": "10.10.10.10",
                                "reason": "N/A",
                            },
                            {
                                "node_id": "23",
                                "node_ip": "10.11.11.11",
                                "reason": "N/A",
                            },
                        ],
                        "rport": "http",
                        "vs_service": "http",
                    },
                    {
                        "pool": [
                            {
                                "node_id": "22",
                                "node_ip": "10.10.10.10",
                                "reason": "N/A",
                            },
                            {
                                "node_id": "23",
                                "node_ip": "10.11.11.11",
                                "reason": "N/A",
                            },
                        ],
                        "rport": "https",
                        "vs_service": "https",
                    },
                ],
                "vs_ip": "1.1.1.1",
            }
        }
    }


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
    assert res == [
        '"Hostname","Port_Number","Untagged_VLAN","Tagged_VLAN"\n"SWITCH","2/11","101","60 70 105 116 117"\n"SWITCH","2/12","103","61 71"'
    ]


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
    assert res == [
        [
            {
                "ospf": {
                    "areas": [
                        {
                            "area": "0.0.0.1",
                            "area_type": "nssa",
                            "nssa_default_metric": "10",
                            "nssa_default_metric_type": "2",
                            "nssa_redis": "enable",
                            "stub_type": "summary",
                        }
                    ],
                    "default_originate_metric": "10",
                    "default_originate_metric_type": "2",
                    "default_rt_metric": "10",
                    "dist_list_in": "OSPF_IMPORT_PREFIX",
                    "interfaces": [
                        {
                            "interface": "Vlan1",
                            "name": "vlan1-int",
                            "network": "point-to-point",
                            "priority": "1",
                            "status": "enable",
                        },
                        {
                            "interface": "vlan2",
                            "name": "vlan2-int",
                            "network": "point-to-point",
                            "priority": "1",
                            "status": "enable",
                        },
                    ],
                    "networks": [
                        {"area": "0.0.0.1", "id": "1", "prefix": "10.1.1.1/30"},
                        {"area": "0.0.0.1", "id": "2", "prefix": "10.1.1.3/30"},
                    ],
                    "redistribute": [
                        {
                            "metric-type": "2",
                            "protocol": "connected",
                            "status": "enable",
                        },
                        {"metric-type": "2", "protocol": "static", "status": "enable"},
                        {"metric-type": "2", "protocol": "bgp", "status": "enable"},
                    ],
                    "ref_bw": "1000",
                    "router_id": "10.1.1.1",
                }
            }
        ]
    ]


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
    assert res == [
        {
            "export-route-targets": "65001:48;65001:0",
            "id": "*c",
            "import-route-targets": "65001:48",
            "interfaces": "lo-ext;vlan56",
            "route-distinguisher": "65001:48",
            "routing-mark": "VRF_EXT",
        },
        {
            "comment": "=",
            "export-route-targets": "65001:80",
            "id": "*10",
            "import-route-targets": "65001:80;65001:0",
            "interfaces": "lo-private",
            "route-distinguisher": "65001:80",
            "routing-mark": "VRF_PRIVATE",
        },
    ]


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
    assert res == [
        {
            "versions": [
                {"type": "firmware", "version": "02.1.1 Build 002"},
                {"type": "hardware", "version": "V2R4"},
            ]
        }
    ]


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
    assert res == [
        [
            {
                "domain": {"fqdn": "Uncknown"},
                "uptime": {
                    "software": {"version": "uncknown"},
                    "uptime": "27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds",
                },
            }
        ]
    ]


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
    assert res == [[{"demo": {"audiences": [{"audience": []}]}}]]


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
    assert res == [
        [
            {
                "servers": [
                    {"server": "1.1.1.1", "servers_number": 1},
                    {"server": "2.2.2.2 3.3.3.3", "servers_number": 2},
                    {"server": "4.4.4.4 5.5.5.5 6.6.6.6", "servers_number": 3},
                ]
            }
        ]
    ]


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
    assert res == [
        [
            {
                "ip": {
                    "extended": {
                        "199": {
                            "10": [
                                {"action": "remark", "remark_name": "COLLECTOR - SNMP"},
                                {
                                    "action": "permit",
                                    "dest_any": "any",
                                    "protocol": "ip",
                                    "src_ntw": "70.70.70.0",
                                    "src_wildcard": "0.0.0.255",
                                },
                            ],
                            "20": [
                                {"action": "remark", "remark_name": "RETURN - Back"},
                                {
                                    "action": "permit",
                                    "dest_any": "any",
                                    "protocol": "ip",
                                    "src_ntw": "80.80.80.0",
                                    "src_wildcard": "0.0.0.127",
                                },
                            ],
                            "30": [
                                {"action": "remark", "remark_name": "VISUALIZE"},
                                {
                                    "action": "permit",
                                    "dest_any": "any",
                                    "protocol": "ip",
                                    "src_host": "90.90.90.138",
                                },
                            ],
                        }
                    },
                    "standard": {
                        "42": {
                            "10": [
                                {"action": "remark", "remark_name": "machine_A"},
                                {"action": "permit", "src_host": "192.168.200.162"},
                            ],
                            "20": [
                                {"action": "remark", "remark_name": "machine_B"},
                                {"action": "permit", "src_host": "192.168.200.149"},
                            ],
                            "30": [{"action": "deny", "log": "log", "src_host": "any"}],
                        },
                        "98": {
                            "10": [{"action": "permit", "src_host": "10.10.10.1"}],
                            "20": [
                                {"action": "remark", "remark_name": "toto"},
                                {"action": "permit", "src_host": "30.30.30.1"},
                            ],
                            "30": [
                                {
                                    "action": "permit",
                                    "src_ntw": "30.30.30.0",
                                    "src_wildcard": "0.0.0.255",
                                }
                            ],
                        },
                        "99": {
                            "10": [
                                {
                                    "action": "permit",
                                    "log": "log",
                                    "src_host": "10.20.30.40",
                                }
                            ],
                            "20": [
                                {
                                    "action": "permit",
                                    "log": "log",
                                    "src_host": "20.30.40.1",
                                }
                            ],
                            "30": [
                                {"action": "remark", "remark_name": "DEVICE - SNMP RW"},
                                {
                                    "action": "permit",
                                    "src_ntw": "50.50.50.128",
                                    "src_wildcard": "0.0.0.127",
                                },
                            ],
                            "40": [
                                {
                                    "action": "permit",
                                    "src_ntw": "60.60.60.64",
                                    "src_wildcard": "0.0.0.63",
                                }
                            ],
                        },
                    },
                }
            }
        ]
    ]


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
    assert res == [
        [
            {
                "service": {
                    "epipe": {
                        "103076": {
                            "customer_id": "160",
                            "description": "vf=EWL:cn=TATA_COM:tl=2C02495918:st=act:",
                            "regular_sdp": {
                                "8051": {"state": "enabled", "vc_id": "103076"}
                            },
                            "sap": {
                                "1/2/12:20.qinq": {
                                    "description": "vf=EWL:cn=TATA_COM:tl=2C02495890:st=act:",
                                    "egress": {
                                        "sap_egress": "1)",
                                        "scheduler_policy": "none",
                                    },
                                    "ingress": {
                                        "sap_ingress": "1",
                                        "scheduler_policy": "none",
                                    },
                                    "mss_name": "TATA_VSNL_STRAT_A206_LAN10",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1588",
                            "service_name": "EPIPE service-103076 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                        "103206": {
                            "customer_id": "1904",
                            "description": "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA "
                            "UK PLC Stepney Green E1 "
                            "3DG'",
                            "regular_sdp": {
                                "8035": {"state": "enabled", "vc_id": "103206"}
                            },
                            "sap": {
                                "2/2/3:401.100": {
                                    "description": "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA "
                                    "UK "
                                    "PLC "
                                    "Stepney "
                                    "Green "
                                    "E1 "
                                    "3DG'",
                                    "egress": {
                                        "sap_egress": "11010",
                                        "scheduler_policy": "none",
                                    },
                                    "ingress": {
                                        "sap_ingress": "11010",
                                        "scheduler_policy": "none",
                                    },
                                    "mss_name": "SKANSKA_E13DG_A825_LAN1",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1988",
                            "service_name": "EPIPE service-103206 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                        "103256": {
                            "customer_id": "160",
                            "description": "vf=EWL:cn=TATA_COMM:tl=2C02490189:st=act:",
                            "regular_sdp": {
                                "8139": {"state": "enabled", "vc_id": "103256"}
                            },
                            "sap": {
                                "1/2/12:15.qinq": {
                                    "description": "vf=EWL:cn=TATA_COMM:tl=2C02490171:st=act:",
                                    "egress": {
                                        "sap_egress": "11000",
                                        "scheduler_policy": "none",
                                    },
                                    "ingress": {
                                        "sap_ingress": "11000",
                                        "scheduler_policy": "none",
                                    },
                                    "mss_name": "TATA_VSNL_STRAT_A206_LAN5",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1988",
                            "service_name": "EPIPE service-103256 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                        "103742": {
                            "customer_id": "160",
                            "description": "vf=EWL:cn=TATA_COM:tl=2C02410363:st=act:",
                            "regular_sdp": {
                                "8061": {"state": "enabled", "vc_id": "103742"}
                            },
                            "sap": {
                                "5/2/50:20.qinq": {
                                    "description": "vf=EWL:cn=TATA_COM:tl=2C02410338:st=act:",
                                    "egress": {
                                        "sap_egress": "11000",
                                        "scheduler_policy": "none",
                                    },
                                    "ingress": {
                                        "sap_ingress": "11000",
                                        "scheduler_policy": "none",
                                    },
                                    "mss_name": "TATA_STRAT_LON_A206_LANA",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1588",
                            "service_name": "EPIPE service-103742 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                        "55517673": {
                            "customer_id": "4",
                            "description": "vf=EAGG:cn=Bulldog:tl=2C01291821:st=act:no=NGA "
                            "EPIPE#BAACTQ#VLAN 901",
                            "endpoint": {
                                "endpoint": '"SDP"',
                                "revert_time": "infinite",
                            },
                            "pwr_sdp": {
                                "8243": {
                                    "endpoint": '"SDP"',
                                    "precedence": "1",
                                    "state": "enabled",
                                    "vc_id": "55517673",
                                },
                                "8245": {
                                    "endpoint": '"SDP"',
                                    "precedence": "primary",
                                    "state": "enabled",
                                    "vc_id": "55517673",
                                },
                            },
                            "sap": {
                                "2/2/3:901.qinq": {
                                    "description": "2_2_3,H0505824A,Bulldog,VLAN "
                                    "901",
                                    "egress": {
                                        "sap_egress": "20010",
                                        "scheduler_policy": '"NGA-LLU-300M"',
                                    },
                                    "ingress": {
                                        "sap_ingress": "20010",
                                        "scheduler_policy": '"NGA-LLU-300M"',
                                    },
                                    "mss_name": "none",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1526",
                            "service_name": "epipe service-64585 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                    }
                }
            }
        ]
    ]


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
    pprint.pprint(res)
    assert res == [
        [
            {
                "service": {
                    "epipe": {
                        "103076": {
                            "customer_id": "160",
                            "regular_sdp": {
                                "8051": {"state": "enabled", "vc_id": "103076"}
                            },
                        },
                        "103206": {
                            "customer_id": "1904",
                            "regular_sdp": {
                                "8035": {"state": "enabled", "vc_id": "103206"}
                            },
                        },
                    }
                }
            }
        ]
    ]


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
    assert res == [
        [
            {
                "service": {
                    "epipe": {
                        "103076": {
                            "customer_id": "160",
                            "description": "vf=EWL:cn=TATA_COM:tl=2C02495918:st=act:",
                            "regular_sdp": {
                                "8051": {"state": "enabled", "vc_id": "103076"}
                            },
                            "sap": {
                                "1/2/12:20.qinq": {
                                    "description": "vf=EWL:cn=TATA_COM:tl=2C02495890:st=act:",
                                    "egress": {
                                        "sap_egress": "1)",
                                        "scheduler_policy": "none",
                                    },
                                    "ingress": {
                                        "sap_ingress": "1",
                                        "scheduler_policy": "none",
                                    },
                                    "mss_name": "TATA_VSNL_STRAT_A206_LAN10",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1588",
                            "service_name": "EPIPE service-103076 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                        "103206": {
                            "customer_id": "1904",
                            "description": "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA "
                            "UK PLC Stepney Green E1 "
                            "3DG'",
                            "regular_sdp": {
                                "8035": {"state": "enabled", "vc_id": "103206"}
                            },
                            "sap": {
                                "2/2/3:401.100": {
                                    "description": "vf=1273:cn=skanska:tl=3C02407455:st=act:no='SKANSKA "
                                    "UK "
                                    "PLC "
                                    "Stepney "
                                    "Green "
                                    "E1 "
                                    "3DG'",
                                    "egress": {
                                        "sap_egress": "11010",
                                        "scheduler_policy": "none",
                                    },
                                    "ingress": {
                                        "sap_ingress": "11010",
                                        "scheduler_policy": "none",
                                    },
                                    "mss_name": "SKANSKA_E13DG_A825_LAN1",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1988",
                            "service_name": "EPIPE service-103206 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                        "103256": {
                            "customer_id": "160",
                            "description": "vf=EWL:cn=TATA_COMM:tl=2C02490189:st=act:",
                            "regular_sdp": {
                                "8139": {"state": "enabled", "vc_id": "103256"}
                            },
                            "sap": {
                                "1/2/12:15.qinq": {
                                    "description": "vf=EWL:cn=TATA_COMM:tl=2C02490171:st=act:",
                                    "egress": {
                                        "sap_egress": "11000",
                                        "scheduler_policy": "none",
                                    },
                                    "ingress": {
                                        "sap_ingress": "11000",
                                        "scheduler_policy": "none",
                                    },
                                    "mss_name": "TATA_VSNL_STRAT_A206_LAN5",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1988",
                            "service_name": "EPIPE service-103256 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                        "103742": {
                            "customer_id": "160",
                            "description": "vf=EWL:cn=TATA_COM:tl=2C02410363:st=act:",
                            "regular_sdp": {
                                "8061": {"state": "enabled", "vc_id": "103742"}
                            },
                            "sap": {
                                "5/2/50:20.qinq": {
                                    "description": "vf=EWL:cn=TATA_COM:tl=2C02410338:st=act:",
                                    "egress": {
                                        "sap_egress": "11000",
                                        "scheduler_policy": "none",
                                    },
                                    "ingress": {
                                        "sap_ingress": "11000",
                                        "scheduler_policy": "none",
                                    },
                                    "mss_name": "TATA_STRAT_LON_A206_LANA",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1588",
                            "service_name": "EPIPE service-103742 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                        "55517673": {
                            "customer_id": "4",
                            "description": "vf=EAGG:cn=Bulldog:tl=2C01291821:st=act:no=NGA "
                            "EPIPE#BAACTQ#VLAN 901",
                            "endpoint": {
                                "endpoint": '"SDP"',
                                "revert_time": "infinite",
                            },
                            "pwr_sdp": {
                                "8243": {
                                    "endpoint": '"SDP"',
                                    "precedence": "1",
                                    "state": "enabled",
                                    "vc_id": "55517673",
                                },
                                "8245": {
                                    "endpoint": '"SDP"',
                                    "precedence": "primary",
                                    "state": "enabled",
                                    "vc_id": "55517673",
                                },
                            },
                            "sap": {
                                "2/2/3:901.qinq": {
                                    "description": "2_2_3,H0505824A,Bulldog,VLAN "
                                    "901",
                                    "egress": {
                                        "sap_egress": "20010",
                                        "scheduler_policy": '"NGA-LLU-300M"',
                                    },
                                    "ingress": {
                                        "sap_ingress": "20010",
                                        "scheduler_policy": '"NGA-LLU-300M"',
                                    },
                                    "mss_name": "none",
                                    "state": "enabled",
                                }
                            },
                            "service_mtu": "1526",
                            "service_name": "epipe service-64585 "
                            "DKTN08a-D0105 "
                            "(63.130.108.41)",
                            "state": "enabled",
                        },
                    }
                }
            }
        ]
    ]


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
    assert res == [
        [
            {
                "vrfs": {
                    "name": "xyz",
                    "route-targets": [
                        {
                            "import": [
                                "65000:3507",
                                "65000:3511",
                                "65000:5453",
                                "65000:5535",
                            ]
                        },
                        {"export": ["65000:5453", "65000:5535"]},
                    ],
                }
            }
        ]
    ]


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
    assert res == [
        [
            {
                "vrfs": {
                    "export_rts": [
                        {"export_rt": "65000:5453"},
                        {"export_rt": "65000:5535"},
                    ],
                    "import_rts": [
                        {"import_rt": "65000:3507"},
                        {"import_rt": "65000:3511"},
                        {"import_rt": "65000:5453"},
                        {"import_rt": "65000:5535"},
                    ],
                    "name": "xyz",
                }
            }
        ]
    ]


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
    pprint.pprint(res)
    # assert res == [
    #     [
    #         {
    #             "vrfs": [
    #                 {
    #                     "forwarding_options": {
    #                         "dhcp_relay": {
    #                             "groups": [
    #                                 {
    #                                     "group_name": "group2",
    #                                     "server_group_name2": "IN_MEDIA_SIGNALING",
    #                                 },
    #                                 {
    #                                     "group_name": "NGN-SIG",
    #                                     "server_group_name2": "DHCP-NGN-SIG",
    #                                 },
    #                             ],
    #                             "server_group": {
    #                                 "dhcp": [
    #                                     {
    #                                         "helper_addresses": [
    #                                             {"helper_address": "10.154.6.147"}
    #                                         ],
    #                                         "server_group_name1": "IN_MEDIA_SIGNALING",
    #                                     },
    #                                     {
    #                                         "helper_addresses": [
    #                                             {"helper_address": "10.154.6.147"}
    #                                         ],
    #                                         "server_group_name1": "DHCP-NGN-SIG",
    #                                     },
    #                                     {"server_group_name1": "overrides"},
    #                                     {"server_group_name1": "overrides"},
    #                                 ]
    #                             },
    #                         }
    #                     },
    #                     "name": "vrf2",
    #                 }
    #             ]
    #         }
    #     ]
    # ]
    # was able to fix the issue by introducing ended_groups tracking in results
    # processing while was trying to fix issue 57
    assert res == [
        [
            {
                "vrfs": [
                    {
                        "forwarding_options": {
                            "dhcp_relay": {
                                "groups": [
                                    {
                                        "group_name": "group2",
                                        "server_group_name2": "IN_MEDIA_SIGNALING",
                                    },
                                    {
                                        "group_name": "NGN-SIG",
                                        "server_group_name2": "DHCP-NGN-SIG",
                                    },
                                ],
                                "server_group": {
                                    "dhcp": [
                                        {
                                            "helper_addresses": [
                                                {"helper_address": "10.154.6.147"}
                                            ],
                                            "server_group_name1": "IN_MEDIA_SIGNALING",
                                        },
                                        {
                                            "helper_addresses": [
                                                {"helper_address": "10.154.6.147"}
                                            ],
                                            "server_group_name1": "DHCP-NGN-SIG",
                                        },
                                    ]
                                },
                            }
                        },
                        "name": "vrf2",
                    }
                ]
            }
        ]
    ]


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
    assert res == [
        [
            {
                "vrfs": [
                    {
                        "forwarding_options": {
                            "dhcp_relay": {
                                "groups": [{"group_name": "NGN-SIG"}],
                                "server_group": {
                                    "dhcp": [
                                        {"server_group_name": "IN_MEDIA_SIGNALING"},
                                        {"server_group_name": "overrides"},
                                    ]
                                },
                            }
                        },
                        "name": "vrf2",
                    }
                ]
            }
        ]
    ]


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
    assert res == [
        [
            {
                "vrfs": [
                    {
                        "forwarding_options": {
                            "dhcp_relay": {
                                "groups": [
                                    {
                                        "group_name": "group2",
                                        "server_group_name2": "IN_MEDIA_SIGNALING",
                                    },
                                    {
                                        "group_name": "NGN-SIG",
                                        "server_group_name2": "DHCP-NGN-SIG",
                                    },
                                ],
                                "server_group": {
                                    "dhcp": [
                                        {
                                            "helper_addresses": [
                                                {"helper_address": "10.154.6.147"}
                                            ],
                                            "server_group_name1": "IN_MEDIA_SIGNALING",
                                        },
                                        {
                                            "helper_addresses": [
                                                {"helper_address": "10.154.6.147"}
                                            ],
                                            "server_group_name1": "DHCP-NGN-SIG",
                                        },
                                    ]
                                },
                            }
                        },
                        "name": "vrf2",
                    }
                ]
            }
        ]
    ]


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
    assert res == [
        [
            [
                {
                    "description": "Router-id-loopback",
                    "interface": "Loopback0",
                    "ip": "192.168.0.113",
                    "mask": "24",
                },
                {
                    "description": "Router-id-loopback 2",
                    "interface": "Loopback2",
                    "ip": "192.168.0.114",
                    "mask": "24",
                },
                {
                    "description": "Router-id-loopback 3",
                    "interface": "Loopback3",
                    "ip": "192.168.0.115",
                    "mask": "24",
                },
            ]
        ]
    ]


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
    assert res == [
        [
            [
                {
                    "code": "3400",
                    "course": "ECON",
                    "department": "Department of Economics and Finance",
                    "description": "In this course, we examine the economics of personnel management in organizations.\n"
                    "Using mainstream microeconomic and behavioural economic theory, we will consider\n"
                    "such issues as recruitment, promotion, financial and non-financial incentives,\n"
                    "compensation, job performance, performance evaluation, and investment in personnel.\n"
                    "The interplay between theoretical models and empirical evidence will be emphasized in\n"
                    "considering different approaches to the management of personnel.",
                    "lecture_lab_time": "3-0",
                    "name": "The Economics of Personnel Management",
                    "prereqs": "ECON*2310 or ECON*2200",
                    "semester": "U",
                    "weight": "0.50",
                },
                {
                    "code": "4400",
                    "course": "ECON",
                    "department": "Department of Economics",
                    "description": "In this course, we examine the economics of personnel management in organizations.\n"
                    "Using mainstream microeconomic and behavioural economic theory, we will consider\n"
                    "such issues as recruitment, promotion, financial and non-financial incentives,\n"
                    "compensation, job performance, performance evaluation, and investment in personnel.",
                    "lecture_lab_time": "7-1",
                    "name": "The Economics of Personnel Management",
                    "prereqs": "ECON*2310",
                    "semester": "U",
                    "weight": "0.90",
                },
            ]
        ]
    ]


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
    pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {
                    "code": "4521",
                    "course": "IBIO",
                    "department": "Department of Integrative Biology",
                    "description": "This course is the first part of the two-semester course IBIO*4521/2. This course is\n"
                    "a two-semester (F,W) undergraduate project in which students conduct a comprehensive,\n"
                    "independent research project in organismal biology under the supervision of a faculty\n"
                    "member in the Department of Integrative Biology. Projects involve a thorough literature\n"
                    "review, a research proposal, original research communicated in oral and poster\n"
                    "presentations, and in a written, publication quality document. This two-semester course\n"
                    "offers students the opportunity to pursue research questions and experimental designs\n"
                    "that cannot be completed in the single semester research courses. Students must make\n"
                    "arrangements with both a faculty supervisor and the course coordinator at least one\n"
                    "semester in advance. A departmental registration form must be obtained from the course\n"
                    "coordinator and submitted no later than the second class day of the fall semester. This is\n"
                    "a twosemester course offered over consecutive semesters F-W. When you select this\n"
                    "course, you must select IBIO*4521 in the Fall semester and IBIO*4522 in the Winter\n"
                    "semester.A grade will not be assigned to IBIO*4521 until IBIO*4522 has been completed.",
                    "lecture_lab_time": "0-12",
                    "name": "Thesis in Integrative Biology",
                    "prereqs": "12.00 credits",
                    "restrictions": "Normally a minimum cumulative average of 70%. Permission of course\ncoordinator.",
                    "semester": "F",
                    "weight": "1.00",
                },
                {
                    "code": "4533",
                    "course": "IBIO",
                    "department": "Department of Integrative Biology",
                    "description": "This course is the first part of the two-semester course IBIO*4521/2. This course is\n"
                    "a two-semester (F,W) undergraduate project in which students conduct a comprehensive,\n"
                    "independent research project in organismal biology under the supervision of a faculty\n"
                    "member in the Department of Integrative Biology.",
                    "lecture_lab_time": "0-14",
                    "name": "Thesis in Integrative Biology",
                    "restrictions": "Normally a minimum cumulative average of 80%. Permission of course\n"
                    "coordinator. Normally a minimum cumulative average of 90%. Permission of course\n"
                    "coordinator.",
                    "semester": "F",
                    "weight": "2.00",
                },
            ]
        ]
    ]


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
    assert res == [
        {
            "comment": "",
            "disabled": False,
            "interface": "lo0",
            "ip": "10.4.1.245",
            "network": "10.4.1.245",
        },
        {
            "comment": "",
            "disabled": False,
            "interface": "lo1",
            "ip": "10.4.1.246",
            "network": "10.4.1.246",
        },
        {
            "comment": "SITEMON",
            "disabled": False,
            "interface": "ether2",
            "ip": "10.9.48.241",
            "mask": "29",
            "network": "10.9.48.240",
        },
        {
            "comment": "Camera",
            "disabled": False,
            "interface": "vlan205@bond1",
            "ip": "10.9.48.233",
            "mask": "29",
            "network": "10.9.48.232",
        },
        {
            "comment": "SM-Management",
            "disabled": False,
            "interface": "vlan200@bond1",
            "ip": "10.9.49.1",
            "mask": "24",
            "network": "10.9.49.0",
        },
        {
            "comment": "to core01",
            "disabled": False,
            "interface": "vlan996@bond4",
            "ip": "10.4.1.130",
            "mask": "30",
            "network": "10.4.1.128",
        },
        {
            "comment": "BH 01",
            "disabled": False,
            "interface": "vlan210@bond1",
            "ip": "10.4.250.28",
            "mask": "29",
            "network": "10.4.250.24",
        },
        {
            "comment": "Cust: site01-PE",
            "disabled": False,
            "interface": "vlan11@bond1",
            "ip": "10.9.50.13",
            "mask": "30",
            "network": "10.9.50.12",
        },
        {
            "comment": "",
            "disabled": "yes",
            "interface": "bridge:customer99",
            "ip": "10.0.0.2",
            "mask": "30",
            "network": "10.0.0.0",
        },
        {
            "comment": "Cambium",
            "disabled": "yes",
            "interface": "vlan200@bond1",
            "ip": "169.254.1.100",
            "mask": "24",
            "network": "169.254.1.0",
        },
        {
            "comment": "Backhaul to AGR (Test Segment)",
            "disabled": "yes",
            "interface": "vlan209@bond1",
            "ip": "10.4.248.20",
            "mask": "29",
            "network": "10.4.248.16",
        },
    ]


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
    assert res == [
        [
            {
                "system": {
                    "ports": [
                        {
                            "admin_enabled": True,
                            "description": "port 1 description",
                            "ethernet": {
                                "encap_type": "dot1q",
                                "lldp_enabled": True,
                                "mode": "hybrid",
                                "network": {
                                    "accounting_policy": "12",
                                    "collect_stats": True,
                                    "egress": {
                                        "queuegroups": [
                                            {
                                                "agg_rate": "50000",
                                                "name": "qos-policy-for-router1",
                                            }
                                        ]
                                    },
                                    "queue_policy": "ncq-only",
                                },
                            },
                            "id": "1/1/1",
                        },
                        {
                            "admin_enabled": True,
                            "description": "another port to a another router",
                            "ethernet": {
                                "egress_sched_policy": "qos-port-scheduler",
                                "encap_type": "dot1q",
                                "mode": "hybrid",
                            },
                            "id": "1/1/2",
                        },
                        {
                            "admin_enabled": True,
                            "description": "port 3 to some third router",
                            "ethernet": {
                                "egress_sched_policy": "strict-scheduler",
                                "encap_type": "dot1q",
                                "mode": "access",
                                "mtu": "2000",
                                "network": {
                                    "accounting_policy": "12",
                                    "collect_stats": True,
                                    "egress": {
                                        "queuegroups": [
                                            {
                                                "agg_rate": "50000",
                                                "name": "some-shaping-policy",
                                            },
                                            {
                                                "agg_rate": "50000",
                                                "name": "another-shaping-policy",
                                            },
                                            {
                                                "agg_rate": "1000000",
                                                "name": "this-shaper-is-cool",
                                            },
                                        ]
                                    },
                                    "queue_policy": "ncq-only",
                                },
                            },
                            "id": "1/1/3",
                        },
                    ]
                }
            }
        ]
    ]


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
    template = """
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
    assert res == [
        [
            {
                "service": {
                    "vprns": [
                        {
                            "4": {
                                "name": "ospf_version3_vprn",
                                "ospf": {
                                    "area": "0.0.0.0",
                                    "interfaces": [{"name": "interface-one"}],
                                },
                                "ospf3": {
                                    "area": "0.0.0.0",
                                    "interfaces": [{"name": "interface-two"}],
                                },
                            },
                            "5": {
                                "name": "vprn5",
                                "ospf": {
                                    "area": "0.0.0.0",
                                    "interfaces": [{"name": "interface-three"}],
                                },
                            },
                        }
                    ]
                }
            }
        ]
    ]


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
    pprint.pprint(res, width=100)
    assert res == [
        [
            {
                "service": {
                    "vprns": [
                        {
                            "1": {
                                "admin_enabled": "True",
                                "interfaces": [
                                    {
                                        "bgp-interface": {
                                            "address": "10.10.10.200",
                                            "mask": "31",
                                            "sap": {"port": "lag-4", "vlan": "100"},
                                        },
                                        "interface-one": {
                                            "address": "10.10.10.10",
                                            "mask": "30",
                                            "sap": {"port": "1/1/1", "vlan": "10"},
                                        },
                                        "interface-two": {
                                            "address": "10.10.10.100",
                                            "mask": "31",
                                            "sap": {"port": "lag-5", "vlan": "80"},
                                        },
                                        "loopback": {
                                            "address": "10.10.10.1",
                                            "mask": "32",
                                        },
                                    }
                                ],
                                "name": "vprn1",
                                "ospf": {
                                    "admin_enabled": "True",
                                    "area": "0.0.0.0",
                                    "interfaces": [
                                        {"name": "interface-two", "passive": "True"}
                                    ],
                                },
                            },
                            "2": {
                                "admin_enabled": "True",
                                "interfaces": [
                                    {
                                        "bgp-interface": {},
                                        "interface-two": {
                                            "address": "10.11.11.10",
                                            "mask": "31",
                                            "sap": {"port": "lag-1", "vlan": "50"},
                                        },
                                        "loopback": {},
                                    }
                                ],
                                "name": "vprn2",
                                "ospf": {
                                    "admin_enabled": "True",
                                    "area": "0.0.0.0",
                                    "interfaces": [
                                        {"name": "interface-two", "passive": "True"}
                                    ],
                                },
                            },
                            "3": {
                                "admin_enabled": "True",
                                "interfaces": [
                                    {
                                        "interface-two": {
                                            "address": "10.12.12.100",
                                            "mask": "31",
                                            "sap": {"port": "lag-5", "vlan": "33"},
                                        },
                                        "loopback": {
                                            "address": "10.12.12.12",
                                            "mask": "32",
                                        },
                                    }
                                ],
                                "name": "vprn3",
                                "ospf": {
                                    "admin_enabled": "True",
                                    "area": "0.0.0.0",
                                    "interfaces": [
                                        {"name": "interface-two", "passive": "True"}
                                    ],
                                },
                            },
                            "4": {
                                "admin_enabled": "True",
                                "interfaces": [
                                    {
                                        "interface-two": {
                                            "address": "10.40.40.100",
                                            "ipv6": {
                                                "address": "1500:1000:460e::2222:1111",
                                                "mask": "64",
                                            },
                                            "mask": "31",
                                            "sap": {"port": "lag-5", "vlan": "800"},
                                        },
                                        "loopback": {
                                            "address": "10.40.40.10",
                                            "ipv6": {
                                                "address": "1500:1000:460e::a03:ae46",
                                                "mask": "128",
                                            },
                                            "mask": "32",
                                        },
                                    }
                                ],
                                "name": "ospf_version3_vprn",
                                "ospf": {
                                    "admin_enabled": "True",
                                    "area": "0.0.0.0",
                                    "interfaces": [
                                        {"name": "interface-two", "passive": "True"}
                                    ],
                                },
                                "ospf3": {
                                    "admin_enabled": "True",
                                    "area": "0.0.0.0",
                                    "interfaces": [
                                        {"name": "interface-two", "passive": "True"}
                                    ],
                                },
                            },
                            "5": {
                                "admin_enabled": "True",
                                "bgp": {
                                    "admin_enabled": "True",
                                    "peergroups": [
                                        {
                                            "name": "eBGP",
                                            "neighbors": [{"address": "10.50.50.201"}],
                                            "remote_as": "4444",
                                        }
                                    ],
                                },
                                "interfaces": [
                                    {
                                        "bgp-interface": {
                                            "address": "10.50.50.200",
                                            "mask": "31",
                                            "sap": {"port": "lag-1", "vlan": "602"},
                                        },
                                        "interface-two": {
                                            "address": "10.50.50.100",
                                            "mask": "31",
                                            "sap": {"port": "lag-5", "vlan": "5"},
                                        },
                                        "loopback": {
                                            "address": "10.50.50.50",
                                            "mask": "32",
                                        },
                                    }
                                ],
                                "name": "vprn5",
                                "ospf": {
                                    "area": "0.0.0.0",
                                    "interfaces": [
                                        {"name": "interface-two", "passive": "True"}
                                    ],
                                },
                            },
                        }
                    ]
                }
            }
        ]
    ]


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
    assert res == [
        [
            {
                "system_level": {
                    "HOSTNAME": "LAB-MX-1",
                    "TZ": "some/time",
                    "default_address_selection": True,
                    "no_ping_record_route": True,
                    "no_ping_time_stamp": True,
                    "no_redirects": True,
                    "services": {
                        "netconf": {
                            "ssh": {"connection-limit": "10", "rate-limit": "4"}
                        },
                        "ssh": {
                            "client-alive-count-max": "3",
                            "client-alive-interval": "10",
                            "connection-limit": "10",
                            "max-sessions": "32",
                            "no-tcp-fwding": True,
                            "rate-limit": "5",
                            "root-login": False,
                            "ssh-proto": "v2",
                        },
                    },
                    "tacacs": {
                        "tacacs-servers": {
                            "1.1.1.1": {
                                "tac_port": "49",
                                "tac_secret": "<SECRET_HASH>",
                                "tac_source": "5.5.5.5",
                            },
                            "2.2.2.2": {
                                "tac_port": "49",
                                "tac_secret": "<SECRET_HASH>",
                                "tac_source": "5.5.5.5",
                            },
                            "4.4.4.4": {
                                "tac_port": "49",
                                "tac_secret": "<SECRET_HASH>",
                                "tac_source": "5.5.5.5",
                            },
                        }
                    },
                }
            }
        ]
    ]


# test_issue_45_for_junos_cfg()


def test_faq_multiline_output_matching():
    data = """
Local Intf: Te2/1/23
System Name: r1.lab.local

System Description: 
Cisco IOS Software, Catalyst 1234 L3 Switch Software (cat1234e-ENTSERVICESK9-M), Version 1534.1(1)SG, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2012 by Cisco Systems, Inc.
Compiled Sun 15-Apr-12 02:35 by p

Time remaining: 92 seconds    
    """
    template = """
<group>
Local Intf: {{ local_intf }}
System Name: {{ peer_name }}

<group name="peer_system_description">
System Description: {{ _start_ }}
{{ sys_description | _line_ | joinmatches(" ") }}
Time remaining: {{ ignore }} seconds {{ _end_ }}
</group>

</group>
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=100)
    assert res == [
        [
            [
                {
                    "local_intf": "Te2/1/23",
                    "peer_name": "r1.lab.local",
                    "peer_system_description": {
                        "sys_description": "Cisco IOS Software, Catalyst 1234 L3 Switch "
                        "Software (cat1234e-ENTSERVICESK9-M), Version "
                        "1534.1(1)SG, RELEASE SOFTWARE (fc3) Technical "
                        "Support: http://www.cisco.com/techsupport "
                        "Copyright (c) 1986-2012 by Cisco Systems, Inc. "
                        "Compiled Sun 15-Apr-12 02:35 by p"
                    },
                }
            ]
        ]
    ]


# test_faq_multiline_output_matching()


def test_issue_52_answer():
    data = """
Origin:
Some random name
Example Address, example number, example city

Origin:
Some random name 2
Example Address, example number, example city 2

Origin:
Some random name 3
Example Address, example number, example city 3
One more string
    """
    template = """
<macro>
def process(data):
    lines = data["match"].splitlines()
    name = lines[0]
    address = lines[1]
    return {"name": name, "address": address}
</macro>

<group name="origin*" macro="process">
Origin: {{ _start_ }}
{{ match | _line_ | joinmatches }}
</group>
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=100)
    assert res == [
        [
            {
                "origin": [
                    {
                        "address": "Example Address, example number, example city",
                        "name": "Some random name",
                    },
                    {
                        "address": "Example Address, example number, example city 2",
                        "name": "Some random name 2",
                    },
                    {
                        "address": "Example Address, example number, example city 3",
                        "name": "Some random name 3",
                    },
                ]
            }
        ]
    ]


# test_issue_52_answer()


def test_issue_51_answer():
    """ test workaround for removing <> chars from input data """
    data = """
Name:Jane<br>
Name:Michael<br>
Name:July<br>
    """
    template = """
<group name="people">
Name:{{ name }}&lt;br&gt;
</group>
    """

    # this works as well
    # template = "Name:{{ name }}br"
    # data = data.replace("<", "").replace(">", "")

    # this did not work. fails with xml parsing error
    # template = "Name:{{ name }}&lt;br&gt;"
    # data = data.replace("<", "&lt;").replace(">", "&gt;")

    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=100)
    assert res == [
        [{"people": [{"name": "Jane"}, {"name": "Michael"}, {"name": "July"}]}]
    ]


# test_issue_51_answer()


def test_issue_50():
    template = """
<input load="text">

        interface "BNG-RH201-CORE"
            address 11.11.11.11/31
            description "BNG-RH201-CORE"
            ldp-sync-timer 10
            port lag-107:709
            ipv6
                address 1111:0:1111:1111::1/64
            exit
            bfd 150 receive 150 multiplier 3
            no shutdown
        exit
        interface "BNG-RH202-CORE"
            address 22.22.22.22/31
            description "BNG-RH201-CORE"
            ldp-sync-timer 10
            port lag-108:809
            ipv6
                address 2222:0:2222:2222::2/64
            exit
            bfd 150 receive 150 multiplier 3
            no shutdown
        exit
        interface "system"
            address 33.33.33.33/32
            ipv6
                address 3333:0:3333:3333::3/128
            exit
            no shutdown
        exit

        ies 97 name "OTDR-MGT" customer 1 create
            description "OTDR-MGT"
            interface "OTDR-MGT" create
                address 44.44.44.44/25
                vrrp 97
                    backup 10.20.30.1
                    priority 200
                exit
                vpls "OTDR-MGT-VPLS"
                exit
            exit
            no shutdown
        exit

        ies 99 name "OLT-MGT" customer 1 create
            description "OLT-INBAND-MGT"
            interface "OLT-MGT" create
                address 55.55.55.55/25
                vrrp 1
                    backup 10.20.40.1
                    priority 200
                exit
                vpls "OLT-MGT-VPLS"
                exit
            exit
            no shutdown
        exit
        ies 100 name "100" customer 1 create
            description "IES 100 for subscribers"
            redundant-interface "shunt" create
                address 66.66.66.66/31
                spoke-sdp 1:100 create
                    no shutdown
                exit
            exit
            subscriber-interface "s100" create
                description " Subscriber interface for subscribers"
                allow-unmatching-subnets
                address 77.77.77.77/22 gw-ip-address 77.77.77.1
                address 88.88.88.88/20 gw-ip-address 88.88.88.1
                group-interface "s100-lag210-vlan101" create
                    tos-marking-state trusted
                    ipv6
                        router-advertisements
                            managed-configuration
                            no shutdown
                        exit
                        dhcp6
                            proxy-server
                                no shutdown
                            exit
                        exit
                    exit
                exit
            exit
</input>


<group name="ifaces.{{ name }}" contains="ipv4,ipv6">
## group to match top level interfaces
        interface "{{ name }}"
            description {{ description | re(".+") | strip('"') }}
            address  {{ ipv4 | joinmatches('; ') }}
                address {{ ipv6 | contains(":") | joinmatches('; ') }}
        exit {{ _end_ }}
</group>

<group name="ifaces.{{ name }}" contains="ipv4,ipv6">
## group to match lower level interfaces
            interface "{{ name | _start_ }}" create
            {{ iftype }}-interface "{{ name | _start_ }}" create
                description {{ description | re(".+") | strip('"') | strip }}
                address {{ ipv4 | contains(".") | joinmatches('; ') }}
                address {{ ipv4 | contains(".") | joinmatches('; ') }} gw-ip-address {{ ignore }}
            exit {{ _end_ }}
</group>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "ifaces": {
                    "BNG-RH201-CORE": {
                        "description": "BNG-RH201-CORE",
                        "ipv4": "11.11.11.11/31",
                        "ipv6": "1111:0:1111:1111::1/64",
                    },
                    "BNG-RH202-CORE": {
                        "description": "BNG-RH201-CORE",
                        "ipv4": "22.22.22.22/31",
                        "ipv6": "2222:0:2222:2222::2/64",
                    },
                    "OLT-MGT": {"ipv4": "55.55.55.55/25"},
                    "OTDR-MGT": {"ipv4": "44.44.44.44/25"},
                    "s100": {
                        "description": "Subscriber interface for subscribers",
                        "iftype": "subscriber",
                        "ipv4": "77.77.77.77/22; 88.88.88.88/20",
                    },
                    "shunt": {"iftype": "redundant", "ipv4": "66.66.66.66/31"},
                    "system": {
                        "ipv4": "33.33.33.33/32",
                        "ipv6": "3333:0:3333:3333::3/128",
                    },
                }
            }
        ]
    ]


# test_issue_50()


def test_start_with_set():
    data = """
authentication { 
inactive: authentication { 
    """
    template = """
authentication { {{ inactive | set(False) | _start_ }}
inactive: authentication { {{ inactive | set(True) | _start_ }}
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{"inactive": False}, {"inactive": True}]]]


# test_start_with_set()


def test_ios_bgp_pers_pars():
    template = """
<vars>
defaults_bgp_peers = {
 "description": "",
 "remote-as": "",
 "shutdown": "no",
 "inherit_peer-session": "",
 "update-source": "",
 "password": ""
}
</vars>

<group name="bgp_peers">
<group name="{{ ASN }}">
router bgp {{ ASN }}
 <group name="{{ PeerIP }}" default="defaults_bgp_peers">
 neighbor {{ PeerIP }} remote-as {{ remote-as }}
 neighbor {{ PeerIP }} description {{ description | ORPHRASE }}
 neighbor {{ PeerIP | let("shutdown", "yes") }} shutdown
 neighbor {{ PeerIP }} inherit peer-session {{ inherit_peer-session }}
 neighbor {{ PeerIP }} password {{ password | ORPHRASE }}
 neighbor {{ PeerIP }} update-source {{ update-source }}
 </group>
 </group>
</group>
    """
    data = """
router bgp 65100
 neighbor 1.1.1.1 remote-as 1234
 neighbor 1.1.1.1 description Some Description here
 neighbor 1.1.1.1 shutdown
 neighbor 1.1.1.1 inherit peer-session session_1
 neighbor 1.1.1.1 password 12345678
 neighbor 1.1.1.1 update-source Loopback 1
 neighbor 1.1.1.2 remote-as 1234
 neighbor 1.1.1.2 inherit peer-session session_1
 neighbor 1.1.1.2 update-source Loopback 1
    """
    parser = ttp(data, template, log_level="DEBUG")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "bgp_peers": {
                    "65100": {
                        "1.1.1.1": {
                            "description": "Some Description here",
                            "inherit_peer-session": "session_1",
                            "password": "12345678",
                            "remote-as": "1234",
                            "shutdown": "yes",
                            "update-source": "",
                        },
                        "1.1.1.2": {
                            "description": "",
                            "inherit_peer-session": "session_1",
                            "password": "",
                            "remote-as": "1234",
                            "shutdown": "no",
                            "update-source": "",
                        },
                    }
                }
            }
        ]
    ]


# test_ios_bgp_pers_pars()


def test_ip_address_parsing():
    data = """
interface Vlan99
 description vlan99_interface
 ip address 20.99.10.1 255.255.255.0 secondary
 ip address 30.99.10.1 255.255.255.0 secondary
 ip address 10.99.10.1 255.255.255.0
 load-interval 60
 bandwidth 10000000
!
interface Vlan100
 description vlan100_interface
 ip address 10.100.10.1 255.255.255.0
 load-interval 60
 bandwidth 10000000
!
    """
    template = """
<group name="interface">
interface {{ interface }}
 description {{ description }}
 ip address {{ ipv4_addr | PHRASE | exclude("secondary") | to_ip | with_prefixlen  }}
 load-interval {{ load-interval }}
 bandwidth {{ bandwidth }}
 <group name="ipv4_secondary*">
 ip address {{ ipv4_addr | PHRASE | let("is_secondary", True) | to_ip | with_prefixlen }} secondary
 </group>
</group>
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "interface": [
                    {
                        "bandwidth": "10000000",
                        "description": "vlan99_interface",
                        "interface": "Vlan99",
                        "ipv4_addr": "10.99.10.1/24",
                        "ipv4_secondary": [
                            {"ipv4_addr": "20.99.10.1/24", "is_secondary": True},
                            {"ipv4_addr": "30.99.10.1/24", "is_secondary": True},
                        ],
                        "load-interval": "60",
                    },
                    {
                        "bandwidth": "10000000",
                        "description": "vlan100_interface",
                        "interface": "Vlan100",
                        "ipv4_addr": "10.100.10.1/24",
                        "load-interval": "60",
                    },
                ]
            }
        ]
    ]


# test_ip_address_parsing()


def test_vlans_parsing():
    template = """
            <group name="ports_summary*">
            {{ port }}  {{ mode }}  {{ encap }}  {{ satus }}  {{ native_vlan | DIGIT }}
            </group>

            <group name="vlans_allowed">
            Port      Vlans allowed on trunk {{ _start_ }}
            <group name="interfaces*">
            {{ port }}    {{ vlans | unrange('-', ',') | split(",") }}
            </group>
{{ _end_ }}
            </group>

            <group name="vlans_active">
            Port      Vlans allowed and active in management domain {{ _start_ }}
            <group name="interfaces*">
            {{ port }}    {{ vlans | unrange('-', ',') | split(",") }}
            </group>
{{ _end_ }}
            </group>

            <group name="vlans_forwarding">
            Port      Vlans in spanning tree forwarding state and not pruned {{ _start_ }}
            <group name="interfaces*">
            {{ port }}    {{ vlans | unrange('-', ',') | split(",") }}
            </group>
{{ _end_ }}
            </group>
    """
    data = """
            Port      Mode         Encapsulation  Status        Native vlan
            Gi0       on           802.1q         trunking      1
            Gi7       on           802.1q         trunking      1

            Port      Vlans allowed on trunk
            Gi0       1,8,999,1002-1005
            Gi7       1,100,120,1000,1002-1005

            Port      Vlans allowed and active in management domain
            Gi0       1,8,999
            Gi7       1,100,120,1000

            Port      Vlans in spanning tree forwarding state and not pruned
            Gi0       1,8,999
            Gi7       1,100,120,1000
    """
    parser = ttp(data, template, log_level="DEBUG")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=120)
    assert res == [
        [
            {
                "ports_summary": [
                    {
                        "encap": "802.1q",
                        "mode": "on",
                        "native_vlan": "1",
                        "port": "Gi0",
                        "satus": "trunking",
                    },
                    {
                        "encap": "802.1q",
                        "mode": "on",
                        "native_vlan": "1",
                        "port": "Gi7",
                        "satus": "trunking",
                    },
                ],
                "vlans_active": {
                    "interfaces": [
                        {"port": "Gi0", "vlans": ["1", "8", "999"]},
                        {"port": "Gi7", "vlans": ["1", "100", "120", "1000"]},
                    ]
                },
                "vlans_allowed": {
                    "interfaces": [
                        {
                            "port": "Gi0",
                            "vlans": ["1", "8", "999", "1002", "1003", "1004", "1005"],
                        },
                        {
                            "port": "Gi7",
                            "vlans": [
                                "1",
                                "100",
                                "120",
                                "1000",
                                "1002",
                                "1003",
                                "1004",
                                "1005",
                            ],
                        },
                    ]
                },
                "vlans_forwarding": {
                    "interfaces": [
                        {"port": "Gi0", "vlans": ["1", "8", "999"]},
                        {"port": "Gi7", "vlans": ["1", "100", "120", "1000"]},
                    ]
                },
            }
        ]
    ]


# test_vlans_parsing()


def test_asa_acls_issue_55_uses_itemize_with_dynamic_path():
    data = """
object-group service gokuhead
 service-object tcp-udp destination eq gokurpc 
 service-object tcp destination eq 902 
 service-object tcp destination eq https 
 service-object tcp destination eq nfs 
 service-object tcp destination eq 10025 
object-group network gohan
 network-object object gohan-01
 network-object object gohan-02
 network-object object vlan_944
 network-object object gohan-03
 network-object object gohan-05
 network-object object gohan-06
object-group service sql tcp
 port-object eq 1433
object-group network vegeta
 group-object trunks
 network-object object vegeta-01
object-group network Space-Users
 network-object object ab
 network-object object ac
 network-object object ad
 network-object object ae
 network-object object af
 network-object object ag
 network-object object ah
 network-object object ai
 network-object object aj
object-group network dalmatians
 network-object object dog-01
 group-object trunks
 network-object object vlan_950
 group-object Space-Users
 network-object object Darts-Summary            
    """
    template = """
<vars>
SVC_PORTS = "tcp-udp|tcp|udp"
</vars>

<group name="object-{{ object_type }}-groups**.{{ object_name }}**">
object-group {{ object_type }} {{ object_name | _start_ }}
object-group {{ object_type }} {{ object_name | _start_ }} {{ protocol | re("SVC_PORTS")}}
 description {{ description | re(".*") }}

 <group name="{{ type }}-objects" itemize="obj_name" method="table">
 network-object object   {{ obj_name | let("type", "network") }}
 network-object host     {{ obj_name | IP | let("type", "network") }}
 group-object            {{ obj_name | let("type", "group") }}
 service-object object   {{ obj_name | let("type", "service") }}
 service-object          {{ obj_name | let("type", "service") }}
 </group>

 <group name="service-object-ports*">
 service-object {{ protocol | re("SVC_PORTS") }} destination eq {{port}}
 </group>
 
 <group name="service-object-port-ranges*">
 service-object {{ protocol | re("SVC_PORTS") }} destination range {{port_begin}} {{port_end}}
 </group>

 <group name="service-port-objects" itemize="port_obj">
 port-object eq {{ port_obj }}
 </group>
 
</group>
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=80)
    assert res == [
        [
            {
                "object-network-groups": {
                    "Space-Users": {
                        "network-objects": [
                            "ab",
                            "ac",
                            "ad",
                            "ae",
                            "af",
                            "ag",
                            "ah",
                            "ai",
                            "aj",
                        ]
                    },
                    "dalmatians": {
                        "group-objects": ["trunks", "Space-Users"],
                        "network-objects": ["dog-01", "vlan_950", "Darts-Summary"],
                    },
                    "gohan": {
                        "network-objects": [
                            "gohan-01",
                            "gohan-02",
                            "vlan_944",
                            "gohan-03",
                            "gohan-05",
                            "gohan-06",
                        ]
                    },
                    "vegeta": {
                        "group-objects": ["trunks"],
                        "network-objects": ["vegeta-01"],
                    },
                },
                "object-service-groups": {
                    "gokuhead": {
                        "service-object-ports": [
                            {"port": "gokurpc", "protocol": "tcp-udp"},
                            {"port": "902", "protocol": "tcp"},
                            {"port": "https", "protocol": "tcp"},
                            {"port": "nfs", "protocol": "tcp"},
                            {"port": "10025", "protocol": "tcp"},
                        ]
                    },
                    "sql": {"protocol": "tcp", "service-port-objects": ["1433"]},
                },
            }
        ]
    ]


# test_asa_acls_issue_55()


def test_asa_acls_issue_55():
    data = """
object-group service gokuhead
 service-object tcp-udp destination eq gokurpc 
 service-object tcp destination eq 902 
 service-object tcp destination eq https 
 service-object tcp destination eq nfs 
 service-object tcp destination eq 10025 
object-group network gohan
 network-object object gohan-01
 network-object object gohan-02
 network-object object vlan_944
 network-object object gohan-03
 network-object object gohan-05
 network-object object gohan-06
object-group service sql tcp
 port-object eq 1433
object-group network vegeta
 group-object trunks
 network-object object vegeta-01
object-group network Space-Users
 network-object object ab
 network-object object ac
 network-object object ad
 network-object object ae
 network-object object af
 network-object object ag
 network-object object ah
 network-object object ai
 network-object object aj
object-group network dalmatians
 network-object object dog-01
 group-object trunks
 network-object object vlan_950
 group-object Space-Users
 network-object object Darts-Summary            
    """
    template = """
<vars>
SVC_PORTS = "tcp-udp|tcp|udp"
</vars>

<group name="object-{{ object_type }}-groups**.{{ object_name }}**">
object-group {{ object_type }} {{ object_name | _start_ }}
object-group {{ object_type }} {{ object_name | _start_ }} {{ protocol | re("SVC_PORTS")}}
 description {{ description | re(".*") }}

 <group name="network-objects" itemize="obj_name" method="table">
 network-object object   {{ obj_name | }}
 network-object host     {{ obj_name | IP }}
 </group> 

 <group name="group-objects" itemize="obj_name" method="table">
 group-object            {{ obj_name }}
 </group>
 
 <group name="group-objects" itemize="obj_name" method="table">
 service-object object   {{ obj_name }}
 service-object          {{ obj_name }}
 </group>

 <group name="service-object-ports*">
 service-object {{ protocol | re("SVC_PORTS") }} destination eq {{port}}
 </group>
 
 <group name="service-object-port-ranges*">
 service-object {{ protocol | re("SVC_PORTS") }} destination range {{port_begin}} {{port_end}}
 </group>

 <group name="service-port-objects" itemize="port_obj">
 port-object eq {{ port_obj }}
 </group>
 
</group>
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=80)
    assert res == [
        [
            {
                "object-network-groups": {
                    "Space-Users": {
                        "network-objects": [
                            "ab",
                            "ac",
                            "ad",
                            "ae",
                            "af",
                            "ag",
                            "ah",
                            "ai",
                            "aj",
                        ]
                    },
                    "dalmatians": {
                        "group-objects": ["trunks", "Space-Users"],
                        "network-objects": ["dog-01", "vlan_950", "Darts-Summary"],
                    },
                    "gohan": {
                        "network-objects": [
                            "gohan-01",
                            "gohan-02",
                            "vlan_944",
                            "gohan-03",
                            "gohan-05",
                            "gohan-06",
                        ]
                    },
                    "vegeta": {
                        "group-objects": ["trunks"],
                        "network-objects": ["vegeta-01"],
                    },
                },
                "object-service-groups": {
                    "gokuhead": {
                        "service-object-ports": [
                            {"port": "gokurpc", "protocol": "tcp-udp"},
                            {"port": "902", "protocol": "tcp"},
                            {"port": "https", "protocol": "tcp"},
                            {"port": "nfs", "protocol": "tcp"},
                            {"port": "10025", "protocol": "tcp"},
                        ]
                    },
                    "sql": {"protocol": "tcp", "service-port-objects": ["1433"]},
                },
            }
        ]
    ]


# test_asa_acls_issue_55()


def test_issue_57_headers_parsing():
    """
    Issue first was with startempty match not beeing selected in favour
    of start match produced by headers :
    Interface            Link Protocol Primary_IP      Description {{ _headers_ }}

    that was fixed by adding this code to the TTP selection logic for multiple
    matches:
                    # startempty RE always more preferred
                    if startempty_re:
                        for index in startempty_re:
                            re_ = result[index][0]
                            result_data = result[index][1]
                            # skip results that did not pass validation check
                            if result_data == False:
                                continue
                            # prefer result with same path as current record
                            elif re_["GROUP"].group_id == self.record["GRP_ID"]:
                                break
                            # prefer children of current record group
                            elif self.record["GRP_ID"] and re_["GROUP"].group_id[
                                0
                            ].startswith(self.record["GRP_ID"][0]):
                                break
                    # start RE preferred next
                    elif start_re:

    Another problem was with
    Interface            Link Protocol Primary_IP      Description {{ _headers_ }}

    matching on "Duplex: (a)/A - auto; H - half; F - full" line, that was fixed
    by chaning _end_ logic by introducing self.ended_groups set to _results_class
    and replacing self.GRPLOCL with logic to use self.ended_groups instead.

    All in all it resulted in better _end_ handling behavior and allowed to fix issue
    45 as well where before this one had to use filtering instead, but now _end_ also
    helps.
    """
    data = """
Brief information on interfaces in route mode:
Link: ADM - administratively down; Stby - standby
Protocol: (s) - spoofing
Interface            Link Protocol Primary IP      Description                
InLoop0              UP   UP(s)    --                                         
REG0                 UP   --       --                                         
Vlan401              UP   UP       10.251.147.36       HSSBC_to_inband_mgmt_r4

Brief information on interfaces in bridge mode:
Link: ADM - administratively down; Stby - standby
Speed: (a) - auto
Duplex: (a)/A - auto; H - half; F - full
Type: A - access; T - trunk; H - hybrid
Interface            Link Speed   Duplex Type PVID Description                
BAGG1                UP   20G(a)  F(a)   T    1            to-KDC-R4.10-Core-1
BAGG14               UP   10G(a)  F(a)   T    1    KDC-R429-E1 BackUp Chassis 
BAGG22               UP   20G(a)  F(a)   T    1                    HSSBC-NS-01
FGE1/0/49            DOWN auto    A      A    1                               
XGE1/0/1             UP   10G(a)  F(a)   T    1    KDC-R402-E1 Backup Chassis 

    """
    template = """
<group name = "interfaces">
<group name="routed">
Brief information on interfaces in route mode: {{ _start_ }}
<group name = "{{Interface}}">
Interface            Link Protocol Primary_IP      Description {{ _headers_ }}
</group>
{{ _end_ }}
</group>

<group name="bridged">
Brief information on interfaces in bridge mode: {{ _start_ }}
<group name = "{{Interface}}">
Interface            Link Speed   Duplex Type PVID Description {{ _headers_ }}
</group>
{{ _end_ }}
</group>
</group>
    """
    parser = ttp(data, template, log_level="error")
    parser.parse()
    res = parser.result()
    pprint.pprint(res, width=80)
    assert res == [
        [
            {
                "interfaces": {
                    "bridged": {
                        "BAGG1": {
                            "Description": "to-KDC-R4.10-Core-1",
                            "Duplex": "F(a)",
                            "Link": "UP",
                            "PVID": "1",
                            "Speed": "20G(a)",
                            "Type": "T",
                        },
                        "BAGG14": {
                            "Description": "KDC-R429-E1 BackUp " "Chassis",
                            "Duplex": "F(a)",
                            "Link": "UP",
                            "PVID": "1",
                            "Speed": "10G(a)",
                            "Type": "T",
                        },
                        "BAGG22": {
                            "Description": "HSSBC-NS-01",
                            "Duplex": "F(a)",
                            "Link": "UP",
                            "PVID": "1",
                            "Speed": "20G(a)",
                            "Type": "T",
                        },
                        "FGE1/0/49": {
                            "Description": "",
                            "Duplex": "A",
                            "Link": "DOWN",
                            "PVID": "1",
                            "Speed": "auto",
                            "Type": "A",
                        },
                        "Link: ADM - administr": {
                            "Description": "",
                            "Duplex": "Stby -",
                            "Link": "ative",
                            "PVID": "dby",
                            "Speed": "ly down;",
                            "Type": "stan",
                        },
                        "XGE1/0/1": {
                            "Description": "KDC-R402-E1 Backup " "Chassis",
                            "Duplex": "F(a)",
                            "Link": "UP",
                            "PVID": "1",
                            "Speed": "10G(a)",
                            "Type": "T",
                        },
                    },
                    "routed": {
                        "InLoop0": {
                            "Description": "",
                            "Link": "UP",
                            "Primary_IP": "--",
                            "Protocol": "UP(s)",
                        },
                        "Link: ADM - administr": {
                            "Description": "",
                            "Link": "ative",
                            "Primary_IP": "Stby - " "standby",
                            "Protocol": "ly down;",
                        },
                        "REG0": {
                            "Description": "",
                            "Link": "UP",
                            "Primary_IP": "--",
                            "Protocol": "--",
                        },
                        "Vlan401": {
                            "Description": "HSSBC_to_inband_mgmt_r4",
                            "Link": "UP",
                            "Primary_IP": "10.251.147.36",
                            "Protocol": "UP",
                        },
                    },
                }
            }
        ]
    ]


# test_issue_57_headers_parsing()


def test_issue_57_headers_parsing_using_columns():
    """
    Added columns for headers, now can adjust headers size as required
    to filter unwanted results
    """
    data = """
Brief information on interfaces in route mode:
Link: ADM - administratively down; Stby - standby
Protocol: (s) - spoofing
Interface            Link Protocol Primary IP      Description                
InLoop0              UP   UP(s)    --                                         
REG0                 UP   --       --                                         
Vlan401              UP   UP       10.251.147.36       HSSBC_to_inband_mgmt_r4

Brief information on interfaces in bridge mode:
Link: ADM - administratively down; Stby - standby
Speed: (a) - auto
Duplex: (a)/A - auto; H - half; F - full
Type: A - access; T - trunk; H - hybrid
Interface            Link Speed   Duplex Type PVID Description                
BAGG1                UP   20G(a)  F(a)   T    1            to-KDC-R4.10-Core-1
BAGG14               UP   10G(a)  F(a)   T    1    KDC-R429-E1 BackUp Chassis 
BAGG22               UP   20G(a)  F(a)   T    1                    HSSBC-NS-01
FGE1/0/49            DOWN auto    A      A    1                               
XGE1/0/1             UP   10G(a)  F(a)   T    1    KDC-R402-E1 Backup Chassis 

    """
    template = """
<group name = "interfaces">
<group name="routed">
Brief information on interfaces in route mode: {{ _start_ }}
<group name = "{{Interface}}">
Interface            Link Protocol Primary_IP      Description {{ _headers_ | columns(5)}}
</group>
{{ _end_ }}
</group>

<group name="bridged">
Brief information on interfaces in bridge mode: {{ _start_ }}
<group name = "{{Interface}}">
Interface            Link Speed   Duplex Type PVID Description {{ _headers_ | columns(7) }}
</group>
{{ _end_ }}
</group>
</group>
    """
    parser = ttp(data, template, log_level="error")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=80)
    assert res == [
        [
            {
                "interfaces": {
                    "bridged": {
                        "BAGG1": {
                            "Description": "to-KDC-R4.10-Core-1",
                            "Duplex": "F(a)",
                            "Link": "UP",
                            "PVID": "1",
                            "Speed": "20G(a)",
                            "Type": "T",
                        },
                        "BAGG14": {
                            "Description": "KDC-R429-E1 BackUp " "Chassis",
                            "Duplex": "F(a)",
                            "Link": "UP",
                            "PVID": "1",
                            "Speed": "10G(a)",
                            "Type": "T",
                        },
                        "BAGG22": {
                            "Description": "HSSBC-NS-01",
                            "Duplex": "F(a)",
                            "Link": "UP",
                            "PVID": "1",
                            "Speed": "20G(a)",
                            "Type": "T",
                        },
                        "FGE1/0/49": {
                            "Description": "",
                            "Duplex": "A",
                            "Link": "DOWN",
                            "PVID": "1",
                            "Speed": "auto",
                            "Type": "A",
                        },
                        "XGE1/0/1": {
                            "Description": "KDC-R402-E1 Backup " "Chassis",
                            "Duplex": "F(a)",
                            "Link": "UP",
                            "PVID": "1",
                            "Speed": "10G(a)",
                            "Type": "T",
                        },
                    },
                    "routed": {
                        "InLoop0": {
                            "Description": "",
                            "Link": "UP",
                            "Primary_IP": "--",
                            "Protocol": "UP(s)",
                        },
                        "REG0": {
                            "Description": "",
                            "Link": "UP",
                            "Primary_IP": "--",
                            "Protocol": "--",
                        },
                        "Vlan401": {
                            "Description": "HSSBC_to_inband_mgmt_r4",
                            "Link": "UP",
                            "Primary_IP": "10.251.147.36",
                            "Protocol": "UP",
                        },
                    },
                }
            }
        ]
    ]


# test_issue_57_headers_parsing_using_columns()


def test_interface_template_not_collecting_all_data_solution():
    data = """
interface Bundle-Ether10
 description Bundle-Ether10
 bfd mode ietf
 bfd address-family ipv4 multiplier 3
 bfd address-family ipv4 destination 192.168.1.7
 bfd address-family ipv4 fast-detect
 bfd address-family ipv4 minimum-interval 100
 mtu 9114
 ipv4 address 192.168.1.6 255.255.255.254
 ipv6 address fc00::1:5/127
 load-interval 30
!
interface Bundle-Ether51
 description Bundle-Ether51
 bfd mode ietf
 bfd address-family ipv4 multiplier 3
 bfd address-family ipv4 destination 192.168.1.2
 bfd address-family ipv4 fast-detect
 bfd address-family ipv4 minimum-interval 100
 mtu 9114
 ipv4 address 192.168.1.3 255.255.255.254
 ipv6 address fc00::1:3/127
 load-interval 30
!
interface Loopback0
 description Loopback0
 ipv4 address 10.1.1.1 255.255.255.255
 ipv4 address 10.2.2.2 255.255.255.255 secondary
 ipv6 address fc00::1/128
 ipv6 address fc00::101/128
!
interface Loopback1
 description Loopback1
 ipv4 address 10.100.0.1 255.255.255.0
 ipv4 address 10.100.1.1 255.255.255.0 secondary
 ipv4 address 10.100.2.1 255.255.255.0 secondary
 ipv6 address fc00:100::1/64
 ipv6 address fc00:100::101/64
 ipv6 address fc00:100::201/64
!
interface MgmtEth0/RP0/CPU0/0
 description MgmtEth0/RP0/CPU0/0
 cdp
 vrf VRF-MGMT
 ipv4 address 172.23.136.21 255.255.252.0
!
interface GigabitEthernet0/0/0/12
 description GigabitEthernet0/0/0/12
 mtu 9018
 lldp
  receive disable
  transmit disable
 !
 negotiation auto
 load-interval 30
 l2transport
 !
!
interface TenGigE0/0/0/4
 description TenGigE0/0/0/4
 bundle id 51 mode active
 cdp
 load-interval 30
!
interface TenGigE0/0/0/5
 shutdown
!
interface TenGigE0/0/0/5.100 l2transport
 description TenGigE0/0/0/5.100
!
interface TenGigE0/0/0/47
 description TenGigE0/0/0/47
 shutdown
 mac-address 201.b19.1234
!
interface BVI101
 cdp
 description BVI101
 ipv4 address 192.168.101.1 255.255.255.0
 load-interval 30
 mac-address 200.b19.4321
!
interface HundredGigE0/0/1/0
 description HundredGigE0/0/1/0
 bundle id 10 mode active
 cdp
 load-interval 30
 mac-address 200.b19.5678
!
interface preconfigure GigabitEthernet0/0/0/11
 description GigabitEthernet0/0/0/11
 shutdown
!
interface preconfigure GigabitEthernet0/0/0/16
 description GigabitEthernet0/0/0/16
 shutdown
!
interface preconfigure GigabitEthernet0/0/0/17
 description GigabitEthernet0/0/0/17
 shutdown
!    
    """
    template_original = """
<doc>
Template for capturing interface configuration data from IOS-XR devices

Note: In order to different interface appearances, the interface block has been replicated.
      Be sure to update all blocks accordingly when adding any new values to capture.
</doc>

<vars>
intf_defaults = {
    "description": None,
    "speed": None,
    "negotiation": None,
    "disabled": False,
    "mode": None,
}
</vars>

<macro>
## parses ipv4 addresses to determine which is primary and which are secondary
## and converts dotted-quad subnet mask into cidr format
def ipv4_macro(data):
    data_list = list(data.split(" "))
    addr = str(data_list[0])
    mask = str(data_list[1])
    mask = str(sum(bin(int(x)).count('1') for x in mask.split('.')))
    ipv4 = addr+"/"+mask
    if 'secondary' in data:
        is_secondary = True
    else:
        is_secondary = False
    result = { "ipv4" : ipv4, "is_secondary" : is_secondary }
    return result
</macro>

<group name="interfaces" default="intf_defaults">
interface {{ interface | _start_}}                                            
interface {{ interface | let("mode", "l2transport") | _start_ }} l2transport      
interface preconfigure {{ interface | let("mode", "preconfigure") | _start_ }}      
 description {{ description | re(".+") }}
 speed {{ speed }}
 negotiation {{ negotiation }}
 shutdown {{ disabled | set(True) }}
 mac-address {{ mac_address }}
 <group name="ipv4*" method="table" containsall="ipv4">
 ipv4 address {{ ipv4 | PHRASE | _exact_ | macro("ipv4_macro") }}
 </group>
 <group name="ipv6*" method="table" containsall="ipv6">
 ipv6 address {{ ipv6 | ORPHRASE | _exact_ }}
 </group>
! {{ _end_ }}
</group> 
    """
    parser = ttp(data, template_original, log_level="error")
    parser.parse()
    res = parser.result()
    pprint.pprint(res, width=80)
    assert res == [
        [
            {
                "interfaces": [
                    {
                        "description": "Bundle-Ether10",
                        "disabled": False,
                        "interface": "Bundle-Ether10",
                        "ipv4": [
                            {"ipv4": {"ipv4": "192.168.1.6/31", "is_secondary": False}}
                        ],
                        "ipv6": [{"ipv6": "fc00::1:5/127"}],
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "Bundle-Ether51",
                        "disabled": False,
                        "interface": "Bundle-Ether51",
                        "ipv4": [
                            {"ipv4": {"ipv4": "192.168.1.3/31", "is_secondary": False}}
                        ],
                        "ipv6": [{"ipv6": "fc00::1:3/127"}],
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "Loopback0",
                        "disabled": False,
                        "interface": "Loopback0",
                        "ipv4": [
                            {"ipv4": {"ipv4": "10.1.1.1/32", "is_secondary": False}},
                            {"ipv4": {"ipv4": "10.2.2.2/32", "is_secondary": True}},
                        ],
                        "ipv6": [{"ipv6": "fc00::1/128"}, {"ipv6": "fc00::101/128"}],
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "Loopback1",
                        "disabled": False,
                        "interface": "Loopback1",
                        "ipv4": [
                            {"ipv4": {"ipv4": "10.100.0.1/24", "is_secondary": False}},
                            {"ipv4": {"ipv4": "10.100.1.1/24", "is_secondary": True}},
                            {"ipv4": {"ipv4": "10.100.2.1/24", "is_secondary": True}},
                        ],
                        "ipv6": [
                            {"ipv6": "fc00:100::1/64"},
                            {"ipv6": "fc00:100::101/64"},
                            {"ipv6": "fc00:100::201/64"},
                        ],
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "MgmtEth0/RP0/CPU0/0",
                        "disabled": False,
                        "interface": "MgmtEth0/RP0/CPU0/0",
                        "ipv4": [
                            {
                                "ipv4": {
                                    "ipv4": "172.23.136.21/22",
                                    "is_secondary": False,
                                }
                            }
                        ],
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "GigabitEthernet0/0/0/12",
                        "disabled": False,
                        "interface": "GigabitEthernet0/0/0/12",
                        "mode": None,
                        "negotiation": "auto",
                        "speed": None,
                    },
                    {
                        "description": "TenGigE0/0/0/4",
                        "disabled": False,
                        "interface": "TenGigE0/0/0/4",
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": None,
                        "disabled": True,
                        "interface": "TenGigE0/0/0/5",
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "TenGigE0/0/0/5.100",
                        "disabled": False,
                        "interface": "TenGigE0/0/0/5.100",
                        "mode": "l2transport",
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "TenGigE0/0/0/47",
                        "disabled": True,
                        "interface": "TenGigE0/0/0/47",
                        "mac_address": "201.b19.1234",
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "BVI101",
                        "disabled": False,
                        "interface": "BVI101",
                        "ipv4": [
                            {
                                "ipv4": {
                                    "ipv4": "192.168.101.1/24",
                                    "is_secondary": False,
                                }
                            }
                        ],
                        "mac_address": "200.b19.4321",
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "HundredGigE0/0/1/0",
                        "disabled": False,
                        "interface": "HundredGigE0/0/1/0",
                        "mac_address": "200.b19.5678",
                        "mode": None,
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "GigabitEthernet0/0/0/11",
                        "disabled": True,
                        "interface": "GigabitEthernet0/0/0/11",
                        "mode": "preconfigure",
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "GigabitEthernet0/0/0/16",
                        "disabled": True,
                        "interface": "GigabitEthernet0/0/0/16",
                        "mode": "preconfigure",
                        "negotiation": None,
                        "speed": None,
                    },
                    {
                        "description": "GigabitEthernet0/0/0/17",
                        "disabled": True,
                        "interface": "GigabitEthernet0/0/0/17",
                        "mode": "preconfigure",
                        "negotiation": None,
                        "speed": None,
                    },
                ]
            }
        ]
    ]


# test_interface_template_not_collecting_all_data_solution()


@pytest.mark.skipif(True, reason="Need to fix this one")
def test_interface_template_not_collecting_all_data():
    """
    For interface BVI101 not collecting mac-address
    """
    data = """
interface Bundle-Ether10
 description Bundle-Ether10
 bfd mode ietf
 bfd address-family ipv4 multiplier 3
 bfd address-family ipv4 destination 192.168.1.7
 bfd address-family ipv4 fast-detect
 bfd address-family ipv4 minimum-interval 100
 mtu 9114
 ipv4 address 192.168.1.6 255.255.255.254
 ipv6 address fc00::1:5/127
 load-interval 30
!
interface Bundle-Ether51
 description Bundle-Ether51
 bfd mode ietf
 bfd address-family ipv4 multiplier 3
 bfd address-family ipv4 destination 192.168.1.2
 bfd address-family ipv4 fast-detect
 bfd address-family ipv4 minimum-interval 100
 mtu 9114
 ipv4 address 192.168.1.3 255.255.255.254
 ipv6 address fc00::1:3/127
 load-interval 30
!
interface Loopback0
 description Loopback0
 ipv4 address 10.1.1.1 255.255.255.255
 ipv4 address 10.2.2.2 255.255.255.255 secondary
 ipv6 address fc00::1/128
 ipv6 address fc00::101/128
!
interface Loopback1
 description Loopback1
 ipv4 address 10.100.0.1 255.255.255.0
 ipv4 address 10.100.1.1 255.255.255.0 secondary
 ipv4 address 10.100.2.1 255.255.255.0 secondary
 ipv6 address fc00:100::1/64
 ipv6 address fc00:100::101/64
 ipv6 address fc00:100::201/64
!
interface MgmtEth0/RP0/CPU0/0
 description MgmtEth0/RP0/CPU0/0
 cdp
 vrf VRF-MGMT
 ipv4 address 172.23.136.21 255.255.252.0
!
interface GigabitEthernet0/0/0/12
 description GigabitEthernet0/0/0/12
 mtu 9018
 lldp
  receive disable
  transmit disable
 !
 negotiation auto
 load-interval 30
 l2transport
 !
!
interface TenGigE0/0/0/4
 description TenGigE0/0/0/4
 bundle id 51 mode active
 cdp
 load-interval 30
!
interface TenGigE0/0/0/5
 shutdown
!
interface TenGigE0/0/0/5.100 l2transport
 description TenGigE0/0/0/5.100
!
interface TenGigE0/0/0/47
 description TenGigE0/0/0/47
 shutdown
 mac-address 201.b19.1234
!
interface BVI101
 cdp
 description BVI101
 ipv4 address 192.168.101.1 255.255.255.0
 load-interval 30
 mac-address 200.b19.4321
!
interface HundredGigE0/0/1/0
 description HundredGigE0/0/1/0
 bundle id 10 mode active
 cdp
 load-interval 30
 mac-address 200.b19.5678
!
interface preconfigure GigabitEthernet0/0/0/11
 description GigabitEthernet0/0/0/11
 shutdown
!
interface preconfigure GigabitEthernet0/0/0/16
 description GigabitEthernet0/0/0/16
 shutdown
!
interface preconfigure GigabitEthernet0/0/0/17
 description GigabitEthernet0/0/0/17
 shutdown
!    
    """
    template_original = """
<doc>
Template for capturing interface configuration data from IOS-XR devices

Note: In order to different interface appearances, the interface block has been replicated.
      Be sure to update all blocks accordingly when adding any new values to capture.
</doc>

<macro>
## parses ipv4 addresses to determine which is primary and which are secondary
## and converts dotted-quad subnet mask into cidr format
def ipv4_macro(data):
    data_list = list(data.split(" "))
    addr = str(data_list[0])
    mask = str(data_list[1])
    mask = str(sum(bin(int(x)).count('1') for x in mask.split('.')))
    ipv4 = addr+"/"+mask
    if 'secondary' in data:
        is_secondary = True
    else:
        is_secondary = False
    result = { "ipv4" : ipv4, "is_secondary" : is_secondary }
    return result
</macro>


## parent group for all interface groups
<group name="interfaces">

## matches primary interfaces
<group>
{{ mode | set(None) }}
{{ description | set(None) }}
{{ speed | set(None) }}
{{ negotiation | set(None) }}
{{ disabled | set(False) }}
interface {{ interface }}
 description {{ description | re(".+") }}
 <group name="ipv4*" method="table" containsall="ipv4">
 ipv4 address {{ ipv4 | PHRASE | _exact_ | macro("ipv4_macro") }}
 </group>
 <group name="ipv6*" method="table" containsall="ipv6">
 ipv6 address {{ ipv6 | PHRASE | _exact_ }}
 </group>
 speed {{ speed }}
 negotiation {{ negotiation }}
 shutdown {{ disabled | set(True) }}
 mac-address {{ mac_address }}
</group>

## matches pre-configured interfaces
<group>
{{ mode | set('preconfigure') }}
{{ description | set(None) }}
{{ speed | set(None) }}
{{ negotiation | set(None) }}
{{ disabled | set(False) }}
interface preconfigure {{ interface }}
 description {{ description | re(".+") }}
 <group name="ipv4*" method="table" containsall="ipv4">
 ipv4 address {{ ipv4 | PHRASE | _exact_ | macro("ipv4_macro") }}
 </group>
 <group name="ipv6*" method="table" containsall="ipv6">
 ipv6 address {{ ipv6 | PHRASE | _exact_ }}
 </group>
 speed {{ speed }}
 negotiation {{ negotiation }}
 shutdown {{ disabled | set(True) }}
 mac-address {{ mac_address }}
</group>

## matches sub-interfaces
<group>
{{ mode | set('l2transport') }}
{{ description | set(None) }}
{{ speed | set(None) }}
{{ negotiation | set(None) }}
{{ disabled | set(False) }}
interface {{ interface }} l2transport
 description {{ description | re(".+") }}
 <group name="ipv4*" method="table" containsall="ipv4">
 ipv4 address {{ ipv4 | PHRASE | _exact_ | macro("ipv4_macro") }}
 </group>
 <group name="ipv6*" method="table" containsall="ipv6">
 ipv6 address {{ ipv6 | PHRASE | _exact_ }}
 </group>
 speed {{ speed }}
 negotiation {{ negotiation }}
 shutdown {{ disabled | set(True) }}
 mac-address {{ mac_address }}
</group>

</group>    
    """
    parser = ttp(data, template_original, log_level="error")
    parser.parse()
    res = parser.result()
    pprint.pprint(res, width=80)


# test_interface_template_not_collecting_all_data()


def test_interface_template_not_collecting_all_data_reduced():
    """
    Below template and data were producing this result:

    [[{'interfaces': [{'interface': 'TenGigE0/0/0/5.100'},
                      {'interface': 'BVI101',
                       'ipv4': [{'ipv4': '192.168.101.1 255.255.255.0'}]}]}]]

    TTP was not collecting mac-address for BVI 101
    """
    data = """
interface TenGigE0/0/0/5.100 l2transport
!
interface BVI101
 ipv4 address 192.168.101.1 255.255.255.0
 mac-address 200.b19.4321
!
    """
    template = """
<group name="interfaces">

## matches primary interfaces
<group>
interface {{ interface }}
 <group name="ipv4*" method="table" containsall="ipv4">
 ipv4 address {{ ipv4 | _line_ | _exact_ }}
 </group>
 mac-address {{ mac_address }}
</group>

## matches sub-interfaces
<group>
interface {{ interface }} l2transport
 mac-address {{ mac_address }}
</group>

</group>      
    """
    parser = ttp(data, template, log_level="error")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=80)
    assert res == [
        [
            {
                "interfaces": [
                    {"interface": "TenGigE0/0/0/5.100"},
                    {
                        "interface": "BVI101",
                        "ipv4": [{"ipv4": "192.168.101.1 255.255.255.0"}],
                        "mac_address": "200.b19.4321",
                    },
                ]
            }
        ]
    ]


# test_interface_template_not_collecting_all_data_reduced()


@pytest.mark.skipif(True, reason="Need to fix this one")
def test_interface_template_not_collecting_all_data_reduced_2():
    """
    Below template and data producing this result:

    [[{'interfaces': [{'interface': 'TenGigE0/0/0/5'},
                      {'interface': 'TenGigE0/0/0/5.100',
                       'mac_address': '200.b19.1234'},
                      {'interface': 'BVI101',
                       'ipv4': [{'ipv4': '192.168.101.1 255.255.255.0'}]},
                      {'interface': 'HundredGigE0/0/1/0',
                       'mac_address': '200.b19.5678'}]}]]

    Interface BVI should not have IPv4 address matched, but
    should have mac-address matched. Problem is due to that
    l2transport group starts and it has group for IPv4 addresses,
    next match after matching IPv4 is mac-address, but his parent
    is a different group, as a result IPv4 address saved under wrong group
    and mac-address not saved at all

    IDEA: try to implement automatic end of group tracking, to add pevious
    groups to self.ended_groups if next, different group starts.
    
    Current solution to this problem would be to use _end_ to explicitly 
    indicate end of group
    """
    data = """
interface TenGigE0/0/0/5
!
interface TenGigE0/0/0/5.100 l2transport
 mac-address 200.b19.1234
!
interface BVI101
 ipv4 address 192.168.101.1 255.255.255.0
 mac-address 200.b19.4321
!
interface HundredGigE0/0/1/0
 mac-address 200.b19.5678
!
    """
    template_original = """
<group name="interfaces">

## matches primary interfaces
<group>
interface {{ interface }}
 mac-address {{ mac_address }}
</group>

## matches sub-interfaces
<group>
interface {{ interface }} l2transport
 <group name="ipv4*" method="table" containsall="ipv4">
 ipv4 address {{ ipv4 | _line_ | _exact_ }}
 </group>
</group>

</group>    
    """
    parser = ttp(data, template_original, log_level="error")
    parser.parse()
    res = parser.result()
    pprint.pprint(res, width=80)


# test_interface_template_not_collecting_all_data_reduced_2()

def test_issue_61():
    data = """
banner motd &
BANNER MESSAGE line 1
BANNER MESSAGE line 2
BANNER MESSAGE line 3
&
some
other staff
    """
    template_to_match_marker = "banner motd {{ marker }}"
    template_to_parse_banner = """
<group name="motd">
banner motd {{ ignore(banner_marker) }} {{ _start_ }}
{{ banner_mesage | _line_ | joinmatches("\\n") }}
{{ ignore(banner_marker) }} {{ _end_ }}
</group>
    """
    # extract marker value
    parser = ttp(data, template_to_match_marker)
    parser.parse()
    marker = parser.result()[0][0]["marker"]
    
    # parse banner
    parser = ttp(data, template_to_parse_banner, vars={"banner_marker": marker})    
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [[{'motd': {'banner_mesage': 'BANNER MESSAGE line 1\n'
                                               'BANNER MESSAGE line 2\n'
                                               'BANNER MESSAGE line 3'}}]]
                                               
# test_issue_61()

def test_fortigate_intf_parsing():
    template = """
<group name="interfaces">
config system interface {{ _start_ }}
    <group name="/interfaces*">
    edit "{{ interface }}"
        set allowaccess {{ allowaccess }}
        set description "{{ description }}"
        set interface "{{ phy_interface }}"
        set snmp-index {{ snmp_index }}
        set type {{ fgt_int_type }}
        set vdom "{{ vdom }}"
        set vlanid {{ vlan }}
    next {{ _end_ }}
    </group>
end {{ _end_ }}
</group>
    """
    data = """
config system np6
    edit "np6_0"
    next
end
config system interface
    edit "mgmt1"
        set vdom "root"
        set ip 10.10.10.1 255.255.255.248
        set allowaccess ping
        set type physical
        set description "mgmt1"
        set snmp-index 1
    next
    edit "port1"
        set vdom "internal"
        set ip 20.20.20.1 255.255.255.248
        set allowaccess ping
        set type physical
        set snmp-index 2
    next
end
config system custom-language
    edit "en"
        set filename "en"
    next
    edit "fr"
        set filename "fr"
    next
end    
    """
    parser = ttp(data, template)    
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [[{'interfaces': [{'allowaccess': 'ping',
                                     'description': 'mgmt1',
                                     'fgt_int_type': 'physical',
                                     'interface': 'mgmt1',
                                     'snmp_index': '1',
                                     'vdom': 'root'},
                                    {'allowaccess': 'ping',
                                     'fgt_int_type': 'physical',
                                     'interface': 'port1',
                                     'snmp_index': '2',
                                     'vdom': 'internal'}]}]]
                                     
# test_fortigate_intf_parsing()


def test_issue_57_one_more():
    """
    Without _anonymous_ group groups id formation bug fix 
    below template/data were producitng this result:
[[{'portchannel': {'1': {'local_members': [{}],
                         'remote_members': [{'flag': '{EF}',
                                             'interface': 'GE6/0/1',
                                             'mac': '0000-0000-0000',
                                             'oper_key': '0',
                                             'priority': '32768',
                                             'status': '0',
                                             'sys_id': '0x8000'},
                                            {'flag': '{EF}',
                                             'interface': 'GE6/0/2',
                                             'mac': '0000-0000-0000',
                                             'oper_key': '0',
                                             'priority': '32768',
                                             'status': '0',
                                             'sys_id': '0x8000'}]},
                   '2': {'local_members': [{}],
                         'remote_members': [{'flag': '{EF}',
                                             'interface': 'GE6/0/3',
                                             'mac': '0000-0000-0000',
                                             'oper_key': '0',
                                             'priority': '32768',
                                             'status': '0',
                                             'sys_id': '0x8000'},
                                            {'flag': '{EF}',
                                             'interface': 'GE6/0/4',
                                             'mac': '0000-0000-0000',
                                             'oper_key': '0',
                                             'priority': '32768',
                                             'status': '0',
                                             'sys_id': '0x8000'}]}}}]]
    Further debugging revelead the flaw in results selection logic,
    due to exclude("Port") statemets group was invalidated and anonymous group_id
    was same as parent group_id resulting in new anonymous group matches were not 
    able to restart the group, fixed by changing the way how anonymous group id formed.
    
    Before fix:

    self.ended_groups:  set()
    re_["GROUP"].group_id:  ('portchannel.{{channel_number}}.local_members*', 0)
    re_["GROUP"].parent_group_id:  ('portchannel.{{channel_number}}.local_members*', 0)
    
    self.ended_groups:  {('portchannel.{{channel_number}}.local_members*', 0)}
    re_["GROUP"].group_id:  ('portchannel.{{channel_number}}.local_members*', 0)
    re_["GROUP"].parent_group_id:  ('portchannel.{{channel_number}}.local_members*', 0)
    
    self.ended_groups:  {('portchannel.{{channel_number}}.local_members*', 0)}
    re_["GROUP"].group_id:  ('portchannel.{{channel_number}}.local_members*', 0)
    re_["GROUP"].parent_group_id:  ('portchannel.{{channel_number}}.local_members*', 0)

    After fix:

    self.ended_groups:  set()
    re_["GROUP"].group_id:  ('portchannel.{{channel_number}}.local_members*._anonymous_', 0)
    re_["GROUP"].parent_group_id:  ('portchannel.{{channel_number}}.local_members*', 0)
    
    self.ended_groups:  {('portchannel.{{channel_number}}.local_members*._anonymous_', 0)}
    re_["GROUP"].group_id:  ('portchannel.{{channel_number}}.local_members*._anonymous_', 0)
    re_["GROUP"].parent_group_id:  ('portchannel.{{channel_number}}.local_members*', 0)
    
    self.ended_groups:  set()
    re_["GROUP"].group_id:  ('portchannel.{{channel_number}}.local_members*._anonymous_', 0)
    re_["GROUP"].parent_group_id:  ('portchannel.{{channel_number}}.local_members*', 0)
    """
    data = """
Loadsharing Type: Shar -- Loadsharing, NonS -- Non-Loadsharing
Port Status: S -- Selected, U -- Unselected,
             I -- Individual, * -- Management port
Flags:  A -- LACP_Activity, B -- LACP_Timeout, C -- Aggregation,
        D -- Synchronization, E -- Collecting, F -- Distributing,
        G -- Defaulted, H -- Expired

Aggregate Interface: Bridge-Aggregation1
Aggregation Mode: Dynamic
Loadsharing Type: Shar
Management VLAN : None
System ID: 0x8000, d07e-28b5-a200
Local:
  Port             Status  Priority Oper-Key  Flag
--------------------------------------------------------------------------------
  GE6/0/1          U       32768    1         {ACG}
  GE6/0/2          U       32768    1         {ACG}
Remote:
  Actor            Partner Priority Oper-Key  SystemID               Flag
--------------------------------------------------------------------------------
  GE6/0/1          0       32768    0         0x8000, 0000-0000-0000 {EF}
  GE6/0/2          0       32768    0         0x8000, 0000-0000-0000 {EF}

Aggregate Interface: Bridge-Aggregation2
Aggregation Mode: Dynamic
Loadsharing Type: Shar
Management VLAN : None
System ID: 0x8000, d07e-28b5-a200
Local:
  Port             Status  Priority Oper-Key  Flag
--------------------------------------------------------------------------------
  GE6/0/3          U       32768    2         {ACG}
  GE6/0/4          U       32768    2         {ACG}
Remote:
  Actor            Partner Priority Oper-Key  SystemID               Flag
--------------------------------------------------------------------------------
  GE6/0/3          0       32768    0         0x8000, 0000-0000-0000 {EF}
  GE6/0/4          0       32768    0         0x8000, 0000-0000-0000 {EF}
    """
    template = """
<group name = "portchannel.{{channel_number}}">
Aggregate Interface: Bridge-Aggregation{{ channel_number}}

<group name = "local_members*" void="">
Local: {{_start_}}
  <group>
  {{interface  | exclude("Port") }} {{status}} {{priority}} {{oper_key }} {{flag}}
  </group>
</group>

<group name = "remote_members*">
  {{interface }} {{status}} {{priority}} {{oper_key}} {{sys_id}}, {{ mac | MAC }} {{flag}}
</group>

</group>
    """
    parser = ttp(data, template)    
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [[{'portchannel': {'1': {'local_members': [{'flag': '{ACG}',
                                                              'interface': 'GE6/0/1',
                                                              'oper_key': '1',
                                                              'priority': '32768',
                                                              'status': 'U'},
                                                             {'flag': '{ACG}',
                                                              'interface': 'GE6/0/2',
                                                              'oper_key': '1',
                                                              'priority': '32768',
                                                              'status': 'U'}],
                                           'remote_members': [{'flag': '{EF}',
                                                               'interface': 'GE6/0/1',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'},
                                                              {'flag': '{EF}',
                                                               'interface': 'GE6/0/2',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'}]},
                                     '2': {'local_members': [{'flag': '{ACG}',
                                                              'interface': 'GE6/0/3',
                                                              'oper_key': '2',
                                                              'priority': '32768',
                                                              'status': 'U'},
                                                             {'flag': '{ACG}',
                                                              'interface': 'GE6/0/4',
                                                              'oper_key': '2',
                                                              'priority': '32768',
                                                              'status': 'U'}],
                                           'remote_members': [{'flag': '{EF}',
                                                               'interface': 'GE6/0/3',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'},
                                                              {'flag': '{EF}',
                                                               'interface': 'GE6/0/4',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'}]}}}]]
# test_issue_57_one_more()


def test_issue_57_one_more_answer():
    data = """
Loadsharing Type: Shar -- Loadsharing, NonS -- Non-Loadsharing
Port Status: S -- Selected, U -- Unselected,
             I -- Individual, * -- Management port
Flags:  A -- LACP_Activity, B -- LACP_Timeout, C -- Aggregation,
        D -- Synchronization, E -- Collecting, F -- Distributing,
        G -- Defaulted, H -- Expired

Aggregate Interface: Bridge-Aggregation1
Aggregation Mode: Dynamic
Loadsharing Type: Shar
Management VLAN : None
System ID: 0x8000, d07e-28b5-a200
Local:
  Port             Status  Priority Oper-Key  Flag
--------------------------------------------------------------------------------
  GE6/0/1          U       32768    1         {ACG}
  GE6/0/2          U       32768    1         {ACG}
Remote:
  Actor            Partner Priority Oper-Key  SystemID               Flag
--------------------------------------------------------------------------------
  GE6/0/1          0       32768    0         0x8000, 0000-0000-0000 {EF}
  GE6/0/2          0       32768    0         0x8000, 0000-0000-0000 {EF}

Aggregate Interface: Bridge-Aggregation2
Aggregation Mode: Dynamic
Loadsharing Type: Shar
Management VLAN : None
System ID: 0x8000, d07e-28b5-a200
Local:
  Port             Status  Priority Oper-Key  Flag
--------------------------------------------------------------------------------
  GE6/0/3          U       32768    2         {ACG}
  GE6/0/4          U       32768    2         {ACG}
Remote:
  Actor            Partner Priority Oper-Key  SystemID               Flag
--------------------------------------------------------------------------------
  GE6/0/3          0       32768    0         0x8000, 0000-0000-0000 {EF}
  GE6/0/4          0       32768    0         0x8000, 0000-0000-0000 {EF}
    """
    template = """
<group name = "portchannel.{{channel_number}}">
Aggregate Interface: Bridge-Aggregation{{ channel_number}}

<group name = "local_members*">
  {{interface}} {{status}} {{priority | DIGIT}} {{oper_key | DIGIT}} {{flag}}
</group>

<group name = "remote_members*">
  {{interface}} {{status}} {{priority | DIGIT}} {{oper_key | DIGIT}} {{sys_id}}, {{ mac | MAC }} {{flag}}
</group>

</group>
    """
    parser = ttp(data, template)    
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'portchannel': {'1': {'local_members': [{'flag': '{ACG}',
                                                              'interface': 'GE6/0/1',
                                                              'oper_key': '1',
                                                              'priority': '32768',
                                                              'status': 'U'},
                                                             {'flag': '{ACG}',
                                                              'interface': 'GE6/0/2',
                                                              'oper_key': '1',
                                                              'priority': '32768',
                                                              'status': 'U'}],
                                           'remote_members': [{'flag': '{EF}',
                                                               'interface': 'GE6/0/1',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'},
                                                              {'flag': '{EF}',
                                                               'interface': 'GE6/0/2',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'}]},
                                     '2': {'local_members': [{'flag': '{ACG}',
                                                              'interface': 'GE6/0/3',
                                                              'oper_key': '2',
                                                              'priority': '32768',
                                                              'status': 'U'},
                                                             {'flag': '{ACG}',
                                                              'interface': 'GE6/0/4',
                                                              'oper_key': '2',
                                                              'priority': '32768',
                                                              'status': 'U'}],
                                           'remote_members': [{'flag': '{EF}',
                                                               'interface': 'GE6/0/3',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'},
                                                              {'flag': '{EF}',
                                                               'interface': 'GE6/0/4',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'}]}}}]]
# test_issue_57_one_more_answer()


def test_issue_57_one_more_empty_dict_in_res():
    """
    Without fix this results produced:
    
[[{'portchannel': {'1': {'local_members': [{},
                                           {'flag': '{ACG}',
                                            'interface': 'GE6/0/1',
                                            'oper_key': '1',
                                            'priority': '32768',
                                            'status': 'U'},
                                           {'flag': '{ACG}',
                                            'interface': 'GE6/0/2',
                                            'oper_key': '1',
                                            'priority': '32768',
                                            'status': 'U'}],
                         'remote_members': [{},
                                            {'flag': '{EF}',
                                             'interface': 'GE6/0/1',
                                             'mac': '0000-0000-0000',
                                             'oper_key': '0',
                                             'priority': '32768',
                                             'status': '0',
                                             'sys_id': '0x8000'},
                                            {'flag': '{EF}',
                                             'interface': 'GE6/0/2',
                                             'mac': '0000-0000-0000',
                                             'oper_key': '0',
                                             'priority': '32768',
                                             'status': '0',
                                             'sys_id': '0x8000'}]},
                   '2': {'local_members': [{},
                                           {'flag': '{ACG}',
                                            'interface': 'GE6/0/3',
                                            'oper_key': '2',
                                            'priority': '32768',
                                            'status': 'U'},
                                           {'flag': '{ACG}',
                                            'interface': 'GE6/0/4',
                                            'oper_key': '2',
                                            'priority': '32768',
                                            'status': 'U'}],
                         'remote_members': [{},
                                            {'flag': '{EF}',
                                             'interface': 'GE6/0/3',
                                             'mac': '0000-0000-0000',
                                             'oper_key': '0',
                                             'priority': '32768',
                                             'status': '0',
                                             'sys_id': '0x8000'},
                                            {'flag': '{EF}',
                                             'interface': 'GE6/0/4',
                                             'mac': '0000-0000-0000',
                                             'oper_key': '0',
                                             'priority': '32768',
                                             'status': '0',
                                             'sys_id': '0x8000'}]}}}]]
                                             
    Above results contain empty dictionary list item, this is because 
    local_members* and remote_members* use * to indicate list item
    as a result self.dict_by_path was returning E as a list element,
    and results were appended to that element, but results are empty dictionary,
    update saving logic to check if results are empty and skip appending them 
    if so.
    """
    data = """
Loadsharing Type: Shar -- Loadsharing, NonS -- Non-Loadsharing
Port Status: S -- Selected, U -- Unselected,
             I -- Individual, * -- Management port
Flags:  A -- LACP_Activity, B -- LACP_Timeout, C -- Aggregation,
        D -- Synchronization, E -- Collecting, F -- Distributing,
        G -- Defaulted, H -- Expired

Aggregate Interface: Bridge-Aggregation1
Aggregation Mode: Dynamic
Loadsharing Type: Shar
Management VLAN : None
System ID: 0x8000, d07e-28b5-a200
Local:
  Port             Status  Priority Oper-Key  Flag
--------------------------------------------------------------------------------
  GE6/0/1          U       32768    1         {ACG}
  GE6/0/2          U       32768    1         {ACG}
Remote:
  Actor            Partner Priority Oper-Key  SystemID               Flag
--------------------------------------------------------------------------------
  GE6/0/1          0       32768    0         0x8000, 0000-0000-0000 {EF}
  GE6/0/2          0       32768    0         0x8000, 0000-0000-0000 {EF}

Aggregate Interface: Bridge-Aggregation2
Aggregation Mode: Dynamic
Loadsharing Type: Shar
Management VLAN : None
System ID: 0x8000, d07e-28b5-a200
Local:
  Port             Status  Priority Oper-Key  Flag
--------------------------------------------------------------------------------
  GE6/0/3          U       32768    2         {ACG}
  GE6/0/4          U       32768    2         {ACG}
Remote:
  Actor            Partner Priority Oper-Key  SystemID               Flag
--------------------------------------------------------------------------------
  GE6/0/3          0       32768    0         0x8000, 0000-0000-0000 {EF}
  GE6/0/4          0       32768    0         0x8000, 0000-0000-0000 {EF}
    """
    template = """
<group name = "portchannel.{{channel_number}}">
Aggregate Interface: Bridge-Aggregation{{ channel_number}}

<group name = "local_members*">
Local: {{_start_}}
  <group>
  {{interface }} {{status}} {{priority}} {{oper_key | DIGIT }} {{flag}}
  </group>
</group>

<group name = "remote_members*">
Remote: {{_start_}}
  <group>
  {{interface }} {{status}} {{priority}} {{oper_key}} {{sys_id}}, {{ mac | MAC }} {{flag}}
  </group>
</group>

</group>
    """
    parser = ttp(data, template)    
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'portchannel': {'1': {'local_members': [{'flag': '{ACG}',
                                                              'interface': 'GE6/0/1',
                                                              'oper_key': '1',
                                                              'priority': '32768',
                                                              'status': 'U'},
                                                             {'flag': '{ACG}',
                                                              'interface': 'GE6/0/2',
                                                              'oper_key': '1',
                                                              'priority': '32768',
                                                              'status': 'U'}],
                                           'remote_members': [{'flag': '{EF}',
                                                               'interface': 'GE6/0/1',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'},
                                                              {'flag': '{EF}',
                                                               'interface': 'GE6/0/2',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'}]},
                                     '2': {'local_members': [{'flag': '{ACG}',
                                                              'interface': 'GE6/0/3',
                                                              'oper_key': '2',
                                                              'priority': '32768',
                                                              'status': 'U'},
                                                             {'flag': '{ACG}',
                                                              'interface': 'GE6/0/4',
                                                              'oper_key': '2',
                                                              'priority': '32768',
                                                              'status': 'U'}],
                                           'remote_members': [{'flag': '{EF}',
                                                               'interface': 'GE6/0/3',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'},
                                                              {'flag': '{EF}',
                                                               'interface': 'GE6/0/4',
                                                               'mac': '0000-0000-0000',
                                                               'oper_key': '0',
                                                               'priority': '32768',
                                                               'status': '0',
                                                               'sys_id': '0x8000'}]}}}]]
# test_issue_57_one_more_empty_dict_in_res()


def test_issue_62():
    data = """
security:
	received (in 351815.564 secs):
		220203204 packets	14522703007 bytes
		3 pkts/sec	41010 bytes/sec
	transmitted (in 351815 secs):
		0 packets	0 bytes
		0 pkts/sec	0 bytes/sec
	"""
    template = """
<group name = '{{ nameif }}'>
{{ nameif | ORPHRASE }}:
{{ ignore('\s+') }}received{{ ignore('.*') }}
{{ ignore('\s+') }}{{ rpps | DIGIT }} pkts/sec{{ ignore('.*') }}
{{ ignore('\s+') }}trasmitted{{ ignore('.*') }}
{{ ignore('\s+') }}{{ tpps | DIGIT }} pkts/sec{{ ignore('.*') }}
</group>
	"""
    parser = ttp(data, template)    
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
	
    assert res == [[{'security': {'rpps': '3'}}]]
# test_issue_62()


def test_issue_62_fix():
    data = """
security:
	received (in 351815.564 secs):
		220203204 packets	14522703007 bytes
		3 pkts/sec	41010 bytes/sec
	transmitted (in 351815 secs):
		0 packets	0 bytes
		0 pkts/sec	0 bytes/sec
	"""
    template = """
<group name = '{{ nameif }}'>
{{ nameif | ORPHRASE }}:

<group name="rx">
	received (in {{ ignore }} secs): {{ _start_ }}
		{{ rpps }} pkts/sec	41010 bytes/sec
</group>

<group name="tx">
	transmitted (in {{ ignore }} secs): {{ _start_ }}
		{{ tpps }} pkts/sec	0 bytes/sec
</group>

</group>
	"""
    parser = ttp(data, template)    
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'security': {'rx': {'rpps': '3'}, 'tx': {'tpps': '0'}}}]]

# test_issue_62_fix()


def test_lookup_crosstemplates():
    template = """
<template name="interfaces">
<input load="text">
interface FastEthernet2.13
 description Customer CPE interface
 ip address 10.12.13.1 255.255.255.0
 vrf forwarding CPE-VRF
!
interface GigabitEthernet2.13
 description Customer CPE interface
 ip address 10.12.14.1 255.255.255.0
 vrf forwarding CUST1
!
</input>

<group name="{{ interface }}">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ subnet | PHRASE | to_ip | network | to_str }}
 vrf forwarding {{ vrf }}
</group>
</template>

<template name="arp">
<input load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.2        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.14.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
</input>

<group lookup="interface, template='interfaces', update=True">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
</group>
</template>
    """
    parser = ttp()
    parser.add_template(template)
    parser.parse()
    
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'FastEthernet2.13': {'description': 'Customer CPE interface',
                        'subnet': '10.12.13.0/24',
                        'vrf': 'CPE-VRF'},
   'GigabitEthernet2.13': {'description': 'Customer CPE interface',
                           'subnet': '10.12.14.0/24',
                           'vrf': 'CUST1'}}],
 [[{'age': '98',
    'description': 'Customer CPE interface',
    'interface': 'FastEthernet2.13',
    'ip': '10.12.13.2',
    'mac': '0950.5785.5cd1',
    'subnet': '10.12.13.0/24',
    'vrf': 'CPE-VRF'},
   {'age': '131',
    'description': 'Customer CPE interface',
    'interface': 'GigabitEthernet2.13',
    'ip': '10.12.14.3',
    'mac': '0150.7685.14d5',
    'subnet': '10.12.14.0/24',
    'vrf': 'CUST1'}]]]

# test_lookup_crosstemplates()