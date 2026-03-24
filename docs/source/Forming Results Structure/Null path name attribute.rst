Null path name attribute
========================

A null path can be specified as a name: ``name="_"``, or as the first item in a path: ``name="_.nextlevel"``.

TTP merges results from a null-path group into its parent, so ``_`` does not appear in the final results.

This is useful for creating a group that processes results normally but merges them flat into the parent, avoiding an extra level of nesting.

**Example**

In this example peer_software used together with _line_ indicator to extract results, however, for _line_ to behave properly it was defined within separate group with explicit ``_start_`` and ``_end_`` indicators. First, this is how template would look like without null path::

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
