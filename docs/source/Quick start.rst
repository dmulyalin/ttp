Quick start
===========

TTP can be used as a module, as a CLI tool or as a script.

As a module
-----------

Sample code::

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
    
    # create parser object and parse data using template:
    parser = ttp(data=data_to_parse, template=ttp_template)
    parser.parse()
    
    # print result in JSON format
    results = parser.result(format='json')[0]
    print(results)
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
    
    # or in csv format
    csv_results = parser.result(format='csv')[0]
    print(csv_results)
    description,interface,ip,mask,vrf
    Router-id-loopback,Loopback0,192.168.0.113,24,
    CPE_Acces_Vlan,Vlan778,2002::fd37,124,CPE1
    
As a CLI tool
-------------

Sample command to run in terminal::

    ttp --data "path/to/data_to_parse.txt" --template "path/to/ttp_template.txt" --outputter json
    
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
    
Where file ``path/to/data_to_parse.txt`` contains::

    interface Loopback0
     description Router-id-loopback
     ip address 192.168.0.113/24
    !
    interface Vlan778
     description CPE_Acces_Vlan
     ip address 2002::fd37/124
     ip vrf CPE1
    !
    
And file ``path/to/ttp_template.txt`` contains::

    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
     description {{ description }}
     ip vrf {{ vrf }}