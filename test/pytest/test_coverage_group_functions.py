import sys

sys.path.insert(0, "../..")
import pprint
import json
import pytest

from ttp import ttp


# =====================================================================
# GROUP equal FUNCTION
# =====================================================================


def test_group_equal_match():
    """Test group equal function - key matches value, group is kept"""
    template = """
<input load="text">
interface Loopback0
  admin_status up
interface Vlan777
  admin_status down
</input>

<group equal="admin_status, up">
interface {{ interface }}
  admin_status {{ admin_status }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Loopback0", "admin_status": "up"}]
    ]]


def test_group_equal_no_match():
    """Test group equal function - key doesn't match, group dropped"""
    template = """
<input load="text">
interface Loopback0
  admin_status down
</input>

<group equal="admin_status, up">
interface {{ interface }}
  admin_status {{ admin_status }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # should be empty since no matches
    assert res == [[{}]]


# =====================================================================
# GROUP exclude FUNCTION
# =====================================================================


def test_group_exclude_key_present():
    """Test group exclude - drops group when specified key is present"""
    template = """
<input load="text">
interface Loopback0
  description RID
  mtu 1500
interface Vlan10
  description VLAN10
</input>

<group exclude="mtu">
interface {{ interface }}
  description {{ description }}
  mtu {{ mtu }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # Loopback0 has mtu so it should be excluded
    assert res == [[
        [{"interface": "Vlan10", "description": "VLAN10"}]
    ]]


def test_group_exclude_key_absent():
    """Test group exclude - keeps group when specified key is absent"""
    template = """
<input load="text">
interface Loopback0
  description RID
</input>

<group exclude="mtu">
interface {{ interface }}
  description {{ description }}
  mtu {{ mtu }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Loopback0", "description": "RID"}]
    ]]


# =====================================================================
# GROUP exclude_val FUNCTION
# =====================================================================


def test_group_exclude_val_match():
    """Test group exclude_val - drops group when key has specified value"""
    template = """
<input load="text">
interface Loopback0
  admin_status up
interface Vlan10
  admin_status down
</input>

<group exclude_val="admin_status, down">
interface {{ interface }}
  admin_status {{ admin_status }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Loopback0", "admin_status": "up"}]
    ]]


def test_group_exclude_val_no_match():
    """Test group exclude_val - keeps group when key has different value"""
    template = """
<input load="text">
interface Loopback0
  admin_status up
</input>

<group exclude_val="admin_status, down">
interface {{ interface }}
  admin_status {{ admin_status }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Loopback0", "admin_status": "up"}]
    ]]


def test_group_exclude_val_key_missing():
    """Test group exclude_val - keeps group when key is not present"""
    template = """
<input load="text">
interface Loopback0
  description RID
</input>

<group exclude_val="admin_status, down">
interface {{ interface }}
  description {{ description }}
  admin_status {{ admin_status }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[
        [{"interface": "Loopback0", "description": "RID"}]
    ]]


# =====================================================================
# GROUP excludeall FUNCTION
# =====================================================================


def test_group_excludeall_all_present():
    """Test group excludeall - drops group when ALL specified keys present"""
    template = """
<input load="text">
interface Loopback0
  description RID
  mtu 1500
interface Vlan10
  description VLAN10
</input>

<group excludeall="description, mtu">
interface {{ interface }}
  description {{ description }}
  mtu {{ mtu }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # Loopback0 has both description and mtu, so it should be excluded
    # Vlan10 has only description, so it should be kept
    assert res == [[
        [{"interface": "Vlan10", "description": "VLAN10"}]
    ]]


def test_group_excludeall_partial_present():
    """Test group excludeall - keeps group when not all keys present"""
    template = """
<input load="text">
interface Loopback0
  description RID
</input>

<group excludeall="description, mtu">
interface {{ interface }}
  description {{ description }}
  mtu {{ mtu }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # Only description found, not all keys, so group is kept
    assert res == [[
        [{"interface": "Loopback0", "description": "RID"}]
    ]]


# =====================================================================
# GROUP to_ip FUNCTION
# =====================================================================


def test_group_to_ip():
    """Test group to_ip function converts IP and mask to IP object"""
    template = """
<input load="text">
interface Loopback0
  ip address 192.168.1.1
  ip mask 255.255.255.0
</input>

<group to_ip="ip_addr, ip_mask">
interface {{ interface }}
  ip address {{ ip_addr }}
  ip mask {{ ip_mask }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    import ipaddress
    assert res == [[
        [{"interface": "Loopback0", "ip_addr": ipaddress.IPv4Interface("192.168.1.1/24"), "ip_mask": "255.255.255.0"}]
    ]]


# =====================================================================
# GROUP contains edge cases
# =====================================================================


def test_group_contains_default_value_same():
    """Test group contains - when key present but value equals default"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan10
  description VLAN10
  mtu 9000
</input>

<group contains="mtu">
interface {{ interface }}
  description {{ description }}
  mtu {{ mtu }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # Only Vlan10 has mtu matched
    assert res == [[
        [{"interface": "Vlan10", "description": "VLAN10", "mtu": "9000"}]
    ]]


# =====================================================================
# GROUP containsall edge cases
# =====================================================================


def test_group_containsall_all_present():
    """Test containsall - keeps group when all keys are present with values"""
    template = """
<input load="text">
interface Loopback0
  description RID
  mtu 1500
interface Vlan10
  description VLAN10
</input>

<group containsall="description, mtu">
interface {{ interface }}
  description {{ description }}
  mtu {{ mtu }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # Only Loopback0 has both description and mtu matched
    assert res == [[
        [{"interface": "Loopback0", "description": "RID", "mtu": "1500"}]
    ]]


def test_group_containsall_missing_key():
    """Test containsall - drops group when a key is missing"""
    template = """
<input load="text">
interface Loopback0
  description RID
</input>

<group containsall="description, mtu">
interface {{ interface }}
  description {{ description }}
  mtu {{ mtu }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[{}]]
