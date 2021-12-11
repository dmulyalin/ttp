How to produce time series data with TTP
========================================

Time stamped data is very easy to produce with TTP, as it has built-in time related functions, allowing to add timestamp to match results. For example, interface counters can be parsed with TTP every X number of seconds, marked with timestamp, producing simple time series data.

Consider this source data::

    GigabitEthernet1 is up, line protocol is up
         297 packets input, 25963 bytes, 0 no buffer
         160 packets output, 26812 bytes, 0 underruns
    GigabitEthernet2 is up, line protocol is up
         150 packets input, 2341 bytes, 0 no buffer
         351 output errors, 3459 collisions, 0 interface resets

And the goal is to get this result::

    {
        timestamp: {
            interface: {
                in_pkts: int,
                out_pkts: int
                }
            }
        }

Template to produce above structure is::

    <vars>
    timestamp = "get_timestamp_ms"
    </vars>

    <group name = "{{ timestamp }}.{{ interface }}">
    {{ interface }} is up, line protocol is up
         {{ in_pkts}} packets input, 25963 bytes, 0 no buffer
         {{ out_pkts }} packets output, 26812 bytes, 0 underruns
    </group>

Results after parsing above data with template::

    [
        [
            {
                "2019-11-10 16:18:32.523": {
                    "GigabitEthernet1": {
                        "in_pkts": "297",
                        "out_pkts": "160"
                    },
                    "GigabitEthernet2": {
                        "in_pkts": "150"
                    }
                }
            }
        ]
    ]

Attention should be paid to the fact, that timestamps produced using local time of the system that happens to parse text data, as a result get_time_ns function can be used to produce time in nanoseconds since the epoch (midnight, 1st of January, 1970) in UTC.
