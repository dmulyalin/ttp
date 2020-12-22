TTP Templates Collection
========================

`TTP Templates <https://github.com/dmulyalin/ttp_templates>`_ repository contains a number of TTP templates.

Install::

    pip install ttp_templates
  
To reference templates from ``ttp_templates``, ttp parser ``template`` argument should be of ``ttp://<path>`` format, where ``path`` is an OS path to template text file within ``ttp_templates`` repository.

Sample code::

    from ttp import ttp
    import pprint
    
    data = """
    <input load="text">
    interface Lo0
     ip address 124.171.238.50 32
    !
    interface Lo1
     description this interface has description
     ip address 1.1.1.1 32
    </input>
    """
    
    parser = ttp(data=data, template="ttp://platform/test_platform_show_run_pipe_sec_interface.txt")
    parser.parse()
    res = parser.result()
    
    pprint.pprint(res)
    
    # prints:
    # 
    # [[[{'interface': 'Lo0', 'ip': '124.171.238.50', 'mask': '32'},
    #    {'description': 'this interface has description',
    #     'interface': 'Lo1',
    #     'ip': '1.1.1.1',
    #     'mask': '32'}]]]
    
Where ``platform/test_platform_show_run_pipe_sec_interface.txt`` is a text file from ``ttp_templates`` repository with content::

    <group>
    interface {{ interface }}
     description {{ description | re(".+") }}
     encapsulation dot1q {{ dot1q }}
     ip address {{ ip }} {{ mask }}
     shutdown {{ disabled | set(True) }}
    </group>