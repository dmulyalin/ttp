[![Downloads](https://pepy.tech/badge/ttp)](https://pepy.tech/project/ttp)
[![PyPI versions](https://img.shields.io/pypi/pyversions/ttp.svg)](https://pypi.python.org/pypi/ttp/)
[![Documentation status](https://readthedocs.org/projects/ttp/badge/?version=latest)](http://ttp.readthedocs.io/?badge=latest)

# Template Text Parser

TTP is a Python library for semi-structured text parsing using templates.

## Why?

Every time questions arise on how many devices has blob X configured or how many interface has QoS policy applied or to find IP overlaps in the network etc., etc., for those who write custom scripts to answer these questions, spending hours putting fancy regexes together and learning how to use specialized libraries to prepare, parse and process text data to transform it in a format that they can make use of - have a look at TTP, it can help with most of it.

## How?

Regexes, regexes everywhere... but dynamically formed out of TTP templates with added capabilities to streamline process of getting desired outcome from raw text data.

## What?

In essence TTP can help to:
  - Prepare, sort and load text data for parsing
  - Parse text using regexes dynamically derived from templates
  - Process matches on the fly using broad set of built-in or custom convenience functions
  - Combine match results in a structure with arbitrary hierarchy
  - Transform results in desired format to ease consumption by humans or machines
  - Return results to various destinations for storage or further processing

Reference [documentation](https://ttp.readthedocs.io) for more information.

## Example

```python
from ttp import ttp

data_to_parse = """
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

ttp_template = """
interface {{ interface }}
 ip address {{ ip }}/{{ mask }}
 description {{ description }}
 ip vrf {{ vrf }}
"""

parser = ttp(data=data_to_parse, template=ttp_template)
parser.parse()
print(parser.result(format='json')[0])

[
    [
        {
            "description": "Router-id-loopback",
            "interface": "Loopback0",
            "ip": "192.168.0.113",
            "mask": "24"
        },
        {
            "description": "CPE_Acces_Vlan",
            "interface": "Vlan778",
            "ip": "2002::fd37",
            "mask": "124",
            "vrf": "CPE1"
        }
    ]
]
```

# Contributions
Feel free to submit an issue, to report a bug or ask a question, feature requests are welcomed or [buy](https://paypal.me/dmulyalin) Author a coffee