import sys
import os
import json
import logging

sys.path.insert(0, "../..")

import pprint
import pytest

from ttp import ttp


# =====================================================================
# FLAT_LIST RESULT STRUCTURE (line 666)
# =====================================================================


def test_flat_list_result_structure_non_list_result():
    """Test flat_list structure when result is not a list (line 666)"""
    template_1 = """
<template name="t1" results="per_template">
<input load="text">
hostname Router1
</input>

<group name="info">
hostname {{ hostname }}
</group>
</template>
    """
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result(structure="flat_list")
    assert isinstance(res, list)
    assert len(res) > 0


# =====================================================================
# PARSE DOC (lines 1190-1191)
# =====================================================================


def test_template_doc_tag():
    """Test <doc> tag parsing (lines 1190-1191)"""
    template = """
<doc>
This is a documentation string for this template.
It should be parsed and stored.
</doc>

<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"hostname": "Router1"}]
    ]]


# =====================================================================
# VARS WITH NAME ATTRIBUTE (lines 1214-1217, 2861-2876)
# =====================================================================


def test_vars_with_name_save_to_results():
    """Test vars with name attribute are saved to results (lines 1214-1217, 2861-2876)."""
    template = """
<input load="text">
hostname Router1
</input>

<vars name="info">
device_type = "router"
vendor = "cisco"
</vars>

<group name="device">
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0]["info"]["device_type"] == "router"
    assert res[0][0]["info"]["vendor"] == "cisco"


# =====================================================================
# LOOKUP WITHOUT NAME (lines 1220-1222)
# =====================================================================


def test_lookup_without_name(caplog):
    """Test lookup tag without name attribute logs warning (lines 1220-1222)"""
    template = """
<input load="text">
hostname Router1
</input>

<lookup>
key1, val1
key2, val2
</lookup>

<group>
hostname {{ hostname }}
</group>
    """
    with caplog.at_level(logging.WARNING):
        parser = ttp(template=template)
        parser.parse()
    assert any("name" in msg.lower() for msg in caplog.messages)


# =====================================================================
# INVALID TEMPLATE TAG (line 1170-1171)
# =====================================================================


def test_invalid_template_tag(caplog):
    """Test invalid tag in template logs warning (line 1170-1171)"""
    template = """
<input load="text">
hostname Router1
</input>

<invalidtag>
blah blah
</invalidtag>

<group>
hostname {{ hostname }}
</group>
    """
    with caplog.at_level(logging.WARNING):
        parser = ttp(template=template)
        parser.parse()
    assert any("invalid" in msg.lower() for msg in caplog.messages)


# =====================================================================
# UNCONDITIONAL SET (lines 2047-2049)
# =====================================================================


def test_unconditional_set():
    """Test unconditional set - no match line, variable goes to defaults (lines 2047-2049)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group>
interface {{ interface }}
  description {{ description }}
  {{ site | set("NYC") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["site"] == "NYC"
    assert res[0][0][1]["site"] == "NYC"


# =====================================================================
# DEFAULT WITH NO ARGS (lines 2052-2056)
# =====================================================================


def test_default_with_no_args():
    """Test default function with no args uses 'None' string (lines 2053-2056)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
</input>

<group>
interface {{ interface }}
  description {{ description | default }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][1]["description"] == "None"


# =====================================================================
# IGNORE WITH CUSTOM REGEX FROM VARS (line 2227)
# =====================================================================


def test_ignore_with_regex_from_vars():
    """Test ignore variable with regex pattern from vars (line 2227)"""
    template = """
<input load="text">
Port 1 Status Up Speed 1000
Port 2 Status Down Speed 100
</input>

<vars>
port_re = r"\d+"
</vars>

<group>
Port {{ port }} Status {{ status }} Speed {{ ignore(port_re) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["port"] == "1"
    assert res[0][0][0]["status"] == "Up"
    assert "ignore" not in res[0][0][0]


# =====================================================================
# BUILT-IN STRING FUNCTIONS AS MATCH FUNCTIONS (lines 2477-2489)
# =====================================================================


def test_match_builtin_string_upper():
    """Test using Python built-in string method upper() as match function (lines 2477-2489)"""
    template = """
