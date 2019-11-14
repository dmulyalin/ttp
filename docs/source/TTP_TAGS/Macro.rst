Macro
=====

One of the core features of TTP is to allow data processing on the go, as a result it has a number of built-in function for various systems - function for groups, functions for outputs, functions for variables and functions for match variables. To extend this functionality even further, TTP allows to define custom functions using <macro> tags.

Macro is a python code within <macro> tag text. This code can contain a number of function definitions, these functions can be referenced within TTP templates.

.. warning:: Python `exec <https://docs.python.org/3/library/functions.html#exec>`_ function used to load macro code, as a result it is unsafe to use templates from untrusted sources, as code within macro tag will be executed on template load.

For further details check:

* Match variables :ref:`Match Variables/Functions:macro`
* Groups :ref:`Groups/Functions:macro`
* Outputs :ref:`TTP_TAGS/Outputs/Functions:macro`