.. |br| raw:: html

   <br />

Indicators
================

Indicators, or directives, can be used to change parsing logic or indicate certain events.

.. list-table:: indicators
   :widths: 10 90
   :header-rows: 1

   * - Name
     - Description
   * - `_exact_`_
     - Leaves digits as is without replacing them with ``\d+`` pattern
   * - `_exact_space_`_
     - Leaves space characters as is without replacing them with ``r(\\ +)`` pattern
   * - `_start_`_
     - Explicitly indicates start of the group
   * - `_end_`_
     - Explicitly indicates end of the group
   * - `_line_`_
     - If present, any line will be matched
   * - `ignore`_
     - Substitute string at given position with regular expression without matching results
   * - `_headers_`_
     - To dynamically form regex for parsing fixed-width, one-line text tables

_exact_
------------------------------------------------------------------------------
``{{ name | _exact_ }}``

By default, the parser will replace all digits in a template with the '\d+' pattern.
However, if ``_exact_`` is present in any match variable within a line, digits will remain unchanged and parsed as is.

This is an important consideration for when a pattern contains numbers.

**Example: capturing an IPv4 configuration**

Sample Data::

 vrf VRF-A
  address-family ipv4 unicast
   maximum prefix 1000 80
  !
  address-family ipv6 unicast
   maximum prefix 300 80
  !

Template without ``_exact_``::

 <group name="vrfs">
 vrf {{ vrf }}
  <group name="ipv4_config">
  address-family ipv4 unicast {{ _start_ }}
   maximum prefix {{ limit }} {{ warning }}
  </group>
 </group>

Result::

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

As you can see, the ipv6 part of vrf configuration was matched as well, which wasn't what we wanted.
A possible solution would be to use``_exact_`` to indicate that "ipv4" should be matched exactly.

Template with ``_exact_``::

 <group name="vrfs">
 vrf {{ vrf }}
  <group name="ipv4_config">
  address-family ipv4 unicast {{ _start_ }}{{ _exact_ }}
   maximum prefix {{ limit }} {{ warning }}
  !{{ _end_ }}
  </group>
 </group>

Result::

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

By default, the parser will replace all space characters in a template with the with '\\ +' pattern.
However, if ``_exact_space_`` is present in any match variable within a line, space characters will remain unchanged and parsed as is.

_start_
------------------------------------------------------------------------------
``{{ name | _start_ }}`` or {{ _start_ }}

Explicitly indicates the start of the group by matching a certain line, or even multiple lines.

**Example-1**

In this example, line "-------------------------" can serve as an indicator of the beginning of the group, but we do not have any match variables defined in it.

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

Result::

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
``pattern {{ _end_ }}``

Explicitly indicates the end of the group.
When a line with the ``_end_`` indicator is encountered by the parser, it acts as a trigger for processing and saving group results into the results tree.

The purpose of this indicator is to optimize parsing performance. TTP is able to determine the end of the group faster and eliminate checking of unrelated text data.

.. warning :: using ``_end_`` together with match variables (i.e. ``{{ name | _end_ }}`` ) is not supported as of TTP 0.6.0 and earlier.

_line_
------------------------------------------------------------------------------
``{{ name | _line_ }}``

The main purpose of the ``_line_`` indicator is to match and collect data that hasn't been matched by other variables.

This indicator serves two purposes. Firstly, special regex will be used to match any line in text.
Moreover, additional logic will be incorporated when a portion of text data is matched by ``_line_`` and other regular expressions simultaneously.

All TTP match variables functions can be used with ``_line_``. For instance, the ``contains`` function can be used to filter results.

TTP will only assign the last line matched by ``_line_`` to the variable. If multiple lines need to be saved, use ``joinmatches``.

.. warning:: ``_line_`` is computationally intensive and can result in longer processing times. It is recommended to use ``_end_`` together with ``_line_`` whenever possible to minimize performance impacts. As always, this can be helped by having very clear source data, as it aids avoiding false positives (i.e. undesirable matches).

**Example**

Let's say we want to get all port-security related configurations on an interface, and save them into a single match variable (``port_security_cfg``).

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

``value`` can be any of the following:

* regular expression string - regex to use to substitute a portion of the string. Default is ``\S+``, meaning any non-space character one or more times.
* template variable - name of template variable that contains regular expression to use
* built in re pattern - name of regex pattern to use, for example :ref:`Match Variables/Patterns:WORD`

.. note:: A template variable should be used if your ignore pattern contains a ``|`` (pipe) character. The pipe character is used by TTP to separate functions and cannot be used in inline regex.

The primary use case of this indicator is to ignore alpha-numerical characters that can vary, or ignore portions of the line.

