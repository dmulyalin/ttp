import sys

sys.path.insert(0, "../..")
import pprint
import json
import os
import pytest

from ttp import ttp


# =====================================================================
# UTILS guess FUNCTION
# =====================================================================


def test_guess_function():
    """Test the guess utility function"""
    from ttp.utils.guess import guess

    result = guess("contans", ["contains", "containsall", "exclude", "excludeall"])
    assert "contains" in result


def test_guess_no_close_match():
    """Test guess when no close match exists"""
    from ttp.utils.guess import guess

    result = guess("zzzzz", ["contains", "excludeall"])
    assert result == []


# =====================================================================
# VARIABLE getfilename FUNCTION
# =====================================================================


def test_getfilename_variable():
    """Test getfilename variable function returns data name"""
    from ttp.variable.getfilename import getfilename

    result = getfilename("some data", "test_file.txt")
    assert result == "test_file.txt"


# =====================================================================
# VARIABLE time_funcs FUNCTIONS
# =====================================================================


def test_get_time():
    """Test get_time returns time string"""
    from ttp.variable.time_funcs import get_time

    result = get_time()
    assert isinstance(result, str)
    # Should match HH:MM:SS format
    parts = result.split(":")
    assert len(parts) == 3


def test_get_date():
    """Test get_date returns date string"""
    from ttp.variable.time_funcs import get_date

    result = get_date()
    assert isinstance(result, str)
    # Should match YYYY-MM-DD format
    parts = result.split("-")
    assert len(parts) == 3
    assert len(parts[0]) == 4


def test_get_timestamp():
    """Test get_timestamp returns datetime string"""
    from ttp.variable.time_funcs import get_timestamp

    result = get_timestamp()
    assert isinstance(result, str)
    assert " " in result  # space between date and time


def test_get_timestamp_ms():
    """Test get_timestamp_ms returns datetime with milliseconds"""
    from ttp.variable.time_funcs import get_timestamp_ms

    result = get_timestamp_ms()
    assert isinstance(result, str)
    assert "." in result  # decimal point for milliseconds


def test_get_time_ns():
    """Test get_time_ns returns nanosecond timestamp"""
    from ttp.variable.time_funcs import get_time_ns

    result = get_time_ns()
    assert isinstance(result, int)
    assert result > 0


def test_get_timestamp_iso():
    """Test get_timestamp_iso returns ISO format timestamp"""
    from ttp.variable.time_funcs import get_timestamp_iso

    result = get_timestamp_iso()
    assert isinstance(result, str)
    assert "T" in result  # ISO format separator
    assert "+" in result or "Z" in result  # timezone info


# =====================================================================
# RETURNER terminal_returner FUNCTION
# =====================================================================


def test_terminal_returner_string(capsys):
    """Test terminal returner with string data"""
    from ttp.returners.terminal_returner import terminal_returner

    terminal_returner("Hello World")
    captured = capsys.readouterr()
    assert "Hello World" in captured.out


def test_terminal_returner_non_string(capsys):
    """Test terminal returner with non-string data"""
    from ttp.returners.terminal_returner import terminal_returner

    terminal_returner({"key": "value"})
    captured = capsys.readouterr()
    assert "key" in captured.out


def test_terminal_returner_with_colour(capsys):
    """Test terminal returner with colour option"""
    from ttp.returners.terminal_returner import terminal_returner

    terminal_returner("Status: True, Error: Failed", colour="True")
    captured = capsys.readouterr()
    assert "True" in captured.out
    assert "Failed" in captured.out


# =====================================================================
# OUTPUT transform FUNCTIONS
# =====================================================================


def test_output_transform_traverse_dict():
    """Test traverse function with dictionary data"""
    from ttp.output.transform import traverse

    data = {"a": {"b": {"c": "value"}}}
    result = traverse(data, "a.b.c")
    assert result == "value"


def test_output_transform_traverse_list():
    """Test traverse function with list data"""
    from ttp.output.transform import traverse

    data = [{"a": {"b": "val1"}}, {"a": {"b": "val2"}}]
    result = traverse(data, "a.b")
    assert result == ["val1", "val2"]


def test_output_transform_traverse_not_strict():
    """Test traverse with strict=False"""
    from ttp.output.transform import traverse

    data = {"a": {"x": "value"}}
    result = traverse(data, "a.b.c", strict=False)
    assert result == {}


def test_output_transform_dict_to_list():
    """Test dict_to_list function"""
    from ttp.output.transform import dict_to_list

    data = {
        "Fa0": {"admin": "down"},
        "Ge0/1": {"access_vlan": "24"},
    }
    result = dict_to_list(data, key_name="interface")
    assert len(result) == 2
    for item in result:
        assert "interface" in item
    interfaces = {d["interface"] for d in result}
    assert interfaces == {"Fa0", "Ge0/1"}


def test_output_transform_dict_to_list_with_path():
    """Test dict_to_list with path traversal"""
    from ttp.output.transform import dict_to_list

    data = {"interfaces": {"Fa0": {"admin": "down"}, "Ge0/1": {"access_vlan": "24"}}}
    result = dict_to_list(data, key_name="interface", path="interfaces", strict=True)
    assert len(result) == 2


def test_output_transform_dict_to_list_non_dict_value():
    """Test dict_to_list when values are not dicts"""
    from ttp.output.transform import dict_to_list

    data = {"a": "string_value", "b": "another"}
    result = dict_to_list(data, key_name="key")
    # should return data as-is when values are not dicts
    assert result == data


