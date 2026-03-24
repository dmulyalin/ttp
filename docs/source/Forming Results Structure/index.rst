.. _results_structure:

Forming Results Structure
=========================

TTP supports a variety of techniques to influence results structure. Most revolve around the group ``name`` attribute, which represents a dot-separated path of keys within the results structure. Other methods can influence results representation across multiple templates.

.. toctree::
   :maxdepth: 2
   :titlesonly:

   Group Name Attribute
   Path formatters
   Dynamic Path
   Dynamic path with path formatters
   Anonymous group
   Null path name attribute
   Absolute path

Expanding Match Variables
-------------------------

Match variables can have name with dot characters in it. Group function :ref:`Groups/Functions:expand` can be used to transform names in a nested dictionary. However, path expansion contained within this group this particular results datum only.

Template results mode
---------------------

Templates support :ref:`Template Tag/Template Tag:results` attribute that can help to influence results structure within given template.

TTP object results structure
----------------------------

TTP object ``result`` method supports the ``structure`` keyword, allowing results from multiple templates to be combined into either a list or a dictionary.
