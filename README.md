[![Downloads](https://pepy.tech/badge/ttp)](https://pepy.tech/project/ttp)
[![PyPI versions](https://img.shields.io/pypi/pyversions/ttp.svg)](https://pypi.python.org/pypi/ttp/)
[![Documentation status](https://readthedocs.org/projects/ttp/badge/?version=latest)](http://ttp.readthedocs.io/?badge=latest)

# Template Text Parser

TTP is a Python library for semi-structured text parsing using templates.

## Why?

To save ones time on transforming raw text into structured data and beyond.

## How?

Regexes, regexes everywhere... but, dynamically formed out of TTP templates with added capabilities to simplify the  process of getting desired outcome.

## What?

In essence TTP can help to:
  - Prepare, sort and load text data for parsing
  - Parse text using regexes dynamically derived out of templates
  - Process matches on the fly using broad set of built-in or custom functions
  - Combine match results in a structure with arbitrary hierarchy
  - Transform results in desired format to ease consumption by humans or machines
  - Return results to various destinations for storage or further processing

Reference [documentation](https://ttp.readthedocs.io) for more information.

## Example - as simple as it can be

Simple interfaces configuration parsing example

<details><summary>Code</summary>

```python
from ttp import ttp
import pprint

data = """
interface Loopback0
 description Router-id-loopback
 ip address 192.168.0.113/24
!
interface Vlan778
 description CPE_Acces_Vlan
 ip address 2002::fd37/124
 ip vrf CPE1
!
"""

template = """
interface {{ interface }}
 ip address {{ ip }}/{{ mask }}
 description {{ description }}
 ip vrf {{ vrf }}
"""

parser = ttp(data, template)
parser.parse()
pprint.pprint(parser.result(), width=100)

# prints:
# [[[{'description': 'Router-id-loopback',
#     'interface': 'Loopback0',
#     'ip': '192.168.0.113',
#     'mask': '24'},
#    {'description': 'CPE_Acces_Vlan',
#     'interface': 'Vlan778',
#     'ip': '2002::fd37',
#     'mask': '124',
#     'vrf': 'CPE1'}]]]
```
</details>

## Example - a bit more complicated

For this example lets say we want to parse BGP peerings output, but combine state with configuration data, at the end we want to get pretty looking text table printed to screen.

<details><summary>Code</summary>

```python
template="""
<doc>
This template first parses "show bgp vrf CUST-1 vpnv4 unicast summary" commands
output, forming results for "bgp_state" dictionary, where peer ip is a key.

Following that, "show run | section bgp" output parsed by group "bgp_cfg". That
group uses nested groups to form results structure, including absolute path 
"/bgp_peers*" with path formatter to produce a list of peers under "bgp_peers"
path. 

For each peer "hostname" and local bgp "local_asn" added using previous matches. 
Additionally, group lookup function used to lookup peer state from "bgp_state" 
group results, adding found data to peer results.

Finally, "bgp_peers" section of results passed via "tabulate_outputter" to
from and print this table to terminal:

hostname           local_asn    vrf_name    peer_ip    peer_asn    uptime    state    description    afi    rpl_in           rpl_out
-----------------  -----------  ----------  ---------  ----------  --------  -------  -------------  -----  ---------------  ---------------
ucs-core-switch-1  65100        CUST-1      192.0.2.1  65101       00:12:33  300      peer-1         ipv4   RPL-1-IMPORT-v4  RPL-1-EXPORT-V4
ucs-core-switch-1  65100        CUST-1      192.0.2.2  65102       03:55:01  idle     peer-2         ipv4   RPL-2-IMPORT-V6  RPL-2-EXPORT-V6

Run this script with "python filename.py"
</doc>

<vars>
hostname="gethostname"
chain_1 = [
    "set('vrf_name')",
    "lookup('peer_ip', group='bgp_state', update=True)"
]
</vars>

<group name="bgp_state.{{ peer }}" input="bgp_state">
{{ peer }}  4 65101      20      21       43    0    0 {{ uptime }} {{ state }}
</group>

<group name="bgp_cfg" input="bgp_config">
router bgp {{ asn | record(asn) }}
  <group name="vrfs.{{ vrf_name }}" record="vrf_name">
  vrf {{ vrf_name }}
    <group name="/bgp_peers*" chain="chain_1">
    neighbor {{ peer_ip }}
      {{ local_asn | set(asn) }}
      {{ hostname | set(hostname) }}
      remote-as {{ peer_asn }}
      description {{ description }}
      address-family {{ afi }} unicast
        route-map {{ rpl_in }} in
        route-map {{ rpl_out }} out
	</group>
  </group>
</group>

<output 
name="tabulate_outputter"
format="tabulate" 
path="bgp_peers" 
returner="terminal"
headers="hostname, local_asn, vrf_name, peer_ip, peer_asn, uptime, state, description, afi, rpl_in, rpl_out"
/>
"""

data_bgp_state = """
ucs-core-switch-1#show bgp vrf CUST-1 vpnv4 unicast summary
Neighbor   V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
192.0.2.1  4 65101      32      54       42    0    0 00:12:33       300
192.0.2.2  4 65101      11      45       99    0    0 03:55:01       idle
"""

data_bgp_config = """
ucs-core-switch-1#show run | section bgp
router bgp 65100
  vrf CUST-1
    neighbor 192.0.2.1
      remote-as 65101
      description peer-1
      address-family ipv4 unicast
        route-map RPL-1-IMPORT-v4 in
        route-map RPL-1-EXPORT-V4 out
    neighbor 192.0.2.2
      remote-as 65102
      description peer-2
      address-family ipv4 unicast
        route-map RPL-2-IMPORT-V6 in
        route-map RPL-2-EXPORT-V6 out
"""

from ttp import ttp

parser = ttp()
parser.add_template(template)
parser.add_input(data=data_bgp_state, input_name="bgp_state")
parser.add_input(data=data_bgp_config, input_name="bgp_config")
parser.parse()
```
</details>

# Contributions
Feel free to submit an issue or report a bug or ask a question, feature requests are welcomed. 

TTP [Networktocode Slack channel](https://networktocode.slack.com/archives/C018HMJQECB)

[buy](https://paypal.me/dmulyalin) Author a coffee