import sys
import os

sys.path.insert(0, "../..")
import pprint
import pytest
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    from ttp_templates import get_template

    HAS_TTP_TEMPLATES = True
except ImportError:
    HAS_TTP_TEMPLATES = False

skip_if_no_ttp_templates = pytest.mark.skipif(
    HAS_TTP_TEMPLATES == False,
    reason="Failed to import ttp_templates module, install it",
)

from ttp import ttp


def test_extend_tag_from_file():
    """
        template="./assets/extend_vlan.txt" content is:
    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>
    """
    template = """
<extend template="./assets/extend_vlan.txt"/>
    """
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [{"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}}]
    ]


# test_extend_tag_from_file()


def test_extend_tag_from_file_anonymous():
    """
        template="./assets/extend_vlan.txt" content is:
    vlan {{ vlan }}
     name {{ name }}
    """
    template = """
<extend template="./assets/extend_vlan_anon.txt"/>
    """
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [[{"name": "some_vlan", "vlan": "1234"}, {"name": "one_more", "vlan": "910"}]]
    ]


# test_extend_tag_from_file_anonymous()


def test_extend_tag_from_file_with_template_tag():
    """
        template="./assets/extend_vlan.txt" content is:
    <template>
    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>
    </template>
    """
    template = """
<extend template="./assets/extend_vlan_with_template_tag.txt"/>
    """
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [{"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}}]
    ]


# test_extend_tag_from_file_with_template_tag()


def test_extend_tag_from_file_wrong_path():
    """
        template="./assets/extend_vlan.txt" content is:
    <template>
    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>
    </template>
    """
    template = """
<extend template="./assets/does_not_exist.txt"/>
    """
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    with pytest.raises(FileNotFoundError):
        parser = ttp(data=data, template=template)


# test_extend_tag_from_file_wrong_path()


@skip_if_no_ttp_templates
def test_extend_tag_from_ttp_templates():
    """
    Test loading ttp_templates template
    """
    template = """
<extend template="ttp://platform/test_platform_show_run_pipe_sec_interface.txt"/>

<group name="vlans.{{ vlan }}">
vlan {{ vlan }}
 name {{ name }}
</group>
    """
    data = """
interface Gi1.100
 description Some description 1
 encapsulation dot1q 100
 ip address 10.0.0.1 255.255.255.0
 shutdown
!
interface Gi2
 description Some description 2
 ip address 10.1.0.1 255.255.255.0
!
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "description": "Some description 1",
                    "disabled": True,
                    "dot1q": "100",
                    "interface": "Gi1.100",
                    "ip": "10.0.0.1",
                    "mask": "255.255.255.0",
                },
                {
                    "description": "Some description 2",
                    "interface": "Gi2",
                    "ip": "10.1.0.1",
                    "mask": "255.255.255.0",
                },
                {"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}},
            ]
        ]
    ]


# test_extend_tag_from_ttp_templates()


def test_extend_tag_from_file_vars_and_lookup():
    """
        ./assets/extend_vars_and_lookup_tag.txt content:
    <lookup name="bgp_asn" load="yaml">
    '65100':
      as_description: Private ASN
      as_name: Subs
      prefix_num: '734'
    '65101':
      as_description: Cust-1 ASN
      as_name: Cust1
      prefix_num: '156'
    </lookup>

    <vars load="yaml">
    var_1: value_1
    var_2: value_2
    var_3: [1,2,3,4,"a"]
    </vars>
    """
    template = """
<extend template="./assets/extend_vars_and_lookup_tag.txt"/>

<input load="text">
router bgp 65100
</input>

<group name="bgp_config">
router bgp {{ bgp_as | lookup("bgp_asn", add_field="as_details") }}
{{ var_1_value | set(var_1) }}
{{ var_2_value | set(var_2) }}
{{ var_2_value | set(var_3) }}
</group> 
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "bgp_config": {
                    "as_details": {
                        "as_description": "Private ASN",
                        "as_name": "Subs",
                        "prefix_num": "734",
                    },
                    "bgp_as": "65100",
                    "var_1_value": "value_1",
                    "var_2_value": "var_3",
                }
            }
        ]
    ]


# test_extend_tag_from_file_vars_and_lookup()