**Example-1**

For the following data, we only want to extract the bia MAC address within the parentheses, ``c201.1d00.1234`` and ``c201.1d00.1111``.

Sample Data::

    FastEthernet0/0 is up, line protocol is up
      Hardware is Gt96k FE, address is c201.1d00.0000 (bia c201.1d00.1234)
      MTU 1500 bytes, BW 100000 Kbit/sec, DLY 1000 usec,
    FastEthernet0/1 is up, line protocol is up
      Hardware is Gt96k FE, address is b20a.1e00.8777 (bia c201.1d00.1111)
      MTU 1500 bytes, BW 100000 Kbit/sec, DLY 1000 usec,


We could try the following template::

    {{ interface }} is up, line protocol is up
      Hardware is Gt96k FE, address is c201.1d00.0000 (bia {{MAC}})
      MTU {{ mtu }} bytes, BW 100000 Kbit/sec, DLY 1000 usec,

But it would only match for a single case! We'd only get matches for "c201.1d00.0000", since it's hard-coded into the template.
The bia MAC address for FastEthernet0/1 would not be matched, and we would receive the following result::

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

Solution template::

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

In this example, we use ``ignore`` with a template variable "pattern_var": a regex pattern that contains the pipe symbol.

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
``head1  head2 ... headN {{ _headers_ }}`` or ``head1  head2 ... headN {{ _headers_ | columns(5) }}``

When used with a line of headers, this indicator dynamically forms regular expressions for parsing fixed-width, single-line text tables.

Starting with TTP 0.8.1, the ``columns`` attribute can be used with ``_headers_``.
``columns`` is a single digit that represents the number of mandatory columns for ``_headers_`` to match.

The default value of ``columns`` is the number of headers minus 2 i.e. ``len(headers) - 2``

Calculations are made by the parser based on these headers. Column width is based on the character lengths of headers, and they are also used to dynamically form variable names.
As a result there are a number of restrictions:

* headers line must match original data to calculate correct columns width
* headers must be separated by at least one space character
* headers must be left-aligned to indicate beginning of the column
* headers cannot contain spaces - use underscores instead
* headers must be valid Python identifiers, since the parser uses them as variable names
* match variable functions are not supported for headers. Instead, group functions can be used for processing
* by default, the last column can be empty and the next to last column is optional. This can be adjusted with the ``columns`` attribute

How column width is calculated::

    Column width calculated from left to the left edge of each header:

    Port      Name               Status       Vlan       Duplex  Speed Type
    <--------><-----------------><-----------><---------><------><----><-infinite->
        C1            C2              C3           C4       C5     C6       C7

Assuming ``columns`` attribute value is 5, this regex set is formed:

* C1 - C4 are mandatory columns. Their width is represented by the regex pattern ``.{x}`` , where ``x`` is column width (represented by ``<---->`` values above)
* C5 is also mandatory, represented by the regex pattern ``.{1, x}`` , where ``x`` is columns width
* C6 is an optional column, represented by the regex pattern ``.{0, x}`` , where ``x`` is columns width
* The last column C7 is also optional, represented by the regex pattern ``.*``

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

Header line can be indented by a number of spaces or tabs, but each tab replaced with 4 space characters to calculate column width.

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

Example-3

This example demonstrates how to use ``columns`` attribute. Below text data has 7 distinctive columns, meaning we can adjust ``columns`` attribute value from 1 to 7 depending on results we need to produce.

Data::

    Port      Name               Status       Vlan       Duplex  Speed Type
    Gi0/1
    Gi0/2     PIT-VDU212
    Gi0/3     PIT-VDU212         notconnect
    Gi0/4     PIT-VDU212         notconnect   18
    Gi0/5     PIT-VDU212         notconnect   18         auto
    Gi0/6     PIT-VDU212         notconnect   18         auto    auto
    Gi0/7     PIT-VDU212         notconnect   18         auto    auto  10/100/1000BaseTX

Template::

    <group name="columns_7">
    Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(7) }}
    </group>

    <group name="columns_6">
    Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(6) }}
    </group>

    <group name="columns_5">
    Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(5) }}
    </group>

    <group name="columns_4">
    Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(4) }}
    </group>

    <group name="columns_3">
    Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(3) }}
    </group>

Result::

    [[{'columns_3': [{'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/3', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': ''},
                     {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/4', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
       'columns_4': [{'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/4', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
       'columns_5': [{'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
       'columns_6': [{'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                     {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
       'columns_7': {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}}]]

The smaller the value of ``columns`` attribute is, the more lines with optional/empty columns will be matched. 
The larger the value is, the stricter the ``_headers_`` regex will be, producing less matches with empty columns.
