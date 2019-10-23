How to parse hierarchical configuration data
============================================

TTP can use simple templates that does not contain much hierarchy (same as the data that parsed by them), but what to do if we want to extract information from below text::

    router bgp 12.34
     address-family ipv4 unicast
      router-id 1.1.1.1
     !
     vrf CT2S2
      rd 102:103
      !
      neighbor 10.1.102.102
       remote-as 102.103
       address-family ipv4 unicast
        send-community-ebgp
        route-policy vCE102-link1.102 in
        route-policy vCE102-link1.102 out
       !
      !
      neighbor 10.2.102.102
       remote-as 102.103
       address-family ipv4 unicast
        route-policy vCE102-link2.102 in
        route-policy vCE102-link2.102 out
       !
      !
     vrf AS65000
      rd 102:104
      !
      neighbor 10.1.37.7
       remote-as 65000
       address-family ipv4 labeled-unicast
        route-policy PASS-ALL in
        route-policy PASS-ALL out
    
In such a case we have to use ttp groups to define nested, hierarchical structure, sample template might look like this::

    <group name="bgp_cfg">
    router bgp {{ ASN }}
     <group name="ipv4_afi">
     address-family ipv4 unicast {{ _start_ }}
      router-id {{ bgp_rid }}
     </group>
     
     <group name="vrfs">
     vrf {{ vrf }}
      rd {{ rd }}
      
      <group name="neighbors">
      neighbor {{ neighbor }}
       remote-as {{ neighbor_asn }}
       <group name="ipv4_afi">
       address-family ipv4 unicast {{ _start_ }}
        send-community-ebgp {{ send_community_ebgp | set("Enabled") }}
        route-policy {{ RPL_IN }} in
        route-policy {{ RPL_OUT }} out
       </group>
      </group>
     </group>
    </group>
    
Above data and template can be saved in two files and run using ttp CLI tool with command::

    ttp -d "/path/to/data/file.txt" -t "/path/to/template.txt" --outputter yaml	
	
These results will be printed to screen::

    - bgp_cfg:
        ASN: '12.34'
        ipv4_afi:
          bgp_rid: 1.1.1.1
        vrfs:
        - neighbors:
          - ipv4_afi:
              RPL_IN: vCE102-link1.102
              RPL_OUT: vCE102-link1.102
              send_community_ebgp: Enabled
            neighbor: 10.1.102.102
            neighbor_asn: '102.103'
          - ipv4_afi:
              RPL_IN: vCE102-link2.102
              RPL_OUT: vCE102-link2.102
            neighbor: 10.2.102.102
            neighbor_asn: '102.103'
          rd: 102:103
          vrf: CT2S2
        - neighbors:
          - ipv4_afi:
              RPL_IN: PASS-ALL
              RPL_OUT: PASS-ALL
          - neighbor: 10.1.37.7
            neighbor_asn: '65000'
          rd: 102:104
          vrf: AS65000

Not too bad, but let's say we want VRFs to be represented as a dictionary with VRF names as keys, same goes for neighbors - we want them to be a dictionary with neighbor IPs as a key, we can use TTP dynamic path feature together with path formatters to accomplish exactly that, here is the template::

    <group name="bgp_cfg">
    router bgp {{ ASN }}
     <group name="ipv4_afi">
     address-family ipv4 unicast {{ _start_ }}
      router-id {{ bgp_rid }}
     </group>
     !
     <group name="vrfs.{{ vrf }}">
     vrf {{ vrf }}
      rd {{ rd }}
      !
      <group name="peers.{{ neighbor }}**">
      neighbor {{ neighbor }}
       remote-as {{ neighbor_asn }}
       <group name="ipv4_afi">
       address-family ipv4 unicast {{ _start_ }}
        send-community-ebgp {{ send_community_ebgp | set("Enabled") }}
        route-policy {{ RPL_IN }} in
        route-policy {{ RPL_OUT }} out
       </group>
      </group>
     </group>
    </group>
    
After parsing TTP will print these structure::

    - bgp_cfg:
        ASN: '12.34'
        ipv4_afi:
          bgp_rid: 1.1.1.1
        vrfs:
          AS65000:
            peers:
              10.1.37.7:
                ipv4_afi:
                  RPL_IN: PASS-ALL
                  RPL_OUT: PASS-ALL
                neighbor_asn: '65000'
            rd: 102:104
          CT2S2:
            peers:
              10.1.102.102:
                ipv4_afi:
                  RPL_IN: vCE102-link1.102
                  RPL_OUT: vCE102-link1.102
                  send_community_ebgp: Enabled
                neighbor_asn: '102.103'
              10.2.102.102:
                ipv4_afi:
                  RPL_IN: vCE102-link2.102
                  RPL_OUT: vCE102-link2.102
                neighbor_asn: '102.103'
            rd: 102:103
        
That's better, but what actually changed to have such a different results, well, not to much by the look of it, but quite a lot in fact.

TTP group's name attribute actually used as a path where to save group parsing results within results tree, to denote different levels dot symbol can be used, that is how we get new *vrf* and *peers* keys in the output. 

In addition we used TTP dynamic path feature by introducing ``{{ vrf }}`` and ``{{ neighbor }}`` in the name of the group, that will be dynamically substituted with matching results.

Moreover, we also have to use double star ``**`` path formatter to tell TTP that ``{{ neighbor }}`` child content should be kept as a dictionary and not transformed into list (default behavior) whenever we add new data to that portion of results tree.