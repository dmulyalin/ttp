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