Overview
=========

TTP is a Python module for fast parsing of semi-structured text data using templates. It was developed to enable programmatic access to CLI output from networking devices, but can be used to parse any semi-structured text with distinctive repetition patterns.

In the simplest case, TTP takes two inputs — data to parse and a parsing template — and returns a structure with the extracted information.

The same data can be parsed by multiple templates. Templates are easy to create, and users are encouraged to write their own.

Motivation
----------

While networking devices continue to add API capabilities, many legacy and limited devices still lack well-developed APIs for structured data retrieval — the closest they offer is SNMP and CLI text output. Even where APIs exist, the effort to use them can outweigh the value of the results.

There are tools available to parse text data, but the author of TTP believes that parsing is only part of the workflow — the ultimate goal is to act on the data.

Say we have configuration files and want to produce a CSV report of all IP addresses configured on devices, along with their VRFs and interface descriptions. To do that we need to: (1) collect data from various inputs and prepare it, (2) parse that data, (3) format it appropriately, and (4) save it or pass it to other programs. TTP has built-in capabilities to address all of these steps.

Core Functionality
------------------

TTP has a number of systems built into it:

* Groups system - defines results hierarchy and data processing functions with filtering
* Parsing system - uses regular expressions derived from templates to parse and process data
* Input system - defines input data sources, retrieves data, prepares it, and maps it to groups for parsing
* Output system - formats parsing results and delivers them to configured destinations
* Macro - inline Python code to process results and extend TTP functionality with access to the ``_ttp_`` dictionary containing all groups, match, input, and output functions
* Lookup tables - enriches results with additional information or combines results across templates and groups
* Template variables - variable store accessible during template execution for caching or retrieving values
* Template tags - defines multiple independent templates within a single file along with a results forming mode
* Extend tags - extends a template with content from other templates to facilitate re-use
* CLI tool - runs templates directly from the command line
* Lazy loader system - imports only functions used by the template, significantly reducing startup time
* Multiprocessing system - manages multiple Python processes to increase parsing performance
* Logging system - aids troubleshooting and debugging
