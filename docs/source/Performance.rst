Performance
===========

TTP has performance of approximately 211 lines per millisecond on Intel Core i5-3320M CPU @ 2.6GHz (CPU End-of-Life July 2014) if running in multiprocess mode, dataset of 3,262,464 lines can be parsed in under 16 seconds best case and under 22 seconds worst case. Multiprocessing mode approximately 30-40% faster compared to running in single process, the difference is more significant the more data has to be parsed.

When TTP ready to parse data it goes through decision logic to determine parsing mode following below rules:

* run in single process if ``one=True`` was set for TTP parse method
* run in multiprocess if ``multi=True`` was set for TTP parse method
* run in single process if overall size of loaded data less then 5MByte
* run in multiprocess if overall size of loaded data more then 5MByte and at least two datums loaded

In multiprocessing mode, TTP starts one process per each CPU core on the system and forms a queue of work, there each item contains data for single input datum. For instance we have a folder with 100 files to process, TTP forms queue of 100 chunks of work, each chunk containing text data from single file, in multiprocessing mode that work distributed across several cores in such a way that as long as chunk of work finished by the process it picks up another chunk, without waiting for other processes to finish.

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
