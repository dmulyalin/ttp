import sys

sys.path.insert(0, "../..")
import pprint
import pytest

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
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{}]]


# test_extend_tag_from_file_wrong_path()


@skip_if_no_ttp_templates
def test_extend_tag_from_ttp_template():
    """
    Test loadng ttp_template template
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


# test_extend_tag_from_ttp_template()


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
    res == [
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
