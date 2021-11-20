Attributes
==========

There are a number of attributes that outputs system can use. Some attributes can be specific to output itself (name, description), others can be used by formatters or returners. 

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Name
     - Description
   * - `name`_ 
     - name of the output, can be referenced in group *output* attribute
   * - `description`_ 
     - attribute to contain description of outputter
   * - `load`_ 
     - name of the loader to use to load output tag text
   * - `returner`_ 
     - returner to use to return data e.g. self, file, terminal
   * - `format`_ 
     - formatter to use to format results    
   * - `condition`_ 
     - condition to check before running output       

name
******************************************************************************
``name="output_name"``

Name of the output, optional attribute, can be used to reference it in groups :ref:`Groups/Attributes:output` attribute, in that case that output will become group specific and will only process results for this group. 

description
******************************************************************************
``name="desription_string"``

desription_string, optional string that contains output description or notes, can serve documentation purposes.

load
******************************************************************************
``load="loader_name"``    

Name of the loader to use to render supplied output tag text data, default is python.

Supported loaders:

* python - uses python `exec <https://docs.python.org/3/library/functions.html#exec>`_ method to load data structured in native Python formats
* yaml - relies on `PyYAML <https://pyyaml.org/>`_ to load YAML structured data
* json - used to load JSON formatted variables data
* ini - `configparser <https://docs.python.org/3/library/configparser.html>`_ Python standard module used to read variables from ini structured file
* csv - csv formatted data loaded with Python *csv* standard library module
     
returner
******************************************************************************
``returner=returner_name"``    

Name of the returner to use to return results.

format
******************************************************************************
``format=formatter_name"``    

Name of the formatter to use to format results.

condition
******************************************************************************
``condition="template_variable_name, template_variable_value"`` 

Where:

* ``template_variable_name`` - name of template variable to use for condition check
* ``template_variable_value`` - value to evaluate

Attribute to check condition for equality - if ``template_variable_value`` parameter equal to value of
template variable with name ``template_variable_name`` condition satisfied.

Used to conditionally run outputters - if condition met, outputter will run, outputter skipped otherwise.

**Example**

Here we conditionally run csv output formatter using ``convert_to_csv`` template variable::

    data = """
    interface GigabitEthernet1/3.251
     description Customer #32148
     encapsulation dot1q 251
     ip address 172.16.33.10 255.255.255.128
     shutdown
    !
    interface GigabitEthernet1/4
     description vCPEs access control
     ip address 172.16.33.10 255.255.255.128
    """    
    template = """
    <group>
    interface {{ interface }}
     description {{ description }}
     encapsulation dot1q {{ vlan }}
     ip address {{ ip }} {{ mask }}
    </group>
    
    <output condition="convert_to_csv, True" format="csv"/>
    """
    parser1 = ttp(data=data, template=template, vars={"convert_to_csv": False})
    parser1.parse()
    res1 = parser1.result()
    
    parser2 = ttp(data=data, template=template, vars={"convert_to_csv": True})
    parser2.parse()
    res2 = parser2.result()
    
    pprint.pprint(res1)
    # prints:
    # [[[{'interface': 'GigabitEthernet1/3.251',
    #     'ip': '172.16.33.10',
    #     'mask': '255.255.255.128',
    #     'vlan': '251'},
    #    {'interface': 'GigabitEthernet1/4',
    #     'ip': '172.16.33.10',
    #     'mask': '255.255.255.128'}]]]
                           
    pprint.pprint(res2)
    # prints:
    # ['"interface","ip","mask","vlan"\n'
    #  '"GigabitEthernet1/3.251","172.16.33.10","255.255.255.128","251"\n'
    #  '"GigabitEthernet1/4","172.16.33.10","255.255.255.128",""']
    
Outputter ``<output condition="convert_to_csv, True" format="csv"/>`` indicates that this outputter will only run if 
``convert_to_csv`` template variable set to ``True``
