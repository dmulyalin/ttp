Dynamic path with path formatters
=================================				  
	
Dynamic path with path formatters is also supported. In example below child for *interfaces* will be a list.

**Example**

Data::

    interface Port-Chanel11
      description Storage
    !
    interface Loopback0
      description RID
      ip address 10.0.0.3/24
    !
    interface Vlan777
      description Management
      ip address 192.168.0.1/24
      vrf MGMT
	  
Template::

    <group name="interfaces*.{{ interface }}">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>
	  
Result::

    [
        {
            "interfaces": [
                {
                    "Loopback0": {
                        "description": "RID",
                        "ip": "10.0.0.3",
                        "mask": "24"
                    },
                    "Port-Chanel11": {
                        "description": "Storage"
                    },
                    "Vlan777": {
                        "description": "Management",
                        "ip": "192.168.0.1",
                        "mask": "24",
                        "vrf": "MGMT"
                    }
                }
            ]
        }
    ]