def test_extend_tag_within_group():
    template = """
<input load="text">
router bgp 65100
 router-id 1.1.1.1
 neighbor 2.2.2.2 remote-as 65000
</input>

<group name="bgp_config">
router bgp {{ bgp_as }}

<extend template="./assets/test_extend_tag_within_group.txt"/>

<group name="peers">
 neighbor {{ peer }} remote-as {{ asn }}
</group>

</group> 
    """
    parser = ttp(template=template, log_level="warning")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "bgp_config": {
                    "bgp_as": "65100",
                    "config": {"rid": "1.1.1.1"},
                    "peers": {"asn": "65000", "peer": "2.2.2.2"},
                }
            }
        ]
    ]


# test_extend_tag_within_group()


def test_extend_tag_within_group_with_child_groups_above():
    template = """
<input load="text">
router bgp 65100
 router-id 1.1.1.1
 neighbor 2.2.2.2 remote-as 65000
</input>

<group name="bgp_config">
router bgp {{ bgp_as }}

<group name="peers">
 neighbor {{ peer }} remote-as {{ asn }}
</group>

<extend template="./assets/test_extend_tag_within_group.txt"/>

</group> 
    """
    parser = ttp(template=template, log_level="warning")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "bgp_config": {
                    "bgp_as": "65100",
                    "config": {"rid": "1.1.1.1"},
                    "peers": {"asn": "65000", "peer": "2.2.2.2"},
                }
            }
        ]
    ]


# test_extend_tag_within_group_with_child_groups_above()


def test_extend_tag_within_group_with_non_hierarch_template():
    template = """
<input load="text">
router bgp 65100
 router-id 1.1.1.1
 neighbor 2.2.2.2 remote-as 65000
</input>

<group name="bgp_config">
router bgp {{ bgp_as }}

<group name="config">
<extend template="./assets/test_extend_tag_within_group_with_non_hierarch_template.txt"/>
</group>

<group name="peers">
 neighbor {{ peer }} remote-as {{ asn }}
</group>

</group> 
    """
    parser = ttp(template=template, log_level="warning")
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [
        [
            {
                "bgp_config": {
                    "bgp_as": "65100",
                    "config": {"rid": "1.1.1.1"},
                    "peers": {"asn": "65000", "peer": "2.2.2.2"},
                }
            }
        ]
    ]


# test_extend_tag_within_group_with_non_hierarch_template()


def test_extend_tag_within_group_with_anonymous_group():
    template = """
<input load="text">
router bgp 65100
 router-id 1.1.1.1
 neighbor 2.2.2.2 remote-as 65000
</input>

<group name="bgp_config">
router bgp {{ bgp_as }}

<group name="config">
<extend template="./assets/test_extend_tag_within_group_with_anonymous_group.txt"/>
</group>

<group name="peers">
 neighbor {{ peer }} remote-as {{ asn }}
</group>

</group> 
    """
    parser = ttp(template=template, log_level="warning")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "bgp_config": {
                    "bgp_as": "65100",
                    "config": {"rid": "1.1.1.1"},
                    "peers": {"asn": "65000", "peer": "2.2.2.2"},
                }
            }
        ]
    ]


# test_extend_tag_within_group_with_anonymous_group()


def test_extend_tag_within_group_with_multiple_groups():
    """
        ./assets/test_extend_tag_within_group_with_multiple_groups.txt content:
    <group name="config">
     router-id {{ rid }}
    </group>

    <group name="vrf.{{ vrf }}">
     address-family ipv4 vrf {{ vrf }}
    </group>
    """
    template = """
<input load="text">
router bgp 65100
 router-id 1.1.1.1
 neighbor 2.2.2.2 remote-as 65000
 neighbor 2.2.2.3 remote-as 65001
 ! 
 address-family ipv4 vrf TEST_1
 address-family ipv4 vrf TEST_2
</input>

<group name="bgp_config">
router bgp {{ bgp_as }}

<extend template="./assets/test_extend_tag_within_group_with_multiple_groups.txt"/>

<group name="peers">
 neighbor {{ peer }} remote-as {{ asn }}
</group>

</group> 
    """
    parser = ttp(template=template, log_level="warning")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "bgp_config": {
                    "bgp_as": "65100",
                    "config": {"rid": "1.1.1.1"},
                    "peers": [
                        {"asn": "65000", "peer": "2.2.2.2"},
                        {"asn": "65001", "peer": "2.2.2.3"},
                    ],
                    "vrf": {"TEST_1": {}, "TEST_2": {}},
                }
            }
        ]
    ]


