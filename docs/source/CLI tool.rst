CLI tool
========

TTP comes with simple CLI tool that takes path to data, path to template and produces parsing results. Results can be represented in one of formats supported by CLI tool - yaml, json, raw or pprint, results will be printer to screen. Alternatively, format can be specified using template output tags and printed to screen or returned to file using returners. 

Sample usage::

  ttp --data "/path/to/data/" --template "path/to/template.txt" --outputter json
  
  results will be printed to screen in JSON format.
  
**Available options**

* ``-d, --data`` path to data file or directory with files to process
* ``-dp, --data-prefix`` OS base path to folder with data separated across additional folders
* ``-t, --template`` path to text file with template content
* ``-tn, --template-name`` name of template to load from python formatted template file
* ``-o, --outputter`` format results using yaml, json, raw or pprint formatter and prints them to terminal
* ``-l, --logging`` logging level - "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
* ``-lf, --log-file`` OS path to file where to write logs instead of printing them to terminal
* ``-T, --Timing`` print simple timing information to screen about time spent on parsing data
* ``--one`` forcefully run parsing using single process
* ``--multi`` forcefully run parsing in multiple processes