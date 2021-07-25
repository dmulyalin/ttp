import sys

sys.path.insert(0, "../..")
import pprint

import logging

logging.basicConfig(level=logging.DEBUG)

from ttp import ttp


def test_group_same_null_path_for_several_groups():
    data = """
vrf xyz
 address-family ipv4 unicast
  import route-target
   65000:3507
   65000:3511
   65000:5453
   65000:5535
  !
  export route-target
   65000:5453
   65000:5535
  !
 !
!    
    """
    template = """
<group name="vrfs">
vrf {{name}}
  <group name="_">
  import route-target {{ _start_ }}
   {{ import | to_list | joinmatches }}
  </group>
  !
  <group name="_">
  export route-target {{ _start_ }}
   {{ export | to_list | joinmatches }}
  </group>
</group>
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [
        [
            {
                "vrfs": {
                    "export": ["65000:5453", "65000:5535"],
                    "import": ["65000:3507", "65000:3511", "65000:5453", "65000:5535"],
                    "name": "xyz",
                }
            }
        ]
    ]


# test_group_same_null_path_for_several_groups()
