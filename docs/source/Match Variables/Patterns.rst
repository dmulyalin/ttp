Regex Patterns
==============

Regexes are in the heart of TTP, but they hidden from user, match patterns or regex formatters can be used to explicitly specify regular expressions that should be used for parsing. 
     
By convention, regex patterns written in upper case, but it is not a hard requirement and custom patterns can use any names.
     
.. list-table:: indicators
   :widths: 10 90
   :header-rows: 1
   
   * - Name
     - Description  
   * - `re`_ 
     - allows to specify regular expression to use for match variable
   * - `WORD`_ 
     - matches single word
   * - `PHRASE`_ 
     - matches a collection of words separated by single space character
   * - `ORPHRASE`_ 
     - matches phrase or single word
   * - `_line_`_ 
     - matches any line
   * - `ROW`_ 
     - matches text-table data with space as column delimiter
   * - `DIGIT`_ 
     - matches single number
   * - `IP`_ 
     - matches IPv4 address
   * - `PREFIX`_ 
     - matches IPv4 prefix
   * - `IPV6`_ 
     - matches IPv6 address
   * - `PREFIXV6`_ 
     - matches IPv6 prefix
   * - `MAC`_ 
     - matches MAC address     
     
re
------------------------------------------------------------------------------
``{{ name | re("regex_value") }}``

* regex_value - regular expression value, this value either substituted with re pattern or used as is. 

Regular expression value searched using below sequence.

    1. Template variables checked to to find variable names equal to regex_value
    2. Built-in regex patterns searched using regex_value
    3. regex_value used as is 
    
**Example**

Template::

    <vars>
    # template variable with custom regular expression:
    GE_INTF = "GigabitEthernet\S+"
    </vars>
    
    <input load="text">
    Protocol  Address     Age (min)  Hardware Addr   Type   Interface
    Internet  10.12.13.1        98   0950.5785.5cd1  ARPA   FastEthernet2.13
    Internet  10.12.13.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
    Internet  10.12.13.4       198   0950.5C8A.5c41  ARPA   GigabitEthernet2.17
    </input>
    
    <group>
    Internet  {{ ip | re("IP")}}  {{ age | re("\d+") }}   {{ mac }}  ARPA   {{ interface | re("GE_INTF") }}
    </group>
    
Results::

    [
        [
            {
                "age": "131",
                "interface": "GigabitEthernet2.13",
                "ip": "10.12.13.3",
                "mac": "0150.7685.14d5"
            },
            {
                "age": "198",
                "interface": "GigabitEthernet2.17",
                "ip": "10.12.13.4",
                "mac": "0950.5C8A.5c41"
            }
        ]
    ]

In this example group line:

 ``Internet  {{ ip | re("IP")}}  {{ age | re("\d+") }}   {{ mac }}  ARPA   {{ interface | re("GE_INTF") }}`` 
 
transformed into this regular expression:
 
``'\nInternet\ +(?P<ip>(?:(?:[0-9]{1,3}\.){3}[0-9]{1,3}))\ +(?P<age>(?:\d+))\ +(?P<mac>(?:\S+))\ +ARPA\ +(?P<interface>(?:GigabitEthernet\S+))[\t ]*(?=\n)'``

using built-in IP pattern for *ip*, ``\d+`` inline regex for *age* and custom ``GE_INTF`` pattern for *interface* match variable. 


.. warning:: inline definition of regular expressions delimited by ``|`` pipe character is not supported due to TTP uses pipe to separate match variable arguments. In other words, this ``{{ name | re("re1|re2|re3") }}`` is not supported. Workaround - reference template variable with required regular expression.

**Example**

Using template variable with multiple regular expression delimited by ``|`` pipe character

Template::

    <input load="text">
    Protocol  Address     Age (min)  Hardware Addr   Type   Interface
    Internet  10.12.13.1        98   0950.5785.5cd1  ARPA   FastEthernet2.13
    Internet  10.12.13.2        98   0950.5785.5cd2  ARPA   Loopback0
    Internet  10.12.13.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
    Internet  10.12.13.4       198   0950.5C8A.5c41  ARPA   GigabitEthernet2.17
    </input>
    
    <vars>
    INTF_RE = r"GigabitEthernet\\S+|Fast\\S+"
    </vars>
    
    <group name="arp_test">
    Internet  {{ ip | re("IP")}}  {{ age | re(r"\\d+") }}   {{ mac }}  ARPA   {{ interface | re("INTF_RE") }}
    </group>

Result::

    [[{'arp_test': [{'age': '98',
                     'interface': 'FastEthernet2.13',
                     'ip': '10.12.13.1',
                     'mac': '0950.5785.5cd1'},
                    {'age': '131',
                     'interface': 'GigabitEthernet2.13',
                     'ip': '10.12.13.3',
                     'mac': '0150.7685.14d5'},
                    {'age': '198',
                     'interface': 'GigabitEthernet2.17',
                     'ip': '10.12.13.4',
                     'mac': '0950.5C8A.5c41'}]}]]

``INTF_RE`` - variable contains several regular expression separate by ``|`` character