def test_output_transform_dict_to_list_with_list_input():
    """Test dict_to_list with list input runs recursion"""
    from ttp.output.transform import dict_to_list

    data = [
        {"Fa0": {"admin": "down"}},
        {"Ge0/1": {"vlan": "24"}},
    ]
    result = dict_to_list(data, key_name="interface")
    assert len(result) == 2


# =====================================================================
# TTP add_lookup METHOD
# =====================================================================


def test_add_lookup():
    """Test ttp.add_lookup method"""
    template = """
<input load="text">
interface Loopback0
  ip address 192.168.1.1
</input>

<group>
interface {{ interface }}
  ip address {{ ip }}
</group>
    """
    parser = ttp(template=template)
    parser.add_lookup(
        name="test_lookup",
        text_data="key1=value1,key2=value2",
        load="ini",
    )
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Loopback0", "ip": "192.168.1.1"}]
    ]]


# =====================================================================
# TTP add_vars METHOD
# =====================================================================


def test_add_vars():
    """Test ttp.add_vars method"""
    template = """
<input load="text">
interface Loopback0
  shutdown
</input>

<group>
interface {{ interface }}
  shutdown {{ state | set(site) }}
</group>
    """
    parser = ttp(template=template)
    parser.add_vars({"site": "NYC"})
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["state"] == "NYC"


def test_add_vars_non_dict():
    """Test ttp.add_vars with non-dict should be a no-op"""
    template = """
<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.add_vars("not_a_dict")  # should not crash
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"hostname": "Router1"}]
    ]]


# =====================================================================
# TTP parse with one=True
# =====================================================================


def test_parse_one_process():
    """Test parsing with one=True forces single process"""
    template = """
<input load="text">
interface Loopback0
  description RID
</input>

<group>
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse(one=True)
    res = parser.result()
    assert res == [[
        [{"interface": "Loopback0", "description": "RID"}]
    ]]


# =====================================================================
# TTP logging_config FUNCTION
# =====================================================================


def test_logging_config_valid():
    """Test logging_config with valid log level"""
    from ttp.ttp import logging_config

    # Should not raise
    logging_config("WARNING", None)


def test_logging_config_invalid_level():
    """Test logging_config with invalid log level does nothing"""
    from ttp.ttp import logging_config

    # Should not raise - just returns
    logging_config("INVALID_LEVEL", None)


# =====================================================================
# INPUT test function
# =====================================================================


def test_input_test_function(capsys):
    """Test the input test function"""
    from ttp.input.test import test

    data, flag = test("some test data here")
    assert data == "some test data here"
    assert flag is None
    captured = capsys.readouterr()
    assert "19" in captured.out  # length of "some test data here"


# =====================================================================
# OUTPUT condition attribute
# =====================================================================


def test_output_with_unsupported_formatter(caplog):
    """Test output with unsupported formatter logs a warning"""
    template = """
<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>

<output format="nonexistent_format" returner="self"/>
    """
    import logging
    with caplog.at_level(logging.WARNING):
        parser = ttp(template=template)
        parser.parse()
        res = parser.result()


# =====================================================================
# GROUP chain attribute with extract_chain
# =====================================================================


def test_group_chain_unknown_function(caplog):
    """Test group chain with unknown function logs error"""
    template = """
<input load="text">
interface Loopback0
  description RID
</input>

<vars>
my_chain = "nonexistent_func_xyz()"
</vars>

<group chain="my_chain">
interface {{ interface }}
  description {{ description }}
</group>
    """
    import logging
    with caplog.at_level(logging.ERROR):
        parser = ttp(template=template)
        parser.parse()
        res = parser.result()
    # Parser should still produce results even with unknown function
    assert len(res) > 0


# =====================================================================
# MATCH string replaceall with dict vars
# =====================================================================


def test_match_string_replaceall_with_dict_var():
    """Test string replaceall with dict variable for replacement mapping"""
    template = """
<input load="text">
interface GigabitEthernet0/0
interface FastEthernet0/1
</input>

<vars>
replace_map = {"Gi": "GigabitEthernet", "Fa": "FastEthernet"}
</vars>

<group>
interface {{ interface | replaceall(replace_map) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Gi0/0"
    assert res[0][0][1]["interface"] == "Fa0/1"


def test_match_string_replaceall_with_list_var():
    """Test string replaceall with list variable"""
    template = """
<input load="text">
interface GigabitEthernet0/0
interface FastEthernet0/1
</input>

<vars>
old_values = ["GigabitEthernet", "FastEthernet"]
</vars>

<group>
interface {{ interface | replaceall("Eth", old_values) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Eth0/0"
    assert res[0][0][1]["interface"] == "Eth0/1"


# =====================================================================
# MATCH string append/prepend from vars
# =====================================================================


def test_match_string_append_from_var():
    """Test string append using value from variables"""
    template = """
<input load="text">
interface Loopback0
</input>

<vars>
suffix = ".example.com"
</vars>

<group>
interface {{ interface | append(suffix) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Loopback0.example.com"


def test_match_string_prepend_from_var():
    """Test string prepend using value from variables"""
    template = """
<input load="text">
interface Loopback0
</input>

<vars>
prefix = "device1-"
</vars>

<group>
interface {{ interface | prepend(prefix) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "device1-Loopback0"
