from ttp import ttp
import json

template="""
<template name="template-1">
<input load="text">
interface Vlan778
 ip address 2002:fd37::91/124
</input>
<group name="interfaces-1">
interface {{ interface }}
 ip address {{ ip }}
</group>
</template>

<template name="template-2">
<input load="text">
interface Vlan778
 description V6 Management vlan
</input>
<group name="interfaces-2">
interface {{ interface }}
 description {{ description | ORPHRASE }}
</group>
</template>
"""

parser=ttp(template=template)
parser.parse()
results = parser.result(structure="dictionary")
print(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')))