# test_extend_tag_within_group_with_multiple_groups()


def test_extend_tag_from_file_group_name_filter():
    """
        template="./assets/extend_vlan.txt" content is:
    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>
    """
    template = """
<extend template="./assets/extend_groups_filter_test.txt" groups="vlans.{{ vlan }}"/>
    """
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [{"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}}]
    ]


# test_extend_tag_from_file_group_filter()


def test_extend_tag_from_file_group_index_filter():
    """
        template="./assets/extend_vlan.txt" content is:
    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>
    """
    template = """
<extend template="./assets/extend_groups_filter_test.txt" groups="1"/>
    """
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [{"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}}]
    ]


# test_extend_tag_from_file_group_index_filter()


def test_extend_tag_from_file_vars_filter():
    template = """
<vars name="some">
a = 1
b = 2
</vars>

<extend template="./assets/extend_test_vars_filter.txt" vars="common_vars, other_vars"/>

<group name="vlans.{{ vlan }}">
vlan {{ vlan }}
 name {{ name }}
 {{ r_test | set(r) }}
</group>
    """
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "common_vars": {"c": 3, "d": 4},
                "other_vars": {"e": 5, "f": 6},
                "some": {"a": 1, "b": 2},
                "vlans": {
                    "1234": {"name": "some_vlan", "r_test": "r"},
                    "910": {"name": "one_more", "r_test": "r"},
                },
            }
        ]
    ]


# test_extend_tag_from_file_vars_filter()


def test_extend_tag_from_file_with_vars_inputs_filter():
    template = """
<extend template="./assets/extend_test_inputs_filter.txt" inputs="vlan_1, vlan_3"/>

<group name="vlans.{{ vlan }}">
vlan {{ vlan }}
 name {{ name }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "some": {"a": 1, "b": 2},
                "vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}},
            },
            {"some": {"a": 1, "b": 2}, "vlans": {"777": {"name": "vlan_name_777"}}},
        ]
    ]


# test_extend_tag_from_file_with_vars_inputs_filter()


def test_extend_tag_from_file_lookups_filter():
    template = """
<extend template="./assets/extend_test_lookups_filter.txt" lookups="bgp_asn"/>

<input load="text">
router bgp 65100
</input>

<group name="bgp_config">
router bgp {{ bgp_as | lookup("bgp_asn", add_field="as_details") }}
{{ var_1_value | set(var_1) }}
{{ var_2_value | set(var_2) }}
{{ var_3_value | set(var_3) }}
</group> 
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "bgp_config": {
                    "as_details": {
                        "as_description": "Private ASN",
                        "as_name": "Subs",
                        "prefix_num": "734",
                    },
                    "bgp_as": "65100",
                    "var_1_value": "value_1",
                    "var_2_value": [1, 2, 3, 4, "a"],
                    "var_3_value": "var_3",
                }
            }
        ]
    ]


# test_extend_tag_from_file_lookups_filter()


def test_extend_tag_from_file_output_filter():
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    template = """
<extend template="./assets/extend_test_output_filter.txt" outputs="to_csv"/>

<group>
vlan {{ vlan }}
 name {{ name }}
</group>
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # print(res[0])
    assert res == ['"name","vlan"\n"some_vlan","1234"\n"one_more","910"']


# test_extend_tag_from_file_output_filter()


def test_extend_tag_from_file_nested_group_filter():
    data = """
interface Gi1
 description bla bla bla
 ip address 1.1.1.1 255.255.255.0
!
interface Gi2
 name bla bla
 shutdown
 ip address 1.1.2.1 255.255.255.0
!
    """
    template = """
<group name="interfaces">
interface {{ interface }}
 description {{ description }}
 shutdown {{ disabled | set(True) }}
 <extend template="./assets/extend_test_nested_group_filter.txt" groups="ip_primary"/>
