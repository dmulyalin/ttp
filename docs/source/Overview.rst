Overview
=========

TTP is a Python module that allows relatively fast performance parsing of semi-structured text data using templates. TTP was developed to enable programmatic access to data produced by CLI of networking devices, but, it can be used to parse any semi-structured text that contains distinctive repetition patterns.

In the simplest case ttp takes two files as an input - data that needs to be parsed and parsing template, returning results structure with extracted information.

Same data can be parsed by several templates producing results accordingly, templates are easy to create and users encouraged to write their own ttp templates.

Motivation
----------

While networking devices continue to develop API capabilities, there is a big footprint of legacy and not-so devices in the field, these devices are lacking of any well developed API to retrieve structured data, the closest they can get is SNMP and CLI text output. Moreover, even if some devices have API capable of representing their configuration or state data in the format that can be consumed programmatically, in certain cases, the amount of work that needs to be done to make use of these capabilities outweighs the benefits or value of produced results.

There are a number of tools available to parse text data, but, author of TTP believes that parsing data is only part of the work flow, where the ultimate goal is to make use of the actual data.

Say we have configuration files and we want to create a report of all IP addresses configured on devices together with VRFs and interface descriptions, report should have csv format. To do that we have (1) collect data from various inputs and maybe sort and prepare it, (2) parse that data, (3) format it in certain way and (4) save it somewhere or pass to other program(s). TTP has built-in capabilities to address all of these steps to produce desired outcome.

Core Functionality
------------------

TTP has a number of systems built into it:

* Groups system - help to define results hierarchy and data processing functions with filtering
* Parsing system - uses regular expressions derived out of templates to parse and process data
* Input system - used to define various input data sources, help to retrieve data, prepare it and map to the groups for parsing
* Output system - allows to format parsing results and return them to certain destinations
* Macro - inline Python code that can be used to process results and extend TTP functionality, having access to _ttp_ dictionary containing all groups, match, inputs, outputs functions
* Lookup tables - helps to enrich results with additional information or reference results across different templates or groups to combine them
* Template variables - variables store, accessible during template execution for caching or retrieving values
* Template tags - to define several independent templates within single file together with results forming mode
* Extend tags - helps to extend template with other templates to facilitate re-use of templates
* CLI tool - allows to run templates directly from command line
* Lazy loader system - TTP only imports function it uses within the templates, that significantly decreases start time
* Multiprocessing system - controls the start and data exchange between several Python processes to increase parsing performance
* Logging system - helps to troubleshoot and debug TTP
