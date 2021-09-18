import sys

sys.path.insert(0, "../..")
import pprint

from ttp import ttp


def test_contains_re_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | contains_re("Port-Channel") }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [
        [[{"interface": "Port-Channel11", "is_lag": True, "is_loopback": False}]]
    ]


# test_contains_re_inline()


def test_contains_re_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management_2
interface Vlan777
  description Management
</input>

<vars>
var_1 = "Port-.+"
</vars>

<group>
interface {{ interface | contains_re(var_1) }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {
                    "description": "Storage",
                    "interface": "Port-Channel11",
                    "is_lag": True,
                    "is_loopback": False,
                },
                {
                    "description": "Management_2",
                    "interface": "Port-Channel12",
                    "is_lag": True,
                    "is_loopback": False,
                },
            ]
        ]
    ]


# test_contains_re_from_vars()


def test_startswith_re_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | startswith_re(r"Por\\S") }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [[{"interface": "Port-Channel11", "is_lag": True, "is_loopback": False}]]
    ]


# test_startswith_re_inline()


def test_startswith_re_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management_2
interface Vlan777
  description Management
</input>

<vars>
var_1 = "Port-.+"
</vars>

<group>
interface {{ interface | startswith_re(var_1) }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {
                    "description": "Storage",
                    "interface": "Port-Channel11",
                    "is_lag": True,
                    "is_loopback": False,
                },
                {
                    "description": "Management_2",
                    "interface": "Port-Channel12",
                    "is_lag": True,
                    "is_loopback": False,
                },
            ]
        ]
    ]


# test_startswith_re_from_vars()


def test_endswith_re_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | endswith_re(r"Channel\\d+") }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [[{"interface": "Port-Channel11", "is_lag": True, "is_loopback": False}]]
    ]


def test_endswith_re_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<vars>
var_1 = r"Channel\\d+"
</vars>

<group>
interface {{ interface | endswith_re(var_1) }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [[{"interface": "Port-Channel11", "is_lag": True, "is_loopback": False}]]
    ]


def test_notstartswith_re_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | notstartswith_re(r"Loop\\S+") }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11", "is_lag": True, "is_loopback": False},
                {
                    "description": "Management",
                    "interface": "Vlan777",
                    "is_lag": True,
                    "is_loopback": False,
                },
            ]
        ]
    ]


# test_notstartswith_re_inline()


def test_notstartswith_re_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<vars>
var_1 = r"Loop\\S+"
</vars>

<group>
interface {{ interface | notstartswith_re(var_1) }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11", "is_lag": True, "is_loopback": False},
                {
                    "description": "Management",
                    "interface": "Vlan777",
                    "is_lag": True,
                    "is_loopback": False,
                },
            ]
        ]
    ]


def test_notendswith_re_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | notendswith_re(r"back\\d+") }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11", "is_lag": True, "is_loopback": False},
                {
                    "description": "Management",
                    "interface": "Vlan777",
                    "is_lag": True,
                    "is_loopback": False,
                },
            ]
        ]
    ]


def test_notendswith_re_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<vars>
var_1 = r"back\\d+|lan\\d+"
</vars>

<group>
interface {{ interface | notendswith_re(var_1) }}
  description {{ description }}
  {{ is_lag | set(True) }}
  {{ is_loopback| set(False) }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [[{"interface": "Port-Channel11", "is_lag": True, "is_loopback": False}]]
    ]


# test_notendswith_re_from_vars()


def test_exclude_re_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | exclude_re(r"back.+") }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11"},
                {"description": "Management", "interface": "Vlan777"},
            ]
        ]
    ]


# test_exclude_re_inline()


def test_exclude_re_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage 
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<vars>
var_1 = r"back\\d+|lan\\d+"
</vars>

<group>
interface {{ interface | exclude_re(var_1) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{"description": "Storage", "interface": "Port-Channel11"}]]]


# test_exclude_re_from_vars()


def test_exclude_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | exclude(Loop) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11"},
                {"description": "Management", "interface": "Vlan777"},
            ]
        ]
    ]


def test_exclude_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
</input>

<vars>
var_1 = "Loop"
</vars>

<group>
interface {{ interface | exclude(var_1) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"interface": "Port-Channel11"},
                {"description": "Management", "interface": "Vlan777"},
            ]
        ]
    ]


def test_contains_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | contains(Port) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description": "Storage", "interface": "Port-Channel11"},
                {"description": "Management", "interface": "Port-Channel12"},
            ]
        ]
    ]


# test_contains_inline()


def test_contains_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<vars>
var_1 = "Port"
</vars>

<group>
interface {{ interface | contains(var_1) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description": "Storage", "interface": "Port-Channel11"},
                {"description": "Management", "interface": "Port-Channel12"},
            ]
        ]
    ]


def test_contains_multi():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<vars>
var_1 = "Port"
</vars>

<group>
interface {{ interface | contains(var_1, Vlan) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description": "Storage", "interface": "Port-Channel11"},
                {"description": "Management", "interface": "Port-Channel12"},
                {"description": "Management", "interface": "Vlan777"},
            ]
        ]
    ]


# test_contains_multi()


def test_equal_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | equal("Port-Channel12") }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    pprint.pprint(res, width=150)
    assert res == [[[{"description": "Management", "interface": "Port-Channel12"}]]]


# test_equal_inline()


def test_equal_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<vars>
var_1 = "Port-Channel12"
</vars>

<group>
interface {{ interface | equal(var_1) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{"description": "Management", "interface": "Port-Channel12"}]]]


def test_notequal_inline():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<group>
interface {{ interface | notequal("Port-Channel12") }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description": "Storage", "interface": "Port-Channel11"},
                {"description": "RID", "interface": "Loopback0"},
                {"description": "Management", "interface": "Vlan777"},
            ]
        ]
    ]


# test_notequal_inline()


def test_notequal_from_vars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<vars>
var_1 = "Port-Channel12"
</vars>

<group>
interface {{ interface | notequal(var_1) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [
        [
            [
                {"description": "Storage", "interface": "Port-Channel11"},
                {"description": "RID", "interface": "Loopback0"},
                {"description": "Management", "interface": "Vlan777"},
            ]
        ]
    ]


# test_notequal_inline()
