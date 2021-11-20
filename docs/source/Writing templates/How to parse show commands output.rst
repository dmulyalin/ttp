How to parse show commands output
=================================

Show commands output parsing with TTP is the same as parsing any text data that contains repetitive patterns and require a certain level of familiarity with tools built into TTP to not only parse but also process match results.

As a use case let's consider parsing "show cdp neighbors detail" command output of Cisco IOS device, source data::

	my_switch_1#show cdp neighbors detail 
	-------------------------
	Device ID: switch-2.net
	Entry address(es): 
	IP address: 10.251.1.49
	Platform: cisco WS-C6509,  Capabilities: Router Switch IGMP 
	Interface: GigabitEthernet4/6,  Port ID (outgoing port): GigabitEthernet1/5
	Holdtime : 130 sec
	
	Version :
	Cisco Internetwork Operating System Software 
	IOS (tm) s72033_rp Software (s72033_rp-PK9SV-M), Version 12.2(17d)SXB11a, RELEASE SOFTWARE (fc1)
	Technical Support: http://www.cisco.com/techsupport
	Copyright (c) 1986-2006 by cisco Systems, Inc.
	Compiled Thu 13-Apr-06 04:50 by kehsiao
	
	advertisement version: 2
	VTP Management Domain: ''
	Duplex: full
	Unidirectional Mode: off
	
	-------------------------
	Device ID: switch-2
	Entry address(es): 
	IP address: 10.151.28.7
	Platform: cisco WS-C3560-48TS,  Capabilities: Switch IGMP 
	Interface: GigabitEthernet1/1,  Port ID (outgoing port): GigabitEthernet0/1
	Holdtime : 165 sec
	
	Version :
	Cisco IOS Software, C3560 Software (C3560-IPBASE-M), Version 12.2(25)SEB2, RELEASE SOFTWARE (fc1)
	Copyright (c) 1986-2005 by Cisco Systems, Inc.
	Compiled Tue 07-Jun-05 23:34 by yenanh
	
	advertisement version: 2
	Protocol Hello:  OUI=0x00000C, Protocol ID=0x0112; payload len=27, value=00000000FFFFFFFF010221FF00000000000000152BC02D80FF0000
	VTP Management Domain: ''
	Native VLAN: 500
	Duplex: full
	Unidirectional Mode: off
	
The goal is to get this results structure::

	{
		local_hostname: str,
		local_interface: str,
		peer_hostname: str,
		peer_interface: str,
		peer_ip: str,
		peer_platform: str,
		peer_capabilities: [cap1, cap2],
		peer_software: str
	}
	

Template to achieve this::

    <vars>
    hostname="gethostname"
    </vars>
    
    <group name="cdp_peers">
    ------------------------- {{ _start_ }}
    Device ID: {{ peer_hostname }}
    IP address: {{ peer_ip }}
    Platform: {{ peer_platform | ORPHRASE }},  Capabilities: {{ peer_capabilities | ORPHRASE | split(" ") }} 
    Interface: {{ local_interface }},  Port ID (outgoing port): {{ peer_interface }}
    {{ local_hostname | set("hostname") }}
	
    <group name="_">
    Version : {{ _start_ }}
    {{ peer_software | _line_ }}
    {{ _end_ }}
    </group>
	
    </group>
	
Results::

    [[[
        {
            "local_hostname": "my_switch_1",
            "local_interface": "GigabitEthernet4/6",
            "peer_capabilities": [
                "Router",
                "Switch",
                "IGMP"
            ],
            "peer_hostname": "switch-2.net",
            "peer_interface": "GigabitEthernet1/5",
            "peer_ip": "10.251.1.49",
            "peer_platform": "cisco WS-C6509",
            "peer_software": "Cisco Internetwork Operating System Software \nIOS (tm) s72033_rp Software (s72033_rp-PK9SV-M), Version 12.2(17d)SXB11a, RELEASE SOFTWARE (fc1)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2006 by cisco Systems, Inc.\nCompiled Thu 13-Apr-06 04:50 by kehsiao"
        },
        {
            "local_hostname": "my_switch_1",
            "local_interface": "GigabitEthernet1/1",
            "peer_capabilities": [
                "Switch",
                "IGMP"
            ],
            "peer_hostname": "switch-2",
            "peer_interface": "GigabitEthernet0/1",
            "peer_ip": "10.151.28.7",
            "peer_platform": "cisco WS-C3560-48TS",
            "peer_software": "Cisco IOS Software, C3560 Software (C3560-IPBASE-M), Version 12.2(25)SEB2, RELEASE SOFTWARE (fc1)\nCopyright (c) 1986-2005 by Cisco Systems, Inc.\nCompiled Tue 07-Jun-05 23:34 by yenanh"
        }
    ]]]
	
Special attention should be paid to this aspects of above template:

* use of explicit _start_ indicator to define start of the group
* ORPHRASE regex formatter to match a single word and collection of words
* _line_ indicator used within separate group to combine software version description, that group has special null path - "_" - indicating that result for this group should be merged with parent group
* explicit use of _end_ indicator to make sure that only relevant information matched
* special handling of peer_capabilities match result by converting into list by splitting match result using space character
