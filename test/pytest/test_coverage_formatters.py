import sys

sys.path.insert(0, "../..")
import pprint
import json
import pytest

from ttp import ttp


def test_pprint_formatter():
    """Test pprint output formatter"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface }}
  description {{ description }}
</group>

<output format="pprint"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)
    assert len(res) > 0
    # pprint formatter returns a string
    assert isinstance(res[0], str)
    assert "Loopback0" in res[0]
    assert "Vlan777" in res[0]


def test_yaml_formatter():
    """Test yaml output formatter"""
    template = """
<input load="text">
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface }}
  description {{ description }}
</group>

<output format="yaml"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)
    assert len(res) > 0
    # yaml formatter returns a string
    assert isinstance(res[0], str)
    assert "Loopback0" in res[0]
    assert "Vlan777" in res[0]


def test_pprint_formatter_with_returner_self():
    """Test pprint formatter with self returner to verify format"""
    template = """
<input load="text">
hostname Router1
</input>

<group>
hostname {{ hostname }}
</group>

<output format="pprint" returner="self"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)
    assert "Router1" in res[0]


def test_yaml_formatter_with_complex_data():
    """Test yaml formatter with nested group data"""
    template = """
<input load="text">
router bgp 65000
  neighbor 10.0.0.1
    remote-as 65001
  neighbor 10.0.0.2
    remote-as 65002
</input>

<group name="bgp">
router bgp {{ asn }}
  <group name="neighbors*">
  neighbor {{ peer }}
    remote-as {{ remote_as }}
  </group>
</group>

<output format="yaml"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert isinstance(res, list)
    assert isinstance(res[0], str)
    assert "65000" in res[0]
    assert "10.0.0.1" in res[0]
