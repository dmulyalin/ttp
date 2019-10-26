[![Downloads](https://pepy.tech/badge/ttp)](https://pepy.tech/project/ttp)
[![PyPI versions](https://img.shields.io/pypi/pyversions/ttp.svg)](https://pypi.python.org/pypi/ttp/)
[![Documentation status](https://readthedocs.org/projects/ttp/badge/?version=latest)](http://ttp.readthedocs.io/?badge=latest)

# Template Text Parser

TTP is a Python library for parsing semi-structured text data using templates relying on Python built-in regular expression module and XML Etree to structure templates. TTP was mainly developed to enable programmatic access to data produced by CLI of networking devices (show commands output or configuration), however, it can be used to parse any semi-structured text that contains distinctive repetition patterns.

In the simplest case TTP takes two files as an input - data that needs to be parsed and template, returning results structure that contains extracted information.

Templates are easy to create and users encouraged to write their own TTP templates, in addition TTP docs shipped with a set of examples applicable for parsing output of network equipment.

Reference [documentation](https://ttp.readthedocs.io) for more information.
