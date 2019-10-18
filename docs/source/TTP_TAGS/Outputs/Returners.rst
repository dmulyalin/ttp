Returners
=========
     
TTP has `file`_, `terminal`_ and `self`_ returners. The purpose of returner is to return or emit or save data to certain destination.
  
self
******************************************************************************

Default returner, data processed by output returned back to ttp for further processing, that way outputs can be chained to produce required results. Another use case is when ttp used as a module, results can be formatted retrieved out of ttp object.

file
******************************************************************************

Results will be saved to text file on local file system. One file will be produced per template to contain all the results for all the inputs and groups of this template.

terminal
******************************************************************************

Results will be printed to terminal window.

Returner attributes
******************************************************************************

.. list-table::
   :widths: 10 10 80
   :header-rows: 1
   
   * - Returner
     - Attribute
     - Description   
     
   * - file
     - `url`_
     - OS path to folder there to save results
   * - file
     - `filename`_ 
     - name of the file to save data in  
     
url
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If returner is file - url attribute helps to specify full OS path to folder where file should be stored.

filename
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If returner is file - filename specifies the name of the file to save data in. Filename attribute support a number of formatters.

Time filename formatters::

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