Performance
===========

TTP has performance of approximately 211 lines per millisecond on Intel Core i5-3320M CPU @ 2.6GHz (CPU End-of-Life July 2014) if running in multiprocess mode with all function pre-cached by Python, meaning that dataset of 3,262,464 lines can be parsed in under 16 seconds best case and under 22 seconds worst case.


Multiprocessing mode restrictions
---------------------------------

While multiprocessing mode has obvious processing speed increase benefits, it comes with several restrictions.

* per_template results mode not supported with multiprocessing as no results shared between processes
* global variables are not shared between processes and have per-process significance (name space), this is due to the fact that global vars not shared between processes