.. |br| raw:: html

   <br />

Indicators
================

Indicators or directives can be used to change parsing logic or indicate certain events.
	 
.. list-table:: indicators
   :widths: 10 90
   :header-rows: 1
   
   * - Name
     - Description  
   * - `_exact_`_ 
     - Threats digits as is without replacing them with ``\d+`` pattern
   * - `_exact_space_`_ 
     - Leave space characters in place without replacing them with ``r(\\ +)`` pattern
   * - `_start_`_ 
     - Explicitly indicates start of the group
   * - `_end_`_ 
     - Explicitly indicates end of the group
   * - `_line_`_ 
     - If present any line will be matched
   * - `ignore`_ 
     - Substitute string at given position with regular expression without matching results
   * - `_headers_`_ 
     - To dynamically form regex for parsing fixed-width, one-line text tables

_exact_
------------------------------------------------------------------------------
``{{ name | _exact_ }}``

By default all digits in template replaced with '\d+' pattern, if ``_exact_`` present in any match variable within that line, digits are unchanged and used for parsing as is.

**Example**

Sample Data::

 vrf VRF-A
  address-family ipv4 unicast
   maximum prefix 1000 80
  !
  address-family ipv6 unicast
   maximum prefix 300 80
  !
  
If Template::

 <group name="vrfs">
 vrf {{ vrf }}
  <group name="ipv4_config">
  address-family ipv4 unicast {{ _start_ }}
   maximum prefix {{ limit }} {{ warning }}
  </group>
 </group>
   
Result will be::

 {
     "vrfs": {
         "ipv4_config": [
             {
                 "limit": "1000",
                 "warning": "80"
             },
             {
                 "limit": "300",
                 "warning": "80"
             }
         ],
         "vrf": "VRF-A"
     }
 }
 
As you can see ipv6 part of vrf configuration was matched as well and we got undesirable results, one of the possible solutions would be to use _exact_ directive to indicate that "ipv4" should be matches exactly.

If Template::

 <group name="vrfs">
 vrf {{ vrf }}
  <group name="ipv4_config">
  address-family ipv4 unicast {{ _start_ }}{{ _exact_ }}
   maximum prefix {{ limit }} {{ warning }}
  !{{ _end_ }}
  </group>
 </group>
 
Result will be::

 {
     "vrfs": {
         "ipv4_config": {
             "limit": "1000",
             "warning": "80"
         },
         "vrf": "VRF-A"
     }
 }
 
_exact_space_
------------------------------------------------------------------------------
``{{ name | _exact_space_ }}``

By default all space characters in template replaced with '\\ +' pattern, if _exact_space_ present, space characters will stay unchanged and will be used for parsing as is.

_start_
------------------------------------------------------------------------------
``{{ name | _start_ }}`` or {{ _start_ }}

This directive can be used to explicitly indicate start of the group by matching certain line or if we have multiple lines that can indicate start of the same group.

**Example-1** 

In this example line "-------------------------" can serve as an indicator of the beginning of the group, but we do not have any match variables defined in it.

Sample data::

 switch-a#show cdp neighbors detail 
 -------------------------
 Device ID: switch-b
 Entry address(es): 
   IP address: 131.0.0.1
 
 -------------------------
 Device ID: switch-c
 Entry address(es): 
   IP address: 131.0.0.2
   
Template::

 <group name="cdp_peers">
 ------------------------- {{ _start_ }}
 Device ID: {{ peer_hostname }}
 Entry address(es): 
   IP address: {{ peer_ip }}
 </group>
 
Result::

 {
     "cdp_peers": [
         {
             "peer_hostname": "switch-b",
             "peer_ip": "131.0.0.1"
         },
         {
             "peer_hostname": "switch-c",
             "peer_ip": "131.0.0.2"
         }
     ]
 }
 
**Example-2**

In this example, two different lines can serve as an indicator of the start for the same group.

Sample Data::

 interface Tunnel2422
  description cpe-1
 !
 interface GigabitEthernet1/1
  description core-1
  
Template::

 <group name="interfaces">
 interface Tunnel{{ if_id }}
 interface GigabitEthernet{{ if_id | _start_ }}
  description {{ description }}
 </group>
 
Result will be::

 {
     "interfaces": [
         {
             "description": "cpe-1",
             "if_id": "2422"
         },
         {
             "description": "core-1",
             "if_id": "1/1"
         }
     ]
 }
 
_end_
------------------------------------------------------------------------------
``{{ name | _end_ }}`` or ``{{ _end_ }}``

Explicitly indicates the end of the group. If line was matched that has _end_ indicator assigned - that will trigger processing and saving group results into results tree. The purpose of this indicator is to optimize parsing performance allowing TTP to determine the end of the group faster and eliminate checking of unrelated text data.

