Quick start
===========

After installing ttp, to use it as a module::

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

In the template each variable that we want to extract must be placed within ``{{ }}`` brackets, name of match variable will become dictionary key with value equal to extracted data. 

Data can be an OS path to file or directory with files to parse, template can be sourced from text file as well, for instance::

    parser = ttp(data="/path/to/data/file.txt", template="/path/to/template.txt")
    
Data and templates can be loaded to the parser object after instantiation::

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
    
    # create parser object, add data, add template and run parsing:
    parser = ttp()
    parser.add_input(data_to_parse)
    parser.add_template(ttp_template)
    parser.parse()
    
    results = parser.result(format='pprint')[0]
    print(results)    
    [   [   {   'description': 'Router-id-loopback',
                'interface': 'Loopback0',
                'ip': '192.168.0.113',
                'mask': '24'},
            {   'description': 'CPE_Acces_Vlan',
                'interface': 'Vlan778',
                'ip': '2002::fd37',
                'mask': '124',
                'vrf': 'CPE1'}]]