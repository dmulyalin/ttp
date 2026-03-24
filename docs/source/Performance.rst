Performance
===========

TTP achieves approximately 211 lines per millisecond on an Intel Core i5-3320M CPU @ 2.6GHz (CPU End-of-Life July 2014) in multiprocess mode. A dataset of 3,262,464 lines can be parsed in under 16 seconds (best case) and under 22 seconds (worst case). Multiprocessing mode is approximately 30–40% faster than single-process mode; the difference grows with dataset size.

When TTP is ready to parse data, it determines the parsing mode using the following rules:

* run in single process if ``one=True`` was set for TTP parse method
* run in multiprocess if ``multi=True`` was set for TTP parse method
* run in single process if overall size of loaded data is less than 5 MB
* run in multiprocess if overall size of loaded data is more than 5 MB and at least two data items are loaded

In multiprocessing mode, TTP starts one process per CPU core and forms a work queue where each item contains data for a single input. For example, with a folder of 100 files, TTP creates 100 work chunks, each containing text data from one file. Work is distributed across cores so that as soon as a process finishes a chunk, it picks up the next one without waiting for other processes.

Multiprocessing mode restrictions
---------------------------------

While multiprocessing mode has obvious processing speed increase benefits, it comes with several restrictions.

* per_template results mode not supported with multiprocessing as no results shared between processes, only per_input mode supported with multiprocessing
* startup time for multiprocessing is slower compared to single process, as each process takes time to initiate
* global variables space not shared between processes, as a result a number of functions will not be able to operate properly, such as:

  * match variable count function - ``globvar`` will not have access to global variables
  * match variable record function - record cannot save variables in global namespace
  * match variable lookup function - will not work if reference group that parse different inputs due to ``_ttp_['template_obj']`` not shared between processes

General performance considerations
-----------------------------------

Keep data processing out of TTP if you are after best performance, the more processing/functions TTP has to run, the more time it will take to finish parsing.

During parsing, avoid use of broad match regular expressions, such as ``.*`` unless no other options left, one such expression used for ``_line_`` indicator internally. As a result of excessive matches, processing time can increase significantly. Strongly consider using ``_end_`` indicator together with any broad match regexes to limit the scope of text processed.

Consider providing TTP with as clean data as possible - data that contains only text that will be matched by TTP. That will help to save CPU cycles by not processing unrelated data, also that will guarantee that no false positive matches exist. For instance, input ``commands`` function can be used to pre-process data and present only required commands output to certain groups.