Another technique to associate match variable with multiple regular expressions, is to reference ``re("regex_value")`` several times. Sample template::

    <input load="text">
    Protocol  Address     Age (min)  Hardware Addr   Type   Interface
    Internet  10.12.13.1        98   0950.5785.5cd1  ARPA   FastEthernet2.13
    Internet  10.12.13.2        98   0950.5785.5cd2  ARPA   Loopback0
    Internet  10.12.13.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
    Internet  10.12.13.4       198   0950.5C8A.5c41  ARPA   GigabitEthernet2.17
    </input>
    
    <group name="arp_test">
    Internet  {{ ip }}  {{ age }}   {{ mac }}  ARPA   {{ interface | re(r"GigabitEthernet\\S+") | re(r"Fast\\S+") }}
    </group>

Results::

    [[{'arp_test': [{'age': '98',
                     'interface': 'FastEthernet2.13',
                     'ip': '10.12.13.1',
                     'mac': '0950.5785.5cd1'},
                    {'age': '131',
                     'interface': 'GigabitEthernet2.13',
                     'ip': '10.12.13.3',
                     'mac': '0150.7685.14d5'},
                    {'age': '198',
                     'interface': 'GigabitEthernet2.17',
                     'ip': '10.12.13.4',
                     'mac': '0950.5C8A.5c41'}]}]]

WORD
------------------------------------------------------------------------------
``{{ name | WORD }}``

WORD pattern helps to match single word - collection of characters excluding any space, tab or new line characters.

PHRASE
------------------------------------------------------------------------------
``{{ name | PHRASE }}``

This pattern matches any phrase - collection of words separated by **single** space character, such as "word1 word2 word3".

ORPHRASE
------------------------------------------------------------------------------
``{{ name | ORPHRASE }}``

In many cases data that needs to be extracted can be either a single word or a phrase, the most prominent example - various descriptions, such as interface descriptions, BGP peers descriptions etc. ORPHRASE allows to match and extract such a data.

**Example**

Template::

    <input load="text">
    interface Loopback0
     description Router id - OSPF, BGP
     ip address 192.168.0.113/24
    !
    interface Vlan778
     description CPE_Acces_Vlan
     ip address 2002::fd37/124
    !
    </input>
    
    <group>
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     ip address {{ ip }}/{{ mask }}
    </group>

Result::

    [
        [
            {
                "description": "Router id - OSPF, BGP",
                "interface": "Loopback0",
                "ip": "192.168.0.113",
                "mask": "24"
            },
            {
                "description": "CPE_Acces_Vlan",
                "interface": "Vlan778",
                "ip": "2002::fd37",
                "mask": "124"
            }
        ]
    ]

_line_
------------------------------------------------------------------------------
``{{ name | _line_ }}``

Matches any line within text data, check :ref:`Match Variables/Indicators:_line_` indicators section for more details.

ROW
------------------------------------------------------------------------------
``{{ name | ROW }}``

Helps to match row-like lines of text - words separated by a number of spaces.

**Example**

Template::

    <input load="text">
    Pesaro# show ip vrf detail Customer_A
    VRF Customer_A; default RD 100:101
      Interfaces:
        Loopback101      Loopback111      Vlan707    
    </input>
    
    <group name="vrfs">
    VRF {{ vrf }}; default RD {{ rd }}
    <group name="interfaces">
      Interfaces: {{ _start_ }}
        {{ intf_list | ROW }} 
    </group>
    </group>
    
Results::

    [
        {
            "vrfs": {
                "interfaces": {
                    "intf_list": "Loopback101      Loopback111      Vlan707"
                },
                "rd": "100:101",
                "vrf": "Customer_A"
            }
        }
    ]

Line "    Loopback101      Loopback111      Vlan707" was matched by ``ROW`` regular expression.

DIGIT
------------------------------------------------------------------------------
``{{ name | DIGIT }}``

Matches any single number, such as 1 or 123 or 0012300.

IP
------------------------------------------------------------------------------
``{{ name | IP }}``

This regex pattern can match IPv4 addresses, for instance *192.168.134.251*. But this pattern does not perform IP address validation, as a result this text also will be matched *321.751.123.999*. Condition check function :ref:`Match Variables/Functions:is_ip` can be used to validate IP addresses.

PREFIX
------------------------------------------------------------------------------
``{{ name | PREFIX }}``

Matches IPv4 prefix, such as *192.168.0.1/24*, but also will match *999.321.192.6/99*, make sure to use :ref:`Match Variables/Functions:is_ip` function to validate prefixes if required.

IPV6
------------------------------------------------------------------------------
``{{ name | IPV6 }}``

Performs match on IPv6 addresses, for example *2001:ABC0::FE31* address, but will also match incorrect IPv6 *2002::fd37::91* address as well, make sure to use :ref:`Match Variables/Functions:is_ip` function to validate IPv6 addresses.

PREFIXV6
------------------------------------------------------------------------------
``{{ name | PREFIXV6 }}``

Matches IPv6 prefix, such as *2001:ABC0::FE31/64*, but will also match *2002::fd37::91/124*, make sure to use :ref:`Match Variables/Functions:is_ip` function to validate prefixes if required.

MAC
------------------------------------------------------------------------------
``{{ name | MAC }}``

MAC addresses will be matched by this regular expression pattern, such as:

* aa:bb:cc:dd:11:33
* aa.bb.cc.dd.11.33
* aabb:ccdd:1133
* aabb.ccdd.1133