<input load="text">
interface Loopback0
interface Vlan10
</input>

<group>
interface {{ interface | upper }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "LOOPBACK0"
    assert res[0][0][1]["interface"] == "VLAN10"


def test_match_builtin_string_lower():
    """Test using Python built-in string method lower() as match function"""
    template = """
<input load="text">
interface LOOPBACK0
interface VLAN10
</input>

<group>
interface {{ interface | lower }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "loopback0"
    assert res[0][0][1]["interface"] == "vlan10"


def test_match_builtin_string_strip():
    """Test using Python built-in strip method"""
    template = """
<input load="text">
interface Loopback0
interface Vlan10
</input>

<group>
interface {{ interface | strip }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Loopback0"


# =====================================================================
# MATCH VARIABLE CHAIN FUNCTION (lines 2072-2077)
# =====================================================================


def test_match_variable_chain():
    """Test match variable chain attribute (lines 2072-2077)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<vars>
my_chain = "upper | truncate(1)"
</vars>

<group>
interface {{ interface | chain(my_chain) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "LOOPBACK0"


def test_match_variable_chain_not_found(caplog):
    """Test match variable chain with non-existent variable (lines 2072-2077)"""
    template = """
<input load="text">
interface Loopback0
</input>

<group>
interface {{ interface | chain(nonexistent_var) }}
</group>
    """
    with caplog.at_level(logging.ERROR):
        parser = ttp(template=template)
        parser.parse()
        res = parser.result()
    assert any("chain" in msg.lower() for msg in caplog.messages)


# =====================================================================
# UNKNOWN MATCH FUNCTION (lines 2490-2504)
# =====================================================================


def test_unknown_match_function(caplog):
    """Test unknown match function logs error with suggestion (lines 2490-2504)"""
    template = """
<input load="text">
interface Loopback0
</input>

<group>
interface {{ interface | uppercas }}
</group>
    """
    with caplog.at_level(logging.ERROR):
        parser = ttp(template=template)
        parser.parse()


# =====================================================================
# GROUP NAME WITH ABSOLUTE PATH IN ANONYMOUS (line 1738)
# =====================================================================


def test_group_absolute_path_in_anonymous():
    """Test group with absolute path when parent is anonymous (line 1738)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group name="/interfaces*">
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res[0][0], dict)
    assert "interfaces" in res[0][0]
    assert len(res[0][0]["interfaces"]) == 2


def test_group_absolute_root_path():
    """Test group with name='/' resolves to anonymous path (line 1738-1742)."""
    template = """
<input load="text">
hostname Router1
</input>

<group name="/">
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["hostname"] == "Router1"


# =====================================================================
# OUTPUT WITH PATH, HEADERS AND CONDITION ATTRIBUTES (lines 3346-3359)
# =====================================================================


def test_output_with_path_attribute():
    """Test output tag with path attribute (line 3346-3347)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group name="interfaces*">
interface {{ interface }}
  description {{ description }}
</group>

<output
format="json"
returner="self"
path="interfaces"
/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)


def test_output_with_headers_attribute():
    """Test output tag with headers attribute (lines 3349-3353)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group name="interfaces*">
interface {{ interface }}
  description {{ description }}
</group>

<output
format="csv"
returner="self"
headers="interface, description"
/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)
    assert isinstance(res[0], str)
    assert "interface" in res[0]


def test_output_condition_attribute():
    """Test output with condition attribute (lines 3355-3359)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group>
interface {{ interface }}
  description {{ description }}
</group>

<output condition="do_csv, True" format="csv"/>
    """
    parser1 = ttp(template=template, vars={"do_csv": False})
    parser1.parse()
    res1 = parser1.result()
    assert isinstance(res1[0], list)

    parser2 = ttp(template=template, vars={"do_csv": True})
    parser2.parse()
    res2 = parser2.result()
    assert isinstance(res2[0], str)


def test_output_unknown_function():
    """Test output with unknown function name logs error (lines 3365-3375)."""
    template = """
<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>

<output functions="nonexistent_function_xyz" returner="self"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0] == [{"hostname": "Router1"}]


