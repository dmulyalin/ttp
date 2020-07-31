Absolute path
=============

By default TTP treats name attribute as a relative path, relative to parent groups, expanding path to full (absolute) path for each and every group. 

For instance for below template::

    <input load="text">
    router bgp 65123
     !
     address-family ipv4 vrf VRF1
      neighbor 10.100.100.212 route-policy DENY_ALL in
      neighbor 10.227.147.122 route-policy DENY_ALL in
     exit-address-family
     !
     address-family ipv4 vrf VRF2
      neighbor 10.61.254.67 route-policy DENY_ALL in
      neighbor 10.61.254.68 route-policy DENY_ALL in
     exit-address-family
    </input>

    <group name="bgp_config">
    router bgp {{ bgp_asn }}
    
    <group name="VRFs">
     address-family {{ afi }} vrf {{ vrf }}
      <group name="neighbors**.{{ neighbor }}**" method="table">
      neighbor {{ neighbor }} route-policy {{ ingreass_rpl }} in
      </group>
    </group>
    
    </group>
	
Paths for child groups will be expanded to the list of absolute path items:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Name attribute
     - Path
   * - bgp_config 
     - [bgp_config]
   * - VRFs
     - [bgp_config, VRFs]
   * - neighbors**.{{ neighbor }}**
     - [bgp_config, VRFs, neighbors, {{ neighbor }}]
	 
Results structure for above template will look like::

    [
        [
            {
                "bgp_config": {
                    "VRFs": [
                        {
                            "afi": "ipv4",
                            "neighbors": {
                                "10.100.100.212": {
                                    "ingreass_rpl": "DENY_ALL"
                                },
                                "10.227.147.122": {
                                    "ingreass_rpl": "DENY_ALL"
                                }
                            },
                            "vrf": "VRF1"
                        },
                        {
                            "afi": "ipv4",
                            "neighbors": {
                                "10.61.254.67": {
                                    "ingreass_rpl": "DENY_ALL"
                                },
                                "10.61.254.68": {
                                    "ingreass_rpl": "DENY_ALL"
                                }
                            },
                            "vrf": "VRF2"
                        }
                    ],
                    "bgp_asn": "65123"
                }
            }
        ]
    ]

However, sometimes it might be beneficial to have a capability to flatten hierarchical structure by specifying absolute path for child groups.

To instruct TTP to treat name attribute as an absolute path, it should be prepended (started) with forward slash `/` character.

Example Template::

    <input load="text">
    router bgp 65123
     !
     address-family ipv4 vrf VRF1
      neighbor 10.100.100.212 route-policy DENY_ALL in
      neighbor 10.227.147.122 route-policy DENY_ALL in
     exit-address-family
     !
     address-family ipv4 vrf VRF2
      neighbor 10.61.254.67 route-policy DENY_ALL in
      neighbor 10.61.254.68 route-policy DENY_ALL in
     exit-address-family
    </input>
    
    <group name="bgp_config">
    router bgp {{ bgp_asn }}
    
    <group name="VRFs">
     address-family {{ afi }} vrf {{ vrf }}
      <group name="/neighbors**.{{ neighbor }}**" method="table">
      neighbor {{ neighbor }} route-policy {{ ingreass_rpl }} in
      </group>
    </group>
    
    </group>
	
In above template, note the name of this child group - `name="/neighbors**.{{ neighbor }}**"` - it is prepended with forward slash character and treated as absolute path. Result structure for above template will be::

    [
        [
            {
                "bgp_config": {
                    "VRFs": [
                        {
                            "afi": "ipv4",
                            "vrf": "VRF1"
                        },
                        {
                            "afi": "ipv4",
                            "vrf": "VRF2"
                        }
                    ],
                    "bgp_asn": "65123"
                },
                "neighbors": {
                    "10.100.100.212": {
                        "ingreass_rpl": "DENY_ALL"
                    },
                    "10.227.147.122": {
                        "ingreass_rpl": "DENY_ALL"
                    },
                    "10.61.254.67": {
                        "ingreass_rpl": "DENY_ALL"
                    },
                    "10.61.254.68": {
                        "ingreass_rpl": "DENY_ALL"
                    }
                }
            }
        ]
    ]

This is because path attribute will not be expanded for `neighbors` child group and will be treated as is, effectively shortening the hierarchy of results structure and flattening it.