_line_
------------------------------------------------------------------------------
``{{ name | _line_ }}``

This indicator serves double purpose, first of all, special regular expression will be used to match any line in text, moreover, additional logic will be incorporated for such a cases when same portion of text data was matched by _line_ and other regular expression simultaneously. Main use case for _line_ indicator is to match and collect data that not been matched by other match variables. 

All TTP match variables function can be used together with _line_ indicator, for instance ``contains`` function can be used to filter results.

TTP will assign only last line matched by _line_ to match variable, if multiple lines needs to be saved, ``joinmatches`` function can be used. 

.. warning:: _line_ expression is computation intensive and can take longer time to process, it is recommended to use _end_ indicator together with _line_ whenever possible to minimize performance impact. In addition, having as clear source data as possible also helps, as it allows to avoid false positives - unnecessary matches.

**Example**

Let's say we want to match all port-security related configuration on the interface and save it into port_security_cfg variable.

Template::

    <input load="text">
    interface Loopback0
     description Router-id-loopback
     ip address 192.168.0.113/24
    !
    interface Gi0/37
     description CPE_Acces
     switchport port-security
     switchport port-security maximum 5
     switchport port-security mac-address sticky
    !
    </input>
    
    <group>
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
     description {{ description }}
     ip vrf {{ vrf }}
     {{ port_security_cfg | _line_ | contains("port-security") | joinmatches }}
    ! {{ _end_ }}
    </group>

Results::

    [[{   'description': 'Router-id-loopback',
          'interface': 'Loopback0',
          'ip': '192.168.0.113',
          'mask': '24'},
      {   'description': 'CPE_Acces',
          'interface': 'Gi0/37',
          'port_security_cfg': 'switchport port-security\n'
                               'switchport port-security maximum 5\n'
                               'switchport port-security mac-address sticky'}
    						 ]]

ignore
------------------------------------------------------------------------------
``{{ ignore }}`` or ``{{ ignore("value") }}``

``value`` can be of:

* regular expression string - regex to use to substitute portion of the string, default is "\S+", meaning any non-space character one or more times.
* template variable name - name of template variable that contains regular expression to use
* built in re pattern name - name of regex patter to use, for example :ref:`Match Variables/Patterns:WORD`

.. note:: use template_variable_name if ignore pattern contains ``|`` (pipe) character, as pipe character used by TTP to separate match variable functions.

Primary use case of this indicator is to ignore changing alpha-numerical characters or ignore portion of the line. For example consider this data::

    FastEthernet0/0 is up, line protocol is up
      Hardware is Gt96k FE, address is c201.1d00.0000 (bia c201.1d00.1234)
      MTU 1500 bytes, BW 100000 Kbit/sec, DLY 1000 usec,
    FastEthernet0/1 is up, line protocol is up
      Hardware is Gt96k FE, address is b20a.1e00.8777 (bia c201.1d00.1111)
      MTU 1500 bytes, BW 100000 Kbit/sec, DLY 1000 usec,
  
**Example-1**

What if only need to extract bia MAC address within parenthesis, below template will **not** work for all cases::

    {{ interface }} is up, line protocol is up
      Hardware is Gt96k FE, address is c201.1d00.0000 (bia {{MAC}})
      MTU {{ mtu }} bytes, BW 100000 Kbit/sec, DLY 1000 usec,
	  
Result::

    [
        [
            {
                "MAC": "c201.1d00.1234",
                "interface": "FastEthernet0/0",
                "mtu": "1500"
            },
            {
                "interface": "FastEthernet0/1",
                "mtu": "1500"
            }
        ]
    ]
	
As we can see MAC address for FastEthernet0/1 was not matched due to the fact that "c201.1d00.0000" text was used in template, to fix it we need to ignore MAC address before parenthesis as it keeps changing across the source data::

    {{ interface }} is up, line protocol is up
      Hardware is Gt96k FE, address is {{ ignore }} (bia {{MAC}})
      MTU {{ mtu }} bytes, BW 100000 Kbit/sec, DLY 1000 usec,
	  
Result::

    [
        [
            {
                "MAC": "c201.1d00.1234",
                "interface": "FastEthernet0/0",
                "mtu": "1500"
            },
            {
                "MAC": "c201.1d00.1111",
                "interface": "FastEthernet0/1",
                "mtu": "1500"
            }
        ]
    ]
	
**Example-2**

In this example template variable "pattern_var" used together with ignore, that variable reference regular expression pattern that contains pipe symbol.