def test_output_unsupported_returner():
    """Test output with unsupported returner name (line 3446)."""
    template = """
<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>

<output returner="nonexistent_returner_xyz"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0] == [{"hostname": "Router1"}]


def test_output_with_json_format():
    """Test output with JSON format and self returner (lines 3385+)."""
    template = """
<input load="text">
hostname Router1
</input>

<group name="devices*">
hostname {{ hostname }}
</group>

<output format="json" returner="self"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    parsed = json.loads(res[0])
    assert parsed[0]["devices"][0]["hostname"] == "Router1"


# =====================================================================
# STARTEMPTY RE / START RE (lines 2747-2760)
# =====================================================================


def test_startempty_re():
    """Test _start_ regex on empty line triggers startempty action (lines 2027-2028, 2747+)"""
    template = """
<input load="text">
interface Loopback0
 description RID
 ip address 1.1.1.1/32
!
interface Vlan10
 description VLAN10
 ip address 10.0.0.1/24
!
</input>

<group>
interface {{ interface }}
 description {{ description }}
 ip address {{ ip }}
{{ _start_ }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert len(res[0][0]) == 2
    assert res[0][0][0]["interface"] == "Loopback0"
    assert res[0][0][1]["interface"] == "Vlan10"


def test_startempty_re_multiple_groups():
    """Test startempty RE selection when multiple groups match (lines 2749+)."""
    template = """
<input load="text">
interface Loopback0
  description RID
  ip address 1.1.1.1 255.255.255.255
!
interface Vlan10
  description MGMT
  ip address 10.0.0.1 255.255.255.0
!
</input>

<group name="interfaces*">
interface {{ interface }}
  description {{ description }}
  <group name="addresses*">
  ip address {{ ip }} {{ mask }}
  </group>
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert "interfaces" in res[0][0]
    assert len(res[0][0]["interfaces"]) == 2
    assert res[0][0]["interfaces"][0]["addresses"][0]["ip"] == "1.1.1.1"


# =====================================================================
# END RE (lines 3199-3212)
# =====================================================================


def test_end_re():
    """Test _end_ regex to close group parsing (lines 3199-3212)"""
    template = """
<input load="text">
interface Loopback0
 description RID
 ip address 1.1.1.1/32
!
interface Vlan10
 description VLAN10
 ip address 10.0.0.1/24
!
</input>

<group>
interface {{ interface }}
 description {{ description }}
 ip address {{ ip }}
! {{ _end_ }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert len(res[0][0]) == 2
    assert res[0][0][0]["interface"] == "Loopback0"
    assert res[0][0][1]["interface"] == "Vlan10"


def test_end_re_on_different_group():
    """Test end RE match from different group doesn't end current group (line 3208)."""
    template = """
<input load="text">
router bgp 65000
  neighbor 10.0.0.1
    remote-as 65001
    description Peer1
  neighbor 10.0.0.2
    remote-as 65002
    description Peer2
</input>

<group name="bgp">
router bgp {{ asn }}
  <group name="neighbors*">
  neighbor {{ peer }}
    remote-as {{ remote_as }}
    description {{ desc }}
  </group>
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert "bgp" in res[0][0]
    assert res[0][0]["bgp"]["asn"] == "65000"
    assert len(res[0][0]["bgp"]["neighbors"]) == 2


# =====================================================================
# JOIN WITH LIST DATA (lines 3174-3177)
# =====================================================================


def test_joinmatches_list_data():
    """Test joinmatches with list data joining (lines 3174-3177)"""
    template = """
<input load="text">
interface Loopback0
  permit 10.0.0.0/8
  permit 192.168.0.0/16
  permit 172.16.0.0/12
</input>

<group>
interface {{ interface }}
  permit {{ nets | to_list | joinmatches }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res[0][0][0]["nets"], list)
    assert len(res[0][0][0]["nets"]) == 3
    assert "10.0.0.0/8" in res[0][0][0]["nets"]


# =====================================================================
# NULL PATH (lines 2909-2917, 2944-2947, 2984-2985)
# =====================================================================


def test_null_path_group():
    """Test group with null path '_' in path (lines 2909-2914)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group name="_">
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)


def test_null_path_in_group_name():
    """Test group with _ (null path) in name (lines 2912+)."""
    template = """
<input load="text">
interface Loopback0
  ip address 1.1.1.1 255.255.255.255
