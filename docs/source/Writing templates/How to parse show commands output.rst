How to parse show commands output
=================================

Show commands output parsing with TTP is the same as parsing any text data that contains repetitive patterns and require a certain level of familiarity with tools built into TTP to not only parse but also process match results.

As a usecase let's consider that we need to parse "show cdp neighbours detail" command output of Cisco IOS devices, here is how source data might look like::

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
	
And the goal is to get this results structure::

	{
		local_hostname: str,
		local_interface: str,
		peer_hostname: str,
		peer_interface: str,
		peer_ip: ip,
		peer_platform: [cap1, cap2]
		peer_capabilities: str,
		peer_software: str
	}
	
Template for that might looks like this::

    <vars>
    hostname="gethostname"
    <vars/>
    
    <group name="cdp_peers">
    ------------------------- {{ _start_ }}
    Device ID: {{ peer_hostname }}
    IP address: {{ peer_ip }}
    Platform: {{ peer_platform | ORPHRASE}},  Capabilities: {{ peer_capabilities | ORPHRASE }} 
    Interface: {{ local_interface }},  Port ID (outgoing port): {{ peer_interface }}
    {{ local_hostname | set("hostname") }}
    <group name="peer_software">
    Version : {{ _start_ }}
    {{ peer_software | _line_ }}
    {{ _end_ }}
    </group>
    </group>