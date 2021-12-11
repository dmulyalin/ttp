Dynamic Path
============

Above are examples of static path, where all the path items are known and predefined beforehand, however, ttp supports dynamic path formation using match variable results for certain match variable names, i.e we have match variable name set to *interface* and correspondent match result would be Gi0/1, it is possible to use Gi0/1 as a path item.

Search for dynamic path item value happens using below sequence:

* *First* - group match results searched for path item value,
* *Second* - upper group results cache (latest values) used,
* *Third* - template variables searched for path item value,
* *Last* - group results discarded as invalid

Dynamic path items specified in group *name* attribute using "*{{ item_name }}*" format, there "*{{ item_name }}*" dynamically replaced with value found using above sequence.

**Example-1**

In this example interface variable match values will be used to substitute {{ interface }} dynamic path items.

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

    <group name="interfaces.{{ interface }}">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>

Result::

    [
        {
            "interfaces": {
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
        }
    ]

Because each path item is a string, and each item produced by spilling name attributes using '.' dot character, it is possible to produce dynamic path there portions of path item will be dynamically substituted.


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

    <group name="interfaces.cool_{{ interface }}_interface">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>

Result::

    [
        {
            "interfaces": {
                "cool_Loopback0_interface": {
                    "description": "RID",
                    "ip": "10.0.0.3",
                    "mask": "24"
                },
                "cool_Port-Chanel11_interface": {
                    "description": "Storage"
                },
                "cool_Vlan777_interface": {
                    "description": "Management",
                    "ip": "192.168.0.1",
                    "mask": "24",
                    "vrf": "MGMT"
                }
            }
        }
    ]

.. note::

  Substitution of dynamic path items happens using re.sub method without the limit set on the count of such a substitutions, e.g. if path item "cool_{{ interface }}_interface_{{ interface }}" and if interface value is "Gi0/1" resulted path item will be "cool_Gi0/1_interface_Gi0/1"

Nested hierarchies also supported with dynamic path, as if no variable found in the group match results ttp will try to find variable in the dynamic path cache or template variables.

**Example-3**

Data::

    ucs-core-switch-1#show run | section bgp
    router bgp 65100
      vrf CUST-1
        neighbor 59.100.71.193
          remote-as 65101
          description peer-1
          address-family ipv4 unicast
            route-map RPL-1-IMPORT-v4 in
            route-map RPL-1-EXPORT-V4 out
          address-family ipv6 unicast
            route-map RPL-1-IMPORT-V6 in
            route-map RPL-1-EXPORT-V6 out
        neighbor 59.100.71.209
          remote-as 65102
          description peer-2
          address-family ipv4 unicast
            route-map AAPTVRF-LB-BGP-IMPORT-V4 in
            route-map AAPTVRF-LB-BGP-EXPORT-V4 out

Template::

    <vars>
    hostname = "gethostname"
    </vars>

    <group name="{{ hostname }}.router.bgp.BGP_AS_{{ asn }}">
    router bgp {{ asn }}
      <group name="vrfs.{{ vrf_name }}">
      vrf {{ vrf_name }}
        <group name="peers.{{ peer_ip }}">
        neighbor {{ peer_ip }}
          remote-as {{ peer_asn }}
          description {{ peer_description }}
    	  <group name="afi.{{ afi }}.unicast">
          address-family {{ afi }} unicast
            route-map {{ rpl_in }} in
            route-map {{ rpl_out }} out
    	  </group>
    	</group>
       </group>
    </group>

Result::

    - ucs-core-switch-1:
        router:
          bgp:
            BGP_AS_65100:
              vrfs:
                CUST-1:
                  peers:
                    59.100.71.193:
                      afi:
                        ipv4:
                          unicast:
                            rpl_in: RPL-1-IMPORT-v4
                            rpl_out: RPL-1-EXPORT-V4
                        ipv6:
                          unicast:
                            rpl_in: RPL-1-IMPORT-V6
                            rpl_out: RPL-1-EXPORT-V6
                      peer_asn: '65101'
                      peer_description: peer-1
                    59.100.71.209:
                      afi:
                        ipv4:
                          unicast:
                            rpl_in: RPL-2-IMPORT-V6
                            rpl_out: RPL-2-EXPORT-V6
                      peer_asn: '65102'
                      peer_description: peer-2