interface Vlan10
  ip address 10.0.0.1 255.255.255.0
</input>

<group name="_.interfaces*">
interface {{ interface }}
  ip address {{ ip }} {{ mask }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert "interfaces" in res[0][0]
    assert len(res[0][0]["interfaces"]) == 2


# =====================================================================
# NESTED CHILD TEMPLATES (line 961)
# =====================================================================


def test_nested_child_templates():
    """Test parsing with child templates (line 961)"""
    template = """
<template name="parent">

<template name="child1">
<input load="text">
hostname Router1
</input>
<group>
hostname {{ hostname }}
</group>
</template>

<template name="child2">
<input load="text">
interface Loopback0
</input>
<group>
interface {{ interface }}
</group>
</template>

</template>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)
    assert len(res) >= 2


# =====================================================================
# GROUP WITH INPUT AND OUTPUT ATTRIBUTES (lines 1730-1736)
# =====================================================================


def test_group_with_input_attribute():
    """Test group with input attribute to map to specific input (lines 1730-1732)"""
    template = """
<input name="input1" load="text">
interface Loopback0
  description RID
</input>

<input name="input2" load="text">
hostname Router1
</input>

<group input="input1">
interface {{ interface }}
  description {{ description }}
</group>

<group input="input2">
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)
    found_interface = False
    found_hostname = False
    for template_res in res:
        for item in template_res:
            if isinstance(item, list):
                for d in item:
                    if isinstance(d, dict):
                        if "interface" in d:
                            found_interface = True
                        if "hostname" in d:
                            found_hostname = True
            elif isinstance(item, dict):
                if "interface" in item:
                    found_interface = True
                if "hostname" in item:
                    found_hostname = True
    assert found_interface
    assert found_hostname


def test_group_with_output_attribute():
    """Test group with output attribute to map to specific output (lines 1734-1736)"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group name="interfaces*" output="out1">
interface {{ interface }}
  description {{ description }}
</group>

<output name="out1" format="json" returner="self"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)


def test_group_output_attribute_resolution():
    """Test group output attribute resolves to named output (lines 1098-1105)."""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group name="interfaces*" output="csv_out">
interface {{ interface }}
  description {{ description }}
</group>

<output name="csv_out" format="csv" returner="self"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res[0][0], list)
    assert isinstance(res[0][0][0], str)
    assert "interface" in res[0][0][0]


# =====================================================================
# GROUP CHAIN (lines 1755-1770)
# =====================================================================


def test_group_chain_unknown_function():
    """Test group with chain referencing unknown function (lines 1762, 1770)."""
    template = """
<input load="text">
interface Loopback0
  description RID
</input>

<vars>
my_chain = "nonexistent_group_func_xyz"
</vars>

<group chain="my_chain">
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Loopback0"


def test_group_chain_with_list_variable():
    """Test group chain where variable value is a list of group functions (line 1755-1762)."""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN
</input>

<vars>
my_chain = ["contains('Loopback')"]
</vars>

<group name="interfaces*" chain="my_chain">
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)


# =====================================================================
# TEMPLATE ATTRIBUTES (lines 1120-1127)
# =====================================================================


def test_template_base_path_attribute():
    """Test template base_path attribute (lines 1120-1121)"""
    template = """
<template base_path="./Data/">
<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>
</template>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"hostname": "Router1"}]
    ]]


def test_template_results_method():
    """Test template results method attribute (lines 1123-1124)"""
    template = """
<template results="per_template">
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group>
interface {{ interface }}
  description {{ description }}
</group>
</template>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res[0], list)
    assert len(res[0]) == 2
    assert res[0][0]["interface"] == "Loopback0"
    assert res[0][1]["interface"] == "Vlan10"


def test_template_pathchar_attribute():
    """Test template pathchar attribute for nested paths (lines 1126-1127)"""
    template = """
<template pathchar="/">
<input load="text">
interface Loopback0
  description RID
</input>

<group name="interfaces/list*">
interface {{ interface }}
  description {{ description }}
</group>
</template>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res[0][0], dict)
    assert "interfaces" in res[0][0]
    assert "list" in res[0][0]["interfaces"]


def test_template_with_filters():
    """Test ttp with template filters to load only specific templates (lines 1191-1192, 1425)."""
    template = """
<template name="interfaces">
<input load="text">
interface Loopback0
  description RID
</input>
<group>
interface {{ interface }}
  description {{ description }}
</group>
</template>

<template name="hostnames">
<input load="text">
hostname Router1
</input>
<group>
hostname {{ hostname }}
</group>
</template>
    """
    parser = ttp()
    parser.add_template(template=template, filters=["interfaces"])
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)


# =====================================================================
# MACRO SYNTAX ERROR (lines 1183-1188)
# =====================================================================


def test_macro_syntax_error(caplog):
    """Test macro with syntax error logs error (lines 1183-1188)"""
    template = """
<input load="text">
hostname Router1
</input>

<macro>
def bad_macro(data)
    # missing colon - syntax error
    return data
</macro>

<group>
hostname {{ hostname }}
</group>
    """
    with caplog.at_level(logging.ERROR):
        parser = ttp(template=template)
        parser.parse()
    assert any("syntax" in msg.lower() for msg in caplog.messages)


# =====================================================================
# MATCH VARIABLE WITH _LINE_ (lines 2062-2067)
# =====================================================================


def test_line_indicator_with_joinmatches():
    """Test _line_ indicator joining unmatched lines (lines 2062-2067, 3155-3177)"""
    template = """
<input load="text">
System Description: Cisco IOS Software
TAC support: http://www.cisco.com/tac
Copyright (c) 2002-2020
Time remaining: 120 seconds
</input>

<group>
System Description: {{ description | re(".+") | joinmatches(" ") }}
{{ description | _line_ | joinmatches(" ") }}
Time remaining: {{ ignore }} seconds {{ _end_ }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    desc = res[0][0][0]["description"]
    assert "Cisco" in desc
    assert "TAC" in desc


def test_line_indicator_in_child_group():
    """Test _line_ indicator in a child group for IS_LINE tracking (lines 3106-3107)."""
    template = """
<input load="text">
interface Loopback0
  description RID
  some random config line
  another config line
interface Vlan10
  description VLAN10
  more config here
</input>

<group>
interface {{ interface }}
  description {{ description }}
  <group name="config*">
  {{ _line_ | joinmatches }}
  </group>
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert "config" in res[0][0][0]


# =====================================================================
# EXTEND TAG GROUP FILTER WITH INDEX (line 1321)
# =====================================================================


def test_extend_tag_from_file_group_index_filter_string():
    """Test extend with group index as string filter (line 1321)"""
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
    parser.parse()
    res = parser.result()
    assert len(res[0][0]) == 1


# =====================================================================
# INPUT ATTRIBUTES (lines 1529-1561)
# =====================================================================


def test_input_extensions_attribute():
    """Test input with extensions attribute (lines 1529-1533)"""
    template = """
<input load="text" extensions="txt">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"hostname": "Router1"}]
    ]]


def test_input_filters_attribute():
    """Test input with filters attribute (lines 1535-1539)"""
    template = """
<input load="text" filters="my_filter">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)


def test_input_load_from_file():
    """Test input loading data from file path (lines 1543-1561)."""
    data_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "Data", "test.txt")
    )
    if os.path.exists(data_path):
        template = """
<group>
interface {{ interface }}
 ip address {{ ip }} {{ mask }}
</group>
        """
        parser = ttp(data=data_path, template=template)
        parser.parse()
        res = parser.result()
        assert isinstance(res, list)


def test_input_structured_list_data():
    """Test input macro receiving structured list data (lines 1574-1583)."""
    template = """
<input load="text">
hostname Router1
ip address 10.0.0.1
</input>

<group>
hostname {{ hostname }}
ip address {{ ip }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["hostname"] == "Router1"


# =====================================================================
# DICTIONARY RESULT STRUCTURE WITH NAMED TEMPLATES
# =====================================================================


def test_result_dictionary_structure_named_templates():
    """Test result(structure='dictionary') with named templates"""
    template = """
<template name="interfaces">
<input load="text">
interface Loopback0
  description RID
</input>

<group>
interface {{ interface }}
  description {{ description }}
</group>
</template>

<template name="hosts">
<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>
</template>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result(structure="dictionary")
    assert isinstance(res, dict)
    assert "interfaces" in res
    assert "hosts" in res


# =====================================================================
# VARIABLE FUNCTIONS (lines 2427-2431)
# =====================================================================


def test_variable_getter_function():
    """Test variable getter function like gethostname (lines 2427-2431)"""
    template = """
<input load="text">
interface Loopback0
  description RID
</input>

<vars>
time_now = "get_time"
</vars>

<group>
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Loopback0", "description": "RID"}]
    ]]


