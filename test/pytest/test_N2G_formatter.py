import sys

sys.path.insert(0, "../..")
import pprint
import pytest

import logging

logging.basicConfig(level="INFO")

from ttp import ttp

try:
    from N2G import yed_diagram

    HAS_N2G = True
except ImportError:
    HAS_N2G = False

skip_if_no_n2g = pytest.mark.skipif(
    HAS_N2G == False, reason="Failed to import N2G module"
)


@skip_if_no_n2g
def test_n2g_formatter():
    template = """
<input load="text">
switch-1#show cdp neighbors detail 
-------------------------
Device ID: switch-2
Entry address(es): 
  IP address: 10.2.2.2
Platform: cisco WS-C6509,  Capabilities: Router Switch IGMP 
Interface: GigabitEthernet4/6,  Port ID (outgoing port): GigabitEthernet1/5

-------------------------
Device ID: switch-3
Entry address(es): 
  IP address: 10.3.3.3
Platform: cisco WS-C3560-48TS,  Capabilities: Switch IGMP 
Interface: GigabitEthernet1/1,  Port ID (outgoing port): GigabitEthernet0/1

-------------------------
Device ID: switch-4
Entry address(es): 
  IP address: 10.4.4.4
Platform: cisco WS-C3560-48TS,  Capabilities: Switch IGMP 
Interface: GigabitEthernet1/2,  Port ID (outgoing port): GigabitEthernet0/10
</input>

<input load="text">
switch-2#show cdp neighbors detail 
-------------------------
Device ID: switch-1
Entry address(es): 
  IP address: 10.1.1.1
Platform: cisco WS-C6509,  Capabilities: Router Switch IGMP 
Interface: GigabitEthernet1/5,  Port ID (outgoing port): GigabitEthernet4/6
</input>

<vars>
hostname='gethostname' 
IfsNormalize = {
    'Ge':['^GigabitEthernet']
} 
</vars>

<group name="cdp*" expand="">
Device ID: {{ target.id }}
  IP address: {{ target.top_label }}
Platform: {{ target.bottom_label | ORPHRASE }},  Capabilities: {{ ignore | ORPHRASE }} 
Interface: {{ src_label | resuball(IfsNormalize) }},  Port ID (outgoing port): {{ trgt_label | ORPHRASE | resuball(IfsNormalize) }}
{{ source | set("hostname") }}
</group>

<output format="n2g">
path = "cdp"
module = "yed"
node_duplicates = "update"
method = "from_list"
</output>
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # print(res)
    assert res == [
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">\n    \n    <key attr.name="Description" attr.type="string" for="graph" id="d0" />\n    <key for="port" id="d1" yfiles.type="portgraphics" />\n    <key for="port" id="d2" yfiles.type="portgeometry" />\n    <key for="port" id="d3" yfiles.type="portuserdata" />\n    <key attr.name="url" attr.type="string" for="node" id="d4" />\n    <key attr.name="description" attr.type="string" for="node" id="d5" />\n    <key for="node" id="d6" yfiles.type="nodegraphics" />\n    <key for="graphml" id="d7" yfiles.type="resources" />\n    <key attr.name="url" attr.type="string" for="edge" id="d8" />\n    <key attr.name="description" attr.type="string" for="edge" id="d9" />\n    <key for="edge" id="d10" yfiles.type="edgegraphics" />\n    <key attr.name="nmetadata" attr.type="string" for="node" id="d11">\n        <default />\n    </key>\n    <key attr.name="emetadata" attr.type="string" for="edge" id="d12">\n        <default />\n    </key>\n    <key attr.name="gmetadata" attr.type="string" for="graph" id="d13">\n        <default />\n    </key>\n    <graph edgedefault="directed" id="G">\n    \n    <node id="switch-1">\n      <data key="d6">\n        <y:ShapeNode>\n          <y:Geometry height="60" width="120" x="200" y="150" />\n          <y:Fill color="#FFFFFF" transparent="false" />\n          <y:BorderStyle color="#000000" raised="false" type="line" width="3.0" />\n          <y:Shape type="roundrectangle" />\n        <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="c" textColor="#000000" verticalTextPosition="bottom" visible="true" width="70">switch-1</y:NodeLabel><y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="70">10.1.1.1</y:NodeLabel></y:ShapeNode>\n      </data>\n    <data key="d11">{"id": "switch-1"}</data></node><node id="switch-2">\n      <data key="d6">\n        <y:ShapeNode>\n          <y:Geometry height="60" width="120" x="200" y="150" />\n          <y:Fill color="#FFFFFF" transparent="false" />\n          <y:BorderStyle color="#000000" raised="false" type="line" width="3.0" />\n          <y:Shape type="roundrectangle" />\n        <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="c" textColor="#000000" verticalTextPosition="bottom" visible="true" width="70">switch-2</y:NodeLabel><y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="70">10.2.2.2</y:NodeLabel></y:ShapeNode>\n      </data>\n    <data key="d11">{"id": "switch-2"}</data></node><edge id="0d1e25a0122c562fa9bc515040ed5607" source="switch-1" target="switch-2">\n      <data key="d10">\n        <y:PolyLineEdge>\n         <y:LineStyle color="#000000" type="line" width="1.0" />\n         <y:Arrows source="none" target="none" />\n         <y:BendStyle smoothed="false" />\n        <y:EdgeLabel alignment="center" backgroundColor="#FFFFFF" configuration="AutoFlippingLabel" distance="2.0" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="free" modelPosition="anywhere" preferredPlacement="target_on_edge" ratio="0.5" textColor="#000000" upX="-1.0" upY="-6E-17" verticalTextPosition="bottom" visible="true" width="32">Ge4/6<y:PreferredPlacementDescriptor angle="0.0" angleOffsetOnRightSide="0" angleReference="relative_to_edge_flow" angleRotationOnRightSide="co" distance="-1.0" placement="source" side="on_edge" sideReference="relative_to_edge_flow" />\n    </y:EdgeLabel><y:EdgeLabel alignment="center" backgroundColor="#FFFFFF" configuration="AutoFlippingLabel" distance="2.0" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="free" modelPosition="anywhere" preferredPlacement="target_on_edge" ratio="0.5" textColor="#000000" upX="-1.0" upY="-6E-17" verticalTextPosition="bottom" visible="true" width="32">Ge1/5<y:PreferredPlacementDescriptor angle="0.0" angleOffsetOnRightSide="0" angleReference="relative_to_edge_flow" angleRotationOnRightSide="co" distance="-1.0" placement="target" side="on_edge" sideReference="relative_to_edge_flow" />\n    </y:EdgeLabel></y:PolyLineEdge>\n      </data>\n    <data key="d12">{"sid": "switch-1", "tid": "switch-2", "id": "0d1e25a0122c562fa9bc515040ed5607"}</data></edge><node id="switch-3">\n      <data key="d6">\n        <y:ShapeNode>\n          <y:Geometry height="60" width="120" x="200" y="150" />\n          <y:Fill color="#FFFFFF" transparent="false" />\n          <y:BorderStyle color="#000000" raised="false" type="line" width="3.0" />\n          <y:Shape type="roundrectangle" />\n        <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="c" textColor="#000000" verticalTextPosition="bottom" visible="true" width="70">switch-3</y:NodeLabel><y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="70">10.3.3.3</y:NodeLabel></y:ShapeNode>\n      </data>\n    <data key="d11">{"id": "switch-3"}</data></node><edge id="6c9855a7f657e1b36f49ff33306a96fa" source="switch-1" target="switch-3">\n      <data key="d10">\n        <y:PolyLineEdge>\n         <y:LineStyle color="#000000" type="line" width="1.0" />\n         <y:Arrows source="none" target="none" />\n         <y:BendStyle smoothed="false" />\n        <y:EdgeLabel alignment="center" backgroundColor="#FFFFFF" configuration="AutoFlippingLabel" distance="2.0" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="free" modelPosition="anywhere" preferredPlacement="target_on_edge" ratio="0.5" textColor="#000000" upX="-1.0" upY="-6E-17" verticalTextPosition="bottom" visible="true" width="32">Ge1/1<y:PreferredPlacementDescriptor angle="0.0" angleOffsetOnRightSide="0" angleReference="relative_to_edge_flow" angleRotationOnRightSide="co" distance="-1.0" placement="source" side="on_edge" sideReference="relative_to_edge_flow" />\n    </y:EdgeLabel><y:EdgeLabel alignment="center" backgroundColor="#FFFFFF" configuration="AutoFlippingLabel" distance="2.0" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="free" modelPosition="anywhere" preferredPlacement="target_on_edge" ratio="0.5" textColor="#000000" upX="-1.0" upY="-6E-17" verticalTextPosition="bottom" visible="true" width="32">Ge0/1<y:PreferredPlacementDescriptor angle="0.0" angleOffsetOnRightSide="0" angleReference="relative_to_edge_flow" angleRotationOnRightSide="co" distance="-1.0" placement="target" side="on_edge" sideReference="relative_to_edge_flow" />\n    </y:EdgeLabel></y:PolyLineEdge>\n      </data>\n    <data key="d12">{"sid": "switch-1", "tid": "switch-3", "id": "6c9855a7f657e1b36f49ff33306a96fa"}</data></edge><node id="switch-4">\n      <data key="d6">\n        <y:ShapeNode>\n          <y:Geometry height="60" width="120" x="200" y="150" />\n          <y:Fill color="#FFFFFF" transparent="false" />\n          <y:BorderStyle color="#000000" raised="false" type="line" width="3.0" />\n          <y:Shape type="roundrectangle" />\n        <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="c" textColor="#000000" verticalTextPosition="bottom" visible="true" width="70">switch-4</y:NodeLabel><y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="70">10.4.4.4</y:NodeLabel></y:ShapeNode>\n      </data>\n    <data key="d11">{"id": "switch-4"}</data></node><edge id="1a55473cf64b1d33fe9a470093808d0d" source="switch-1" target="switch-4">\n      <data key="d10">\n        <y:PolyLineEdge>\n         <y:LineStyle color="#000000" type="line" width="1.0" />\n         <y:Arrows source="none" target="none" />\n         <y:BendStyle smoothed="false" />\n        <y:EdgeLabel alignment="center" backgroundColor="#FFFFFF" configuration="AutoFlippingLabel" distance="2.0" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="free" modelPosition="anywhere" preferredPlacement="target_on_edge" ratio="0.5" textColor="#000000" upX="-1.0" upY="-6E-17" verticalTextPosition="bottom" visible="true" width="32">Ge1/2<y:PreferredPlacementDescriptor angle="0.0" angleOffsetOnRightSide="0" angleReference="relative_to_edge_flow" angleRotationOnRightSide="co" distance="-1.0" placement="source" side="on_edge" sideReference="relative_to_edge_flow" />\n    </y:EdgeLabel><y:EdgeLabel alignment="center" backgroundColor="#FFFFFF" configuration="AutoFlippingLabel" distance="2.0" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasLineColor="false" height="18" horizontalTextPosition="center" iconTextGap="4" modelName="free" modelPosition="anywhere" preferredPlacement="target_on_edge" ratio="0.5" textColor="#000000" upX="-1.0" upY="-6E-17" verticalTextPosition="bottom" visible="true" width="32">Ge0/10<y:PreferredPlacementDescriptor angle="0.0" angleOffsetOnRightSide="0" angleReference="relative_to_edge_flow" angleRotationOnRightSide="co" distance="-1.0" placement="target" side="on_edge" sideReference="relative_to_edge_flow" />\n    </y:EdgeLabel></y:PolyLineEdge>\n      </data>\n    <data key="d12">{"sid": "switch-1", "tid": "switch-4", "id": "1a55473cf64b1d33fe9a470093808d0d"}</data></edge></graph>\n    <data key="d7">\n        <y:Resources>\n        </y:Resources>\n    </data>\n    </graphml>'
    ]


# test_n2g_formatter()