Template::

    <input load="text">
    FastEthernet0/0 is up, line protocol is up
      Hardware is Gt96k FE, address is c201.1d00.0000 (bia c201.1d00.1234)
      MTU 1500 bytes, BW 100000 Kbit/sec, DLY 1000 usec,
    FastEthernet0/1 is up, line protocol is up
      Hardware is Gt96k FE, address is b20a.1e00.8777 (bia c201.1d00.1111)
      MTU 1500 bytes, BW 100000 Kbit/sec, DLY 1000 usec,
    </input>
    
    <vars>
    pattern_var = "\S+|\d+"
    </vars>
    
    <group name="interfaces">
    {{ interface }} is up, line protocol is up
      Hardware is Gt96k FE, address is {{ ignore("pattern_var") }} (bia {{MAC}})
      MTU {{ mtu }} bytes, BW 100000 Kbit/sec, DLY 1000 usec,
    </group>
	
Results::

    [
        [
            {
                "interfaces": [
                    {
                        "MAC": "c201.1d00.1234",
                        "interface": "FastEthernet0/0",
                        "mtu": "1500"
                    },
                    {
                        "MAC": "c201.1d00.1111",
                        "interface": "FastEthernet0/1",
                        "mtu": "1500"
                    }
                ]
            }
        ]
    ]
	
_headers_
------------------------------------------------------------------------------
``head1  head2 ... headN {{ _headers_ }}``

This indicator uses headers line to dynamically form regular expression to parse fixed-width, one-line text tables.

Column width calculated based on header items length, variables names dynamically formed out of header items. As a result there are a number of restrictions:

* headers line must match original data to calculate correct columns width
* header items must be separated by at least one space character
* header items must be left-aligned to indicate beginning of the column
* header items cannot contain spaces, replace them with underscore
* header items must be valid Python identifies to form variables names
* match variable functions not supported for header items, instead, group functions and macro can be used for processing

**Example-1**

Template::

    <input load="text">
    Port      Name               Status       Vlan       Duplex  Speed Type
    Gi0/1     PIT-VDU213         connected    18         a-full  a-100 10/100/1000BaseTX
    Gi0/3     PIT-VDU212         notconnect   18           auto   auto 10/100/1000BaseTX
    Gi0/4                        connected    18         a-full  a-100 10/100/1000BaseTX
    Gi0/5                        notconnect   18           auto   auto 10/100/1000BaseTX
    Gi0/15                       connected    trunk        full   1000 1000BaseLX SFP
    Gi0/16    pitrs2201 te1/1/4  connected    trunk        full   1000  1000BaseLX SFP
    </input>
    
    <group>
    Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ }}
    </group>   

Result::

    [[[{'Duplex': 'a-full',
        'Name': 'PIT-VDU213',
        'Port': 'Gi0/1',
        'Speed': 'a-100',
        'Status': 'connected',
        'Type': '10/100/1000BaseTX',
        'Vlan': '18'},
       {'Duplex': 'a-full',
        'Name': '',
        'Port': 'Gi0/4',
        'Speed': 'a-100',
        'Status': 'connected',
        'Type': '10/100/1000BaseTX',
        'Vlan': '18'},
       {'Duplex': 'full',
        'Name': 'pitrs2201 te1/1/4',
        'Port': 'Gi0/16',
        'Speed': '1000',
        'Status': 'connected',
        'Type': '1000BaseLX SFP',
        'Vlan': 'trunk'}]]]
		
**Example-2**

Header can be indented by a number of spaces or tabs, but each tab replaced with 4 space characters to calculate column width.

Template::

    <input load="text">
       Network            Next Hop            Metric     LocPrf     Weight Path
    *>e11.11.1.111/32     12.123.12.1              0                     0 65000 ?
    *>e222.222.222.2/32   12.123.12.1              0                     0 65000 ?
    *>e333.33.333.333/32  12.123.12.1              0                     0 65000 ?
    </input>
    
    <group>
       Network            Next_Hop            Metric     LocPrf     Weight Path  {{ _headers_ }}
    </group>   


Result::

   [[[{'LocPrf': '',
       'Metric': '0',
       'Network': '*>e11.11.1.111/32',
       'Next_Hop': '12.123.12.1',
       'Path': '65000 ?',
       'Weight': '0'},
      {'LocPrf': '',
       'Metric': '0',
       'Network': '*>e222.222.222.2/32',
       'Next_Hop': '12.123.12.1',
       'Path': '65000 ?',
       'Weight': '0'},
      {'LocPrf': '',
       'Metric': '0',
       'Network': '*>e333.33.333.333/32',
       'Next_Hop': '12.123.12.1',
       'Path': '65000 ?',
       'Weight': '0'}]]]