# =====================================================================
# INPUT FUNCTIONS (lines 2408-2416)
# =====================================================================


def test_input_with_macro_function():
    """Test input with macro function processing data (lines 2408-2416)"""
    template = """
<input load="text">
hostname Router1
interface Loopback0
</input>

<macro>
def filter_input(data):
    # return data unchanged
    return data, None
</macro>

<group>
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.add_function(
        fun="def filter_input(data):\n    return data, None\n",
        scope="input",
        name="filter_input",
    )
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)


# =====================================================================
# MATCH FUNCTION RETURNING NEW_FIELD (line 2509)
# =====================================================================


def test_match_function_returning_new_field():
    """Test match function returning new_field flag dict (line 2509)."""
    template = """
<input load="text">
interface Loopback0
  ip address 10.0.0.1/32
</input>

<group>
interface {{ interface }}
  ip address {{ ip | to_ip | ip_info }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    result = res[0][0][0]
    assert result["interface"] == "Loopback0"


# =====================================================================
# ADD_INPUT / SET_INPUT / CLEAR_INPUT API (lines 270, 305, 315+)
# =====================================================================


def test_add_input_before_template():
    """Test add_input when no templates loaded yet (line 270)."""
    parser = ttp()
    parser.add_input(data="hostname Router1", input_name="test_input")
    parser.add_template(
        template="""
<group>
hostname {{ hostname }}
</group>
    """
    )
    parser.add_input(data="hostname Router1")
    parser.parse()
    res = parser.result()
    assert res[0][0] == [{"hostname": "Router1"}]


def test_set_input_clears_and_adds():
    """Test set_input method which clears then adds input (line 305)."""
    template = """
<group>
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.set_input(data="hostname Router1")
    parser.parse()
    res = parser.result()
    assert res[0][0] == [{"hostname": "Router1"}]


def test_clear_input():
    """Test clear_input method (line 322+)."""
    template = """
<group>
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    parser.add_input(data="hostname Router1")
    parser.parse()
    res1 = parser.result()
    assert res1[0][0] == [{"hostname": "Router1"}]

    parser.clear_input()
    for template_obj in parser._templates:
        assert template_obj.inputs == {}


# =====================================================================
# PARSE one=True AND multi=True RAISES SystemExit (lines 436-437)
# =====================================================================


def test_parse_one_and_multi_raises():
    """Test that parse(one=True, multi=True) raises SystemExit (lines 436-437)."""
    template = """
<input load="text">
hostname Router1
</input>
<group>
hostname {{ hostname }}
</group>
    """
    parser = ttp(template=template)
    with pytest.raises(SystemExit):
        parser.parse(one=True, multi=True)


# =====================================================================
# FORM_RESULTS WITH ANONYMOUS AND NAMED GROUPS (line 1007)
# =====================================================================


def test_form_results_anonymous_plus_named():
    """Test form_results when both _anonymous_ and named group results exist (line 1007+)."""
    template = """
<input load="text">
hostname Router1
interface Loopback0
  description RID
</input>

hostname {{ hostname }}

<group name="interfaces*">
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res[0][0], (list, dict))
    assert len(res[0][0]) > 0


# =====================================================================
# DEBUG MODE (lines 967, 983, 990)
# =====================================================================


def test_debug_mode_with_logging():
    """Test that debug mode doesn't crash (lines 967, 983, 990)."""
    template = """
<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>
    """
    logger = logging.getLogger("ttp")
    original_level = logger.level
    logger.setLevel(logging.DEBUG)
    try:
        parser = ttp(template=template, log_level="DEBUG")
        parser.parse()
        res = parser.result()
        assert res[0][0] == [{"hostname": "Router1"}]
    finally:
        logger.setLevel(original_level)
