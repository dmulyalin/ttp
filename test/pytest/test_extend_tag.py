import sys

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
