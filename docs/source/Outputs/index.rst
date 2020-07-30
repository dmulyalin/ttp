Outputs
=======

Outputs system allows to process parsing results, format them in certain way and return results to various destination. For instance, using yaml formatter results can take a form of YAML syntax and using file returner these results can be saved into file.

Outputs can be chained, say results after passing through first outputter will serve as an input for next outputter. That allows to implement complex processing logic of results produced by ttp.

The opposite way would be that each output defined in template will work with parsing results, transform them in different way and return to different destinations. An example of such a behavior might be the case when first outputter form csv table and saves it onto the file, while second outputter will render results with Jinja2 template and print them to the screen.

In addition two types of outputter exists - template specific and group specific. Template specific outputs will process template overall results, while group-specific will work with results of this particular group only.

There is a set of function available in outputs to process/modify results further.

.. note:: If several outputs provided - they run sequentially in the order defined in template. Within single output, processing order is - functions run first, after that formatters, followed by returners. 

Outputs reference
-------------------

.. toctree::
   :maxdepth: 2
   
   Attributes
   Functions
   Formatters
   Returners