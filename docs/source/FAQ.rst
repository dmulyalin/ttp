FAQ
===

Collection of answers to frequently asked questions.

Why TTP returns nested list of lists of lists?
==============================================

By default TTP accounts for most general case where several templates added in TTP object,
each template producing its own results, that is why top structure is a list.

Within template, several inputs can be defined (input = string/text to parse), parsing results 
for each input produced independently, joining in a list, where each item corresponds to 
input. That gives second level of lists.

If template does not have groups defined or has groups without ``name`` attribute, results for
such a template will produce list of items on a per-input basis. That is third level of lists.

Above is a default, generalized behavior that (so far) works for all cases, as items always can be 
appended to the list. 

Reference :ref:`results_structure` documentation on how to produce results suitable for your case
using TTP built-in techniques, otherwise, Python results post-processing proved to be useful
as well.

How to add comments in TTP templates?
=====================================

To put single line comment within TTP group use double hash tag - ``##``, e.g.::

    <group name="interfaces">
    ## important comment
    ## another comment
    interface {{ interface }}
     description {{ description }}
    </group>
    
To place comments outside of TTP groups can use XML comments::

    <!--Your comment, can be
    multi line  
    -->
    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
    </group>
    
If you after writing extensive description about your template, using <doc> tag
could be another option::

    <doc>
    My 
    documentation 
    here
    </doc>
    
    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
    </group>

How to make TTP always return a list even if single item matched?
=================================================================

Please reference TTP :ref:`path_formatters` for details on how 
to enforce list or dictionary as part of results structure.

Generally, going through :ref:`results_structure` documentation 
might be useful as well.