Template
========

TTP templates support <template> tag to define several templates within single template, each template processes separately, no data shared across templates.

Only two levels of hierarchy supported - top template tag and a number of child template tags within it, further template tags nested within children are ignored.

First use case for this functionality stems from the fact that templates executed in sequence, meaning it is possible to organize such a work flow when results produced by one template can be leveraged by next template(s), for instance first template can produce lookup table text file and other template will rely on.

Another use case is templates grouping under single definition and that can simplify loading - instead of adding each template to TTP object, all of them can be loaded in one go.

For instance::

    from ttp import ttp
    
    template1="""
    <group>
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
    </group>
    """
    
    template2="""
    <group name="vrfs">
    VRF {{ vrf }}; default RD {{ rd }}
    <group name="interfaces">
      Interfaces: {{ _start_ }}
        {{ intf_list | ROW }} 
    </group>
    </group>
    """
    
    parser = ttp()
    parser.add_data(some_data)
    parser.add_template(template1)
    parser.add_template(template2)
    parser.parse()

Above code will produce same results as this code::

    from ttp import ttp
    
    template="""
    <template>
    <group>
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
    </group>
    </template>
    
    <template>
    <group name="vrfs">
    VRF {{ vrf }}; default RD {{ rd }}
    <group name="interfaces">
      Interfaces: {{ _start_ }}
        {{ intf_list | ROW }} 
    </group>
    </group>
    </template>
    """
    
    parser = ttp()
    parser.add_data(some_data)
    parser.add_template(template)
    parser.parse()
    
Template tag attributes
-----------------------------------------------------------------------------

There are a number of attributes can be used with template tag, these attributes help to define template processing behavior.

.. list-table:: 
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `name`_   
     - Uniquely identifies template
   * - `base_path`_   
     - Fully qualified OS path to data
   * - `results`_   
     - Identifies the way how results should be grouped
   * - `pathchar`_   
     - Character to use for group name-path processing

name
******************************************************************************     

TBD

base_path
******************************************************************************     

TBD

results
******************************************************************************     

TBD

pathchar
******************************************************************************     

TBD