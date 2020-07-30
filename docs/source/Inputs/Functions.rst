Functions
===================

Input tag support functions to pre-process data.

.. list-table:: 
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `functions attribute`_   
     - String with functions defined int it
   * - `macro`_   
     - Name of macro function to run input data through
   * - `extract_commands`_   
     - Comma separated list of commands output to extract from text data
   * - `test`_   
     - Test function to verify input function handling
     
functions attribute
------------------------------------------------------------------------
``functions="function1('attributes') | function2('attributes') | ... | functionN('attributes')"``

* functionN - name of the input function together with it's attributes

This attribute allow to define a sequence of function, the main advantage of using string of functions against defining functions directly in the input tag is the fact that functions order will be honored, otherwise functionality is the same.

.. warning:: pipe '|' symbol must be used to separate function names, not comma

macro
------------------------------------------------------------------------
``macro="name1, name2, ... , nameN"``

* nameN - comma separated string of macro functions names that should be used to run input data through. The sequence is *preserved* and macros executed in specified order, in other words macro named name2 will run after macro name1.

Macro brings Python language capabilities to input data processing and validation during TTP module execution, as it allows to run custom python functions. Macro functions referenced by their name in input tag macro definitions.

Macro function must accept only one attribute to hold input data text.

Depending on data returned by macro function, TTP will behave differently according to these rules:

* If macro returns True or False - original data unchanged, macro handled as condition functions, stopping further functions execution on False and keeps processing input data on True
* If macro returns None - data processing continues, no additional logic associated
* If macro returns single item - that item replaces original data supplied to macro and processed further by other input tag functions

extract_commands
------------------------------------------------------------------------
``extract_commands="command1, command2, ... , commandN"``     

Purpose of this function is for each network device command string TTP can extract associated data from input text, so that input groups will only process data they designed to parse
    
..note:: to be able to successfully extract show commands output, text data should contain device hostname together with command itself. ``gethostname`` function will be called on data to extract hostname
    
**Example**

In below template, only "show interfaces" command output will be processed, as only that command specified in input ``extract_commands`` attribute.

Template::

    <input load="text" extract_commands="show interfaces">
    cpe1#show int
    GigabitEthernet33 is up, line protocol is up
      Hardware is CSR vNIC, address is 0800.2779.9999 (bia 0800.2779.9999)
    cpe1#show interfaces
    GigabitEthernet44 is up, line protocol is up
      Hardware is CSR vNIC, address is 0800.2779.e896 (bia 0800.2779.e896)
    cpe1#show interf
    GigabitEthernet55 is up, line protocol is up
      Hardware is CSR vNIC, address is 0800.2779.e888 (bia 0800.2779.e888)
    </input>
    
    <group name="interfaces_status">
    {{ interface }} is up, line protocol is up
      Hardware is CSR vNIC, address is {{ mac }} (bia {{ bia_mac }})
    </group>

Result::

    [
        [
            {
                "interfaces_status": {
                    "bia_mac": "0800.2779.e896",
                    "interface": "GigabitEthernet44",
                    "mac": "0800.2779.e896"
                }
            }
        ]
    ]

test
------------------------------------------------------------------------
``test=""``     

Test function to verify input function call, test simply prints informational message to the screen, indicating that input test function was called.