Null path name attribute
========================

It is possible to specify null path as a name, null path looks like ``name="_"`` or null path can be used as a first item in the path - ``name="_.nextlevel"``. 

Special handling implemented for null path - TTP will merge results with parent for group with null path, as a result null path ``_`` will not appear in results. 

One of the usecases for this feature is to create a group that will behave like a normal group in terms of results forming and processing, but will merge with parent in the process of saving into overall results. 

**Example**

In this example peer_software used together with _line_ indicator to extract results, however, for _line_ to behave properly it was defined within separate group with explicit _stat_ and _end_ indicators. First, this is how template would look like without null path::

    <input load="text">
    Device ID: switch-2.net 
    IP address: 10.251.1.49
    
    Version :
    Cisco Internetwork Operating System Software 
    IOS (tm) s72033_rp Software (s72033_rp-PK9SV-M), Version 12.2(17d)SXB11a, RELEASE SOFTWARE (fc1)
    
    advertisement version: 2
    </input>
    
    <group>
    Device ID: {{ peer_hostname }}
    IP address: {{ peer_ip }}
    
    <group name="peer_software">
    Version : {{ _start_ }}
    {{ peer_software | _line_ }}
    {{ _end_ }}
    </group>
    
    </group>
	
And result would be::

    [
        [
            {
                "peer_hostname": "switch-2.net",
                "peer_ip": "10.251.1.49",
                "peer_software": {
                    "peer_software": "Cisco Internetwork Operating System Software \nIOS (tm) s72033_rp Software (s72033_rp-PK9SV-M), Version 12.2(17d)SXB11a, RELEASE SOFTWARE (fc1)"
                }
            }
        ]
    ]
	
Above results have a bit of redundancy in them as they have unnecessary hierarchy to store peer_software details, to avoid that, null path can be used::

    <input load="text">
    Device ID: switch-2.net 
    IP address: 10.251.1.49
    
    Version :
    Cisco Internetwork Operating System Software 
    IOS (tm) s72033_rp Software (s72033_rp-PK9SV-M), Version 12.2(17d)SXB11a, RELEASE SOFTWARE (fc1)
    
    advertisement version: 2
    </input>
    
    <group>
    Device ID: {{ peer_hostname }}
    IP address: {{ peer_ip }}
    
    <group name="_">
    Version : {{ _start_ }}
    {{ peer_software | _line_ }}
    {{ _end_ }}
    </group>
    
    </group>
	
Results with new template::

    [
        [
            {
                "peer_hostname": "switch-2.net",
                "peer_ip": "10.251.1.49",
                "peer_software": "Cisco Internetwork Operating System Software \nIOS (tm) s72033_rp Software (s72033_rp-PK9SV-M), Version 12.2(17d)SXB11a, RELEASE SOFTWARE (fc1)"
            }
        ]
    ]
	
Even though peer_software match variable was defined in separate group, because of null path, it was merged with parent group, flattening results structure.