Outputs
=======

The outputs system processes parsing results, formats them, and delivers them to configured destinations. For example, using the yaml formatter, results can be formatted as YAML, and using the file returner, they can be saved to a file.

Outputs can be chained: the result of the first outputter becomes the input for the next, enabling complex processing pipelines.

Alternatively, each output defined in the template can independently transform results and deliver them to different destinations. For example, one outputter may produce a CSV file while another renders results with a Jinja2 template and prints them to screen.

Two types of outputters exist: template-specific and group-specific. Template-specific outputs process the overall template results; group-specific outputs process only the results of a particular group.

A set of functions is available in outputs to further process or modify results.

.. note:: If multiple outputs are defined, they run sequentially in the order specified in the template. Within a single output, the processing order is: functions first, then formatters, then returners.

Outputs reference
-------------------

.. toctree::
   :maxdepth: 2

   Attributes
   Functions
   Formatters
   Returners
