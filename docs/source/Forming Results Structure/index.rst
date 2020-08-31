Forming Results Structure
=========================

TTP supports variety of techniques to influence results structure. Majority of them revolving around group name attribute, which represents dot separated path of keys within results structure - that is generally helps for results within given template. Other methods can influence results representation across several templates.

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

TTP object ``result`` method have support for ``structure`` keyword, allowing to combine results across several templates in either a list or dictionary manner.