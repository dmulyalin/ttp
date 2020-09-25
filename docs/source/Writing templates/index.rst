Writing templates
=================

Writing templates is simple.

To create template, take data that needs to be parsed and replace portions of it with match variables::

    # Data we want to parse
    interface Loopback0
     description Router-id-loopback
     ip address 192.168.0.113/24
    !
    interface Vlan778
     description CPE_Acces_Vlan
     ip address 2002::fd37/124
     ip vrf CPE1
    !

    # TTP template
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
     description {{ description }}
     ip vrf {{ vrf }}
    
Above data and template can be saved in two files, and ttp CLI tool can be used to parse it with command::

    ttp -d "/path/to/data/file.txt" -t "/path/to/template.txt" --outputter json	
	
And get these results::

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
	
.. warning:: TTP match variables names used as regular expressions group names, hence they must be valid Python identifiers, except for ``.`` and ``-`` characters, dot replaced with ``__dot_char__`` to use with group ``expand`` function and ``-`` replaced with ``_`` but reconstructed to original value when forming results.

Above process is very similar to writing `Jinja2 <https://palletsprojects.com/p/jinja/>`_ templates but in reverse direction - we have text and we need to transform it into structured data, as opposed to having structured data, that needs to be rendered with Jinja2 template to produce text.

.. warning:: Indentation is important. Trailing spaces and tabs are ignored by TTP.

TTP use leading spaces and tabs to produce better match results, exact number of leading spaces and tabs used to form regular expressions. There is a way to ignore indentation by the use of :ref:`Match Variables/Indicators:ignore` indicator coupled with ``[\s\t]*`` or ``\s+`` or ``\s{1,3}`` or ``\t+`` etc.  regular expressions. 

TTP supports various output formats, for instance, if we need to emit data not in json but csv format we can use outputter and write this template::

    <group>
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
     description {{ description }}
     ip vrf {{ vrf }}
    </group>
    
    <output format="csv" returner="terminal"/> 

Run ttp CLI tool without -o option to print only results produced by outputter defined within template:: 

	ttp -d "/path/to/data/file.txt" -t "/path/to/template.txt"	

We told TTP that ``returner="terminal"``, because of that results will be printed to terminal screen::

    description,interface,ip,mask,vrf
    Router-id-loopback,Loopback0,192.168.0.113,24,
    CPE_Acces_Vlan,Vlan778,2002::fd37,124,CPE1

XML Primer
----------

TBD

HOW TOs
-------

.. toctree::
   :maxdepth: 2
   
   How to parse hierarchical (configuration) data
   How to parse text tables
   How to parse show commands output
   How to filter with TTP
   How to produce time series data with TTP