Getters
=======

TTP template variables also support a number of getters - functions targeted to get some information and assign it to variable. Getters called for each input datum.

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Function
     - Description
   * - `gethostname`_
     - this function tries to extract hostname out of source data prompts
   * - `getfilename`_
     - returns a name of the source data
   * - `get_time`_
     - returns current time
   * - `get_date`_
     - returns current date
   * - `get_timestamp`_
     - returns combination of current date and time
   * - `get_timestamp_ms`_
     - returns combination of current date and time with milliseconds
   * - `get_timestamp_iso`_
     - returns timestamp in ISO format in UTC timezone
   * - `get_time_ns`_
     - returns current time in nanoseconds since Epoch

gethostname
------------------------------------------------------------------------------
``var_name="gethostname"``

Using this getter function TTP tries to extract device's hostname out of it prompt.

Supported prompts are:

* Juniper such as ``some.user@hostname>``
* Huawei such as ``<hostname>``
* Cisco IOS Exec such as ``hostname>``
* Cisco IOS XR such as ``RP/0/4/CPU0:hostname#``
* Cisco IOS Privileged such as ``hostname#``
* Fortigate such as ``hostname (context) #``
* Nokia (ALU) SROS such as ``A:hostname>``, ``*A:hostname#`` or ``*A:ALA-12>config#``

**Example**

Template::

    <input load="text">
    switch1#show run int
    interface GigabitEthernet3/11
     description input_1_data
    </input>

    <vars name="vars">
    hostname_var = "gethostname"
    </vars>

    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
    </group>

Result::

    [
        {
            "interfaces": {
                "description": "input_1_data",
                "interface": "GigabitEthernet3/11"
            },
            "vars": {
                "hostname_var": "switch1"
            }
        }
    ]

getfilename
------------------------------------------------------------------------------
``var_name="getfilename"``

This function returns the name of input data file if data was loaded from file, if data was loaded from text it will return "text_data".

get_time
------------------------------------------------------------------------------
``var_name="get_time"``

Returns current time in ``%H:%M:%S`` format.

get_date
------------------------------------------------------------------------------
``var_name="get_date"``

Returns current date in ``%Y-%m-%d`` format.

get_timestamp
------------------------------------------------------------------------------
``var_name="get_timestamp"``

Returns current timestamp in ``%Y-%m-%d %H:%M:%S`` format.

get_timestamp_ms
------------------------------------------------------------------------------
``var_name="get_timestamp_ms"``

Returns current timestamp but with milliseconds precision in a format of ``%Y-%m-%d %H:%M:%S.%ms``

get_timestamp_iso
------------------------------------------------------------------------------
``var_name="get_timestamp_iso"``

Returns current timestamp in ISO format with UTC timezone e.g. ``2020-06-30T11:07:01.212349+00:00``. Uses python datetime function to produce timestamp.

get_time_ns
------------------------------------------------------------------------------
``var_name="get_time_ns"``

This function uses time.time_ns method to return current time in nanoseconds since Epoch
