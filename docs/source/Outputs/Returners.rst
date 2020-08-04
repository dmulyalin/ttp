Returners
=========
     
TTP has `file`_, `terminal`_ and `self`_ returners. The purpose of returner is to return or emit or save data to certain destination.

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Returner
     - Description
   * - `self`_   
     - return result to calling function
   * - `file`_   
     - save results to file
   * - `terminal`_   
     - print results to terminal screen
   * - `syslog`_   
     - send results over UDP to Syslog server
	 
  
self
-------------------------------------

Default returner, data processed by output returned back to ttp for further processing, that way outputs can be chained to produce required results. Another use case is when ttp used as a module, results can be formatted retrieved out of ttp object.

file
-------------------------------------

Results will be saved to text file on local file system. One file will be produced per template to contain all the results for all the inputs and groups of this template.

**Supported returner attributes**

* ``url`` OS path to folder where file should be stored
* ``filename`` name of the file, can contain these time formatter::

   * ``%m``  Month as a decimal number [01,12].
   * ``%d``  Day of the month as a decimal number [01,31].
   * ``%H``  Hour (24-hour clock) as a decimal number [00,23].
   * ``%M``  Minute as a decimal number [00,59].
   * ``%S``  Second as a decimal number [00,61].
   * ``%z``  Time zone offset from UTC.
   * ``%a``  Locale's abbreviated weekday name.
   * ``%A``  Locale's full weekday name.
   * ``%b``  Locale's abbreviated month name.
   * ``%B``  Locale's full month name.
   * ``%c``  Locale's appropriate date and time representation.
   * ``%I``  Hour (12-hour clock) as a decimal number [01,12].
   * ``%p``  Locale's equivalent of either AM or PM.

   
For instance, filename="OUT_%Y-%m-%d_%H-%M-%S_results.txt" will be rendered to "OUT_2019-09-09_18-19-58_results.txt" filename. By default filename is set to "output_<ctime>.txt", where "ctime" is a string produced after rendering "%Y-%m-%d_%H-%M-%S" by python `time.strftime() <https://docs.python.org/3/library/time.html#time.strftime>`_ function.

terminal
-------------------------------------

Results will be printed to terminal window. Terminal returner support colouring output using `colorama module <https://pypi.org/project/colorama/>`_

**Supported returner attributes**

* ``colour`` if present with any value, colorama module will be initiated to colour certain words in output
* ``red_words`` comma separated list of patterns to colour in red, default is *False,No,Failed,Error,Failure,Fail,false,no,failed,error,failure,fail*
* ``green_words`` comma separated list of patterns to colour in green, default is *True,Yes,Success,Ok,true,yes,success,ok*
* ``yeallow_words`` comma separated list of patterns to colour in yellow, default is *Warning,warning*

**Example**

Template::

    <input load="text">
    interface Port-Channel11
      description Storage Management
    interface Loopback0
      description RID
    interface Vlan777
      description Management
    </input>
    
    <group>
    interface {{ interface | contains("Port-Channel") }}
      description {{ description }}
      {{ is_lag | set(True) }}
      {{ is_loopback| set(False) }}
    </group>
    
    <group>
    interface {{ interface | contains("Loop") }}
      description {{ description }}
      {{ is_lag | set(False) }}
      {{ is_loopback| set(True) }}
    </group>
    
    <output
    returner="terminal" 
    colour=""  
    red="false,False" 
    green="true,True"
    format="json"
    />
	
Results printed to screen:

.. image:: ../_images/terminal_returner_colorama.png

syslog
-----------

TBD