</group>
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "interfaces": [
                    {
                        "interface": "Gi1",
                        "ip_primary": {"ip": "1.1.1.1", "mask": "255.255.255.0"},
                    },
                    {
                        "disabled": True,
                        "interface": "Gi2",
                        "ip_primary": {"ip": "1.1.2.1", "mask": "255.255.255.0"},
                    },
                ]
            }
        ]
    ]


# test_extend_tag_from_file_nested_group_filter()


@skip_if_no_ttp_templates
def test_extend_tag_groups_recursive_extend_load():
    template = """
<extend template="./assets/extend_groups_recursive_extend_load.txt"/>

<group name="vlans.{{ vlan }}">
vlan {{ vlan }}
 name {{ name }}
</group>
    """
    data = """
logging host 1.1.1.1
logging host 1.1.1.2
!
interface Gi1.100
 description Some description 1
 encapsulation dot1q 100
 ip address 10.0.0.1 255.255.255.0
 shutdown
!
interface Gi2
 description Some description 2
 ip address 10.1.0.1 255.255.255.0
!
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "config": {
                    "interfaces_config": [
                        {
                            "description": "Some description 1",
                            "disabled": True,
                            "dot1q": "100",
                            "interface": "Gi1.100",
                            "ip": "10.0.0.1",
                            "mask": "255.255.255.0",
                        },
                        {
                            "description": "Some description 2",
                            "interface": "Gi2",
                            "ip": "10.1.0.1",
                            "mask": "255.255.255.0",
                        },
                    ],
                    "logging": [{"syslog": "1.1.1.1"}, {"syslog": "1.1.1.2"}],
                },
                "vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}},
            }
        ]
    ]


# test_extend_tag_groups_recursive_extend_load()


@skip_if_no_ttp_templates
def test_extend_tag_groups_recursive_extend_load_several_top_groups():
    template = """
<extend template="./assets/extend_groups_recursive_extend_load_several_top_groups.txt"/>

<group name="vlans.{{ vlan }}">
vlan {{ vlan }}
 name {{ name }}
</group>
    """
    data = """
logging host 1.1.1.1
logging host 1.1.1.2
!
interface Gi1.100
 description Some description 1
 encapsulation dot1q 100
 ip address 10.0.0.1 255.255.255.0
 shutdown
!
interface Gi2
 description Some description 2
 ip address 10.1.0.1 255.255.255.0
!
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            {
                "interfaces_config": [
                    {
                        "description": "Some description 1",
                        "disabled": True,
                        "dot1q": "100",
                        "interface": "Gi1.100",
                        "ip": "10.0.0.1",
                        "mask": "255.255.255.0",
                    },
                    {
                        "description": "Some description 2",
                        "interface": "Gi2",
                        "ip": "10.1.0.1",
                        "mask": "255.255.255.0",
                    },
                ],
                "logging": [{"syslog": "1.1.1.1"}, {"syslog": "1.1.1.2"}],
                "vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}},
            }
        ]
    ]


# test_extend_tag_groups_recursive_extend_load_several_top_groups()


def test_extend_tag_from_file_with_macro():
    template = """
<macro>
def indent(data):
    # macro to indent each line of original template with 4 space characters
    return "\\n".join(f"    {line}" for line in data.splitlines())
</macro>

<extend template="./assets/extend_vlan.txt" macro="indent"/>
    """
    data = """
    vlan 1234
     name some_vlan
    !
    vlan 910
     name one_more
    !
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [
        [{"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}}]
    ]
	
# test_extend_tag_from_file_with_macro()


def test_ttp_templates_dir_env_variable_with_extend():
    os.environ["TTP_TEMPLATES_DIR"] = os.path.join(
        os.getcwd(), "assets", "TTP_TEMPLATES_DIR_TEST"
    )
    data = """
vlan 1234
 name some_vlan
!
vlan 910
 name one_more
!
    """
    template = """
<extend template="test_ttp_templates_dir_env_variable.txt"/>
    """
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [[{'vlans': {'1234': {'name': 'some_vlan'}, '910': {'name': 'one_more'}}}]]
    
# test_ttp_templates_dir_env_variable_with_extend()