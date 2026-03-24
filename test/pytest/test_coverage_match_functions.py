import sys

sys.path.insert(0, "../..")
import pprint
import json
import pytest

from ttp import ttp


# =====================================================================
# MATCH void FUNCTION
# =====================================================================


def test_match_void():
    """Test void function - invalidates match results"""
    template = """
<input load="text">
interface Loopback0
  description RID
  mtu 1500
</input>

<group>
interface {{ interface }}
  description {{ description | void }}
  mtu {{ mtu }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # description should be voided
    assert res == [[
        [{"interface": "Loopback0", "mtu": "1500"}]
    ]]


# =====================================================================
# MATCH count FUNCTION  
# =====================================================================


def test_match_count_var():
    """Test count function with var - counts matches in template variable"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
interface Vlan20
  description VLAN20
</input>

<group>
interface {{ interface | count(var="intf_count") }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert len(res[0][0]) == 3


def test_match_count_globvar():
    """Test count function with globvar - counts matches in global variable"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
</input>

<group>
interface {{ interface | count(globvar="global_count") }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert len(res[0][0]) == 2


# =====================================================================
# MATCH mac_eui FUNCTION
# =====================================================================


def test_match_mac_eui_colon_format():
    """Test mac_eui function - converts colon-separated MAC to EUI"""
    template = """
<input load="text">
interface Eth1
  mac 00:80:41:ae:fd:7e
</input>

<group>
interface {{ interface }}
  mac {{ mac | mac_eui }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Eth1", "mac": "00:80:41:ae:fd:7e"}]
    ]]


def test_match_mac_eui_dot_format():
    """Test mac_eui function - converts dot-separated MAC to EUI"""
    template = """
<input load="text">
interface Eth1
  mac 0080.41ae.fd7e
</input>

<group>
interface {{ interface }}
  mac {{ mac | mac_eui }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Eth1", "mac": "00:80:41:ae:fd:7e"}]
    ]]


def test_match_mac_eui_hyphen_format():
    """Test mac_eui function - converts hyphen-separated MAC to EUI"""
    template = """
<input load="text">
interface Eth1
  mac 00-80-41-AE-FD-7E
</input>

<group>
interface {{ interface }}
  mac {{ mac | mac_eui }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Eth1", "mac": "00:80:41:ae:fd:7e"}]
    ]]


def test_match_mac_eui_short_mac():
    """Test mac_eui function - handles short MAC by padding with zeros"""
    template = """
<input load="text">
interface Eth1
  mac 0080.41ae.fd7
</input>

<group>
interface {{ interface }}
  mac {{ mac | mac_eui }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # short MAC should be padded with zeros
    assert "mac" in res[0][0][0]


# =====================================================================
# MATCH uptimeparse FUNCTION
# =====================================================================


def test_match_uptimeparse_seconds():
    """Test uptimeparse returns seconds by default"""
    template = """
<input load="text">
uptime 2 years, 27 weeks, 3 days, 10 hours, 46 minutes
</input>

<group>
uptime {{ uptime | ORPHRASE | uptimeparse }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # Calculate expected: 2*365*86400 + 27*7*86400 + 3*86400 + 10*3600 + 46*60
    expected = 2 * 365 * 86400 + 27 * 7 * 86400 + 3 * 86400 + 10 * 3600 + 46 * 60
    assert res == [[
        [{"uptime": expected}]
    ]]


def test_match_uptimeparse_dict_format():
    """Test uptimeparse returns dict when format is dict"""
    template = """
<input load="text">
uptime 3 days, 5 hours, 30 minutes
</input>

<group>
uptime {{ uptime | ORPHRASE | uptimeparse(format="dict") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    uptime = res[0][0][0]["uptime"]
    assert isinstance(uptime, dict)
    assert uptime["days"] == "3"
    assert uptime["hours"] == "5"
    assert uptime["mins"] == "30"


def test_match_uptimeparse_no_match():
    """Test uptimeparse with non-matching string returns original"""
    template = """
<input load="text">
uptime not_a_time_string
</input>

<group>
uptime {{ uptime | uptimeparse }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"uptime": "not_a_time_string"}]
    ]]


# =====================================================================
# MATCH string functions
# =====================================================================


def test_match_string_exclude():
    """Test string exclude function"""
    template = """
<input load="text">
interface Loopback0
interface Vlan10
interface GigabitEthernet0/0
</input>

<group>
interface {{ interface | exclude("Vlan") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    interfaces = [d["interface"] for d in res[0][0]]
    assert "Vlan10" not in interfaces
    assert "Loopback0" in interfaces


def test_match_string_equal():
    """Test string equal function"""
    template = """
<input load="text">
status up
status down
status up
</input>

<group>
status {{ status | equal("up") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert all(d["status"] == "up" for d in res[0][0])


def test_match_string_notequal():
    """Test string notequal function"""
    template = """
<input load="text">
status up
status down
status up
</input>

<group>
status {{ status | notequal("up") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert all(d["status"] == "down" for d in res[0][0])


def test_match_string_contains():
    """Test string contains function"""
    template = """
<input load="text">
interface GigabitEthernet0/0
interface Loopback0
interface FastEthernet0/1
</input>

<group>
interface {{ interface | contains("Ethernet") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    interfaces = [d["interface"] for d in res[0][0]]
    assert "GigabitEthernet0/0" in interfaces
    assert "FastEthernet0/1" in interfaces
    assert "Loopback0" not in interfaces


def test_match_string_isdigit():
    """Test string isdigit function"""
    template = """
<input load="text">
vlan 100
vlan abc
vlan 200
</input>

<group>
vlan {{ id | isdigit }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    ids = [d["id"] for d in res[0][0]]
    assert "100" in ids
    assert "200" in ids
    assert "abc" not in ids


def test_match_string_notdigit():
    """Test string notdigit function"""
    template = """
<input load="text">
tag 100
tag abc
tag 200
</input>

<group>
tag {{ id | notdigit }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    ids = [d["id"] for d in res[0][0]]
    assert "abc" in ids
    assert "100" not in ids


def test_match_string_greaterthan():
    """Test string greaterthan function"""
    template = """
<input load="text">
vlan 100
vlan 500
vlan 50
</input>

<group>
vlan {{ id | greaterthan("200") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"id": "500"}]
    ]]


def test_match_string_lessthan():
    """Test string lessthan function"""
    template = """
<input load="text">
vlan 100
vlan 500
vlan 50
</input>

<group>
vlan {{ id | lessthan("200") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    ids = [d["id"] for d in res[0][0]]
    assert "100" in ids
    assert "50" in ids
    assert "500" not in ids


def test_match_string_join():
    """Test string join function with joinmatches"""
    template = """
<input load="text">
permit 10.0.0.0/8
permit 192.168.0.0/16
permit 172.16.0.0/12
</input>

<group>
permit {{ net | joinmatches(",") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert "10.0.0.0/8" in res[0][0][0]["net"]


def test_match_string_append():
    """Test string append function"""
    template = """
<input load="text">
interface Loopback0
interface Vlan10
</input>

<group>
interface {{ interface | append(" (found)") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Loopback0 (found)"


def test_match_string_prepend():
    """Test string prepend function"""
    template = """
<input load="text">
interface Loopback0
interface Vlan10
</input>

<group>
interface {{ interface | prepend("intf: ") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "intf: Loopback0"


def test_match_string_replaceall_simple():
    """Test string replaceall function - simple replacement"""
    template = """
<input load="text">
interface GigabitEthernet0/0
interface FastEthernet0/1
</input>

<group>
interface {{ interface | replaceall("Ethernet") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Gigabit0/0"
    assert res[0][0][1]["interface"] == "Fast0/1"


def test_match_string_truncate():
    """Test string truncate function"""
    template = """
<input load="text">
description this is a very long description text
</input>

<group>
description {{ description | ORPHRASE | truncate(3) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["description"] == "this is a"


# =====================================================================
# MATCH to functions
# =====================================================================


def test_match_to_str():
    """Test to_str function"""
    template = """
<input load="text">
vlan 100
</input>

<group>
vlan {{ id | to_int | to_str }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["id"] == "100"
    assert isinstance(res[0][0][0]["id"], str)


def test_match_to_list():
    """Test to_list function"""
    template = """
<input load="text">
interface Loopback0
</input>

<group>
interface {{ interface | to_list }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == ["Loopback0"]


def test_match_to_int_valid():
    """Test to_int function with valid integer"""
    template = """
<input load="text">
vlan 100
</input>

<group>
vlan {{ id | to_int }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["id"] == 100
    assert isinstance(res[0][0][0]["id"], int)


def test_match_to_int_invalid():
    """Test to_int function with invalid value - returns original"""
    template = """
<input load="text">
vlan abc
</input>

<group>
vlan {{ id | to_int }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # should return original string since conversion fails
    assert res[0][0][0]["id"] == "abc"


def test_match_to_float():
    """Test to_float function"""
    template = """
<input load="text">
metric 3.14
</input>

<group>
metric {{ value | to_float }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["value"] == 3.14
    assert isinstance(res[0][0][0]["value"], float)


# =====================================================================
# MATCH item FUNCTION
# =====================================================================


def test_match_item_first():
    """Test item function to get first item"""
    template = """
<input load="text">
route 10.0.0.0/8 via 192.168.1.1
</input>

<group>
route {{ route }} via {{ nexthop | item(0) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # item(0) on a string returns first character
    assert res[0][0][0]["nexthop"] == "1"


def test_match_item_negative_index():
    """Test item function with negative index"""
    template = """
<input load="text">
route 10.0.0.0/8 via 192.168.1.1
</input>

<group>
route {{ route }} via {{ nexthop | item(-1) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # item(-1) on "192.168.1.1" returns last character "1"
    assert res[0][0][0]["nexthop"] == "1"


# =====================================================================
# MATCH ip functions
# =====================================================================


def test_match_to_ip_v4_address():
    """Test to_ip match function with IPv4 address"""
    template = """
<input load="text">
interface Loopback0
  ip address 192.168.1.1
</input>

<group>
interface {{ interface }}
  ip address {{ ip | to_ip }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res[0][0][0]["ip"] == ipaddress.ip_address("192.168.1.1")


def test_match_to_ip_v4_interface():
    """Test to_ip match function with IPv4 interface (CIDR)"""
    template = """
<input load="text">
interface Loopback0
  ip address 192.168.1.1/24
</input>

<group>
interface {{ interface }}
  ip address {{ ip | to_ip }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res[0][0][0]["ip"] == ipaddress.ip_interface("192.168.1.1/24")


def test_match_to_ip_v4_explicit():
    """Test to_ip match function with explicit ipv4 argument"""
    template = """
<input load="text">
interface Loopback0
  ip address 10.0.0.1/30
</input>

<group>
interface {{ interface }}
  ip address {{ ip | to_ip("ipv4") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res[0][0][0]["ip"] == ipaddress.IPv4Interface("10.0.0.1/30")


def test_match_to_ip_v6():
    """Test to_ip match function with IPv6"""
    template = """
<input load="text">
interface Loopback0
  ipv6 address 2001:db8::1/64
</input>

<group>
interface {{ interface }}
  ipv6 address {{ ip | to_ip("ipv6") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res[0][0][0]["ip"] == ipaddress.IPv6Interface("2001:db8::1/64")


def test_match_to_ip_v6_address_only():
    """Test to_ip match function with IPv6 address without prefix"""
    template = """
<input load="text">
interface Loopback0
  ipv6 address 2001:db8::1
</input>

<group>
interface {{ interface }}
  ipv6 address {{ ip | to_ip("ipv6") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res[0][0][0]["ip"] == ipaddress.IPv6Address("2001:db8::1")


def test_match_is_ip_valid():
    """Test is_ip match function with valid IP"""
    template = """
<input load="text">
address 192.168.1.1
address not_an_ip
address 10.0.0.1
</input>

<group>
address {{ ip | is_ip }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    ips = [d["ip"] for d in res[0][0]]
    assert "192.168.1.1" in ips
    assert "10.0.0.1" in ips
    assert "not_an_ip" not in ips


def test_match_to_net():
    """Test to_net match function"""
    template = """
<input load="text">
network 192.168.0.0/24
</input>

<group>
network {{ net | to_net }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res[0][0][0]["net"] == ipaddress.ip_network("192.168.0.0/24")


def test_match_to_net_v4_explicit():
    """Test to_net with explicit ipv4 argument"""
    template = """
<input load="text">
network 10.0.0.0/8
</input>

<group>
network {{ net | to_net("ipv4") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res[0][0][0]["net"] == ipaddress.IPv4Network("10.0.0.0/8")


def test_match_to_net_v6():
    """Test to_net with explicit ipv6 argument"""
    template = """
<input load="text">
network 2001:db8::/32
</input>

<group>
network {{ net | to_net("ipv6") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res[0][0][0]["net"] == ipaddress.IPv6Network("2001:db8::/32")


def test_match_to_cidr():
    """Test to_cidr converts subnet mask to CIDR prefix length"""
    template = """
<input load="text">
interface Loopback0
  mask 255.255.255.0
interface Vlan10
  mask 255.255.0.0
</input>

<group>
interface {{ interface }}
  mask {{ mask | to_cidr }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["mask"] == 24
    assert res[0][0][1]["mask"] == 16


def test_match_to_cidr_invalid():
    """Test to_cidr with invalid mask returns original"""
    template = """
<input load="text">
mask not_a_mask
</input>

<group>
mask {{ mask | to_cidr }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["mask"] == "not_a_mask"


def test_match_ip_info_interface():
    """Test ip_info function with interface address"""
    template = """
<input load="text">
address 192.168.1.1/24
</input>

<group>
address {{ ip | to_ip | ip_info }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    info = res[0][0][0]["ip"]
    assert isinstance(info, dict)
    assert info["version"] == 4
    assert "netmask" in info
    assert "network" in info
    assert info["prefixlen"] == 24


def test_match_ip_info_address_only():
    """Test ip_info function with plain address (no prefix)"""
    template = """
<input load="text">
address 10.0.0.1
</input>

<group>
address {{ ip | to_ip | ip_info }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    info = res[0][0][0]["ip"]
    assert isinstance(info, dict)
    assert info["version"] == 4
    assert info["ip"] == "10.0.0.1"
    assert "is_loopback" in info


def test_match_cidr_match():
    """Test cidr_match function"""
    template = """
<input load="text">
address 192.168.1.1/24
address 10.0.0.1/8
address 172.16.0.1/12
</input>

<group>
address {{ ip | to_ip | cidr_match("192.168.0.0/16") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert len(res[0][0]) == 1
    assert res[0][0][0]["ip"] == ipaddress.ip_interface("192.168.1.1/24")


def test_match_cidr_match_with_plain_address():
    """Test cidr_match with plain IP address (no prefix)"""
    template = """
<input load="text">
address 192.168.1.1
address 10.0.0.1
</input>

<group>
address {{ ip | to_ip | cidr_match("192.168.0.0/16") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert len(res[0][0]) == 1


# =====================================================================
# MATCH re_ functions (uncovered branches)
# =====================================================================


def test_match_resub_with_vars():
    """Test resub using pattern from vars"""
    template = """
<input load="text">
interface GigabitEthernet0/0
interface FastEthernet0/1
</input>

<vars>
old_pattern = "Ethernet"
</vars>

<group>
interface {{ interface | resub(old="old_pattern", new="Eth") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "GigabitEth0/0"


def test_match_resuball_with_list_var():
    """Test resuball with a list variable"""
    template = """
<input load="text">
interface GigabitEthernet0/0
interface FastEthernet0/1
</input>

<vars>
old_patterns = ["GigabitEthernet", "FastEthernet"]
</vars>

<group>
interface {{ interface | resuball("Eth", old_patterns) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Eth0/0"
    assert res[0][0][1]["interface"] == "Eth0/1"


def test_match_resuball_with_dict_var():
    """Test resuball with a dict variable for replacement mapping"""
    template = """
<input load="text">
interface GigabitEthernet0/0
interface FastEthernet0/1
</input>

<vars>
replace_map = {"Gi": "GigabitEthernet", "Fa": "FastEthernet"}
</vars>

<group>
interface {{ interface | resuball(replace_map) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Gi0/0"
    assert res[0][0][1]["interface"] == "Fa0/1"


def test_match_resuball_with_str_var():
    """Test resuball with a string variable"""
    template = """
<input load="text">
interface GigabitEthernet0/0
</input>

<vars>
old_pattern = "GigabitEthernet"
</vars>

<group>
interface {{ interface | resuball("Gi", old_pattern) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["interface"] == "Gi0/0"


# =====================================================================
# MATCH set_ function (uncovered branches)
# =====================================================================


def test_match_set_from_global_vars():
    """Test set function loading value from vars"""
    template = """
<input load="text">
interface Loopback0
  shutdown
</input>

<vars>
site = "NYC"
</vars>

<group>
interface {{ interface }}
  shutdown {{ location | set(site) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res[0][0][0]["location"] == "NYC"
