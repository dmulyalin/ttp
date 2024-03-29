import sys

sys.path.insert(0, "../..")
import pprint
import logging

logging.basicConfig(level=logging.DEBUG)

from ttp import ttp


def test_headers_indicator_left_aligned():
    template = """
<input load="text">
Port      Name               Status       Vlan       Duplex  Speed Type
Gi0/1     PIT-VDU213         connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/2     PIT-VDU211         connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/3     PIT-VDU212         notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/4                        connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/5                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/6                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/7                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/8                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/9                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/10                       notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/11                       notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/12                       notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/13                       disabled     1            auto   auto 10/100/1000BaseTX
Gi0/14                       disabled     1            auto   auto 10/100/1000BaseTX
Gi0/15                       connected    trunk        full   1000 1000BaseLX SFP
Gi0/16    pitrs2201 te1/1/4  connected    trunk        full   1000  1000BaseLX SFP
</input>

<group>
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ }}
</group>   
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "Duplex": "a-full",
                    "Name": "PIT-VDU213",
                    "Port": "Gi0/1",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "a-full",
                    "Name": "PIT-VDU211",
                    "Port": "Gi0/2",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "PIT-VDU212",
                    "Port": "Gi0/3",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "a-full",
                    "Name": "",
                    "Port": "Gi0/4",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/5",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/6",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/7",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/8",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/9",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/10",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/11",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/12",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/13",
                    "Speed": "auto",
                    "Status": "disabled",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "1",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/14",
                    "Speed": "auto",
                    "Status": "disabled",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "1",
                },
                {
                    "Duplex": "full",
                    "Name": "",
                    "Port": "Gi0/15",
                    "Speed": "1000",
                    "Status": "connected",
                    "Type": "1000BaseLX SFP",
                    "Vlan": "trunk",
                },
                {
                    "Duplex": "full",
                    "Name": "pitrs2201 te1/1/4",
                    "Port": "Gi0/16",
                    "Speed": "1000",
                    "Status": "connected",
                    "Type": "1000BaseLX SFP",
                    "Vlan": "trunk",
                },
            ]
        ]
    ]


# test_headers_indicator()


def test_headers_indicator_space_indented_header():
    template = """
<input load="text">
   Network            Next Hop            Metric     LocPrf     Weight Path
*>e11.11.1.111/32     12.123.12.1              0                     0 65000 ?
*>e222.222.222.2/32   12.123.12.1              0                     0 65000 ?
*>e333.33.333.333/32  12.123.12.1              0                     0 65000 ?
</input>

<group>
   Network            Next_Hop            Metric     LocPrf     Weight Path  {{ _headers_ }}
</group>   
"""
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "LocPrf": "",
                    "Metric": "0",
                    "Network": "*>e11.11.1.111/32",
                    "Next_Hop": "12.123.12.1",
                    "Path": "65000 ?",
                    "Weight": "0",
                },
                {
                    "LocPrf": "",
                    "Metric": "0",
                    "Network": "*>e222.222.222.2/32",
                    "Next_Hop": "12.123.12.1",
                    "Path": "65000 ?",
                    "Weight": "0",
                },
                {
                    "LocPrf": "",
                    "Metric": "0",
                    "Network": "*>e333.33.333.333/32",
                    "Next_Hop": "12.123.12.1",
                    "Path": "65000 ?",
                    "Weight": "0",
                },
            ]
        ]
    ]


# test_headers_indicator_2()


def test_headers_indicator_multiline_header():
    template = """
<input load="text">
--------------------------------------------------------------------------------
Port      Name               Status       Vlan       Duplex  Speed Type
--------------------------------------------------------------------------------
Gi0/1     PIT-VDU213         connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/2     PIT-VDU211         connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/3     PIT-VDU212         notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/4                        connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/5                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/6                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/7                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/8                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/9                        notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/10                       notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/11                       notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/12                       notconnect   18           auto   auto 10/100/1000BaseTX
Gi0/13                       disabled     1            auto   auto 10/100/1000BaseTX
Gi0/14                       disabled     1            auto   auto 10/100/1000BaseTX
Gi0/15                       connected    trunk        full   1000 1000BaseLX SFP
Gi0/16    pitrs2201 te1/1/4  connected    trunk        full   1000  1000BaseLX SFP
</input>

<group macro='clean_up'>
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ }}
</group>   

<macro>
def clean_up(data):
    if "----" in data["Port"]:
        return False
    return True
</macro>
"""
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    # res = parser.result(format="tabulate")[0]
    # print(res)
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "Duplex": "a-full",
                    "Name": "PIT-VDU213",
                    "Port": "Gi0/1",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "a-full",
                    "Name": "PIT-VDU211",
                    "Port": "Gi0/2",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "PIT-VDU212",
                    "Port": "Gi0/3",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "a-full",
                    "Name": "",
                    "Port": "Gi0/4",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/5",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/6",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/7",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/8",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/9",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/10",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/11",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/12",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/13",
                    "Speed": "auto",
                    "Status": "disabled",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "1",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/14",
                    "Speed": "auto",
                    "Status": "disabled",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "1",
                },
                {
                    "Duplex": "full",
                    "Name": "",
                    "Port": "Gi0/15",
                    "Speed": "1000",
                    "Status": "connected",
                    "Type": "1000BaseLX SFP",
                    "Vlan": "trunk",
                },
                {
                    "Duplex": "full",
                    "Name": "pitrs2201 te1/1/4",
                    "Port": "Gi0/16",
                    "Speed": "1000",
                    "Status": "connected",
                    "Type": "1000BaseLX SFP",
                    "Vlan": "trunk",
                },
            ]
        ]
    ]


# test_headers_indicator_3()


def test_headers_indicator_columns_merged():
    template = """
<input load="text">
Port   Name             Status    Vlan       Duplex  Speed Type
Gi0/1  PIT-VDU213       connected 18         a-full  a-100 10/100/1000BaseTX
Gi0/3  PIT-VDU212       notconnect18           auto   auto 10/100/1000BaseTX
Gi0/5                   notconnect18           auto   auto 10/100/1000BaseTX
Gi0/15                  connected trunk        full   1000 1000BaseLX SFP
Gi0/16 pitrs2201 te1/1/4connected trunk        full   1000  1000BaseLX SFP
</input>

<group>
Port   Name             Status    Vlan       Duplex  Speed Type   {{ _headers_ }}
</group>   
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # print(parser.result(format="tabulate")[0])
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "Duplex": "a-full",
                    "Name": "PIT-VDU213",
                    "Port": "Gi0/1",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "PIT-VDU212",
                    "Port": "Gi0/3",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "auto",
                    "Name": "",
                    "Port": "Gi0/5",
                    "Speed": "auto",
                    "Status": "notconnect",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "full",
                    "Name": "",
                    "Port": "Gi0/15",
                    "Speed": "1000",
                    "Status": "connected",
                    "Type": "1000BaseLX SFP",
                    "Vlan": "trunk",
                },
                {
                    "Duplex": "full",
                    "Name": "pitrs2201 te1/1/4",
                    "Port": "Gi0/16",
                    "Speed": "1000",
                    "Status": "connected",
                    "Type": "1000BaseLX SFP",
                    "Vlan": "trunk",
                },
            ]
        ]
    ]


# test_headers_indicator_columns_merged()


def test_headers_indicator_tab_indented_header():
    template = """
<input load="text">
    Network               Next Hop            Metric     LocPrf     Weight Path
*>ef11.11.1.111/32     12.123.12.1              0                     0 65000 ?
*>ef222.222.222.2/32   12.123.12.1              0                     0 65000 ?
*>ef333.333.333.333/32 12.123.12.1              0                     0 65000 ?
</input>

<group>
    Network            Next_Hop            Metric     LocPrf     Weight Path  {{ _headers_ }}
</group>   
"""
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "LocPrf": "",
                    "Metric": "0",
                    "Network": "*>ef11.11.1.111/32",
                    "Next_Hop": "12.123.12.1",
                    "Path": "65000 ?",
                    "Weight": "0",
                },
                {
                    "LocPrf": "",
                    "Metric": "0",
                    "Network": "*>ef222.222.222.2/32",
                    "Next_Hop": "12.123.12.1",
                    "Path": "65000 ?",
                    "Weight": "0",
                },
                {
                    "LocPrf": "",
                    "Metric": "0",
                    "Network": "*>ef333.333.333.333/32",
                    "Next_Hop": "12.123.12.1",
                    "Path": "65000 ?",
                    "Weight": "0",
                },
            ]
        ]
    ]


# test_headers_indicator_tab_indented_header()


def test_headers_docs_example():
    template = """
<input load="text">
Port      Name               Status       Vlan       Duplex  Speed Type
Gi0/1     PIT-VDU213         connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/4                        connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/16    pitrs2201 te1/1/4  connected    trunk        full   1000  1000BaseLX SFP
</input>

<group>
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ }}
</group>   
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "Duplex": "a-full",
                    "Name": "PIT-VDU213",
                    "Port": "Gi0/1",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "a-full",
                    "Name": "",
                    "Port": "Gi0/4",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "full",
                    "Name": "pitrs2201 te1/1/4",
                    "Port": "Gi0/16",
                    "Speed": "1000",
                    "Status": "connected",
                    "Type": "1000BaseLX SFP",
                    "Vlan": "trunk",
                },
            ]
        ]
    ]


# test_headers_docs_example()


def test_headers_shorter_lines():
    data = """
Filesystem              1K-blocks    Used Available Use% Mounted on
tmpfs                     1457328       0   1457328   0% /sys/fs/cgroup
/dev/mapper/centos-root  14034944 5783384   8251560  42% /
/dev/sda1                 1038336  220604    817732  22% /boot
    """
    template = """
Filesystem              K1_blocks Used    Available Use_ Mounted_on {{ _headers_ }}
"""
    parser = ttp(template=template, log_level="ERROR")
    parser.add_input(data)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "Available": "1457328",
                    "Filesystem": "tmpfs",
                    "K1_blocks": "1457328",
                    "Mounted_on": "/sys/fs/cgroup",
                    "Use_": "0%",
                    "Used": "0",
                },
                {
                    "Available": "8251560",
                    "Filesystem": "/dev/mapper/centos-root",
                    "K1_blocks": "14034944",
                    "Mounted_on": "/",
                    "Use_": "42%",
                    "Used": "5783384",
                },
                {
                    "Available": "817732",
                    "Filesystem": "/dev/sda1",
                    "K1_blocks": "1038336",
                    "Mounted_on": "/boot",
                    "Use_": "22%",
                    "Used": "220604",
                },
            ]
        ]
    ]


# test_headers_shorter_lines()


def test_headers_last_column_empty():
    data = """
Filesystem              1K-blocks    Used Available Use% Mounted on
tmpfs                     1457328       0   1457328   0% /sys/fs/cgroup
/dev/mapper/centos-root  14034944 5783384   8251560  2%
/dev/sda1                 1038336  220604    817732  22% /boot
    """
    template = """
Filesystem              K1_blocks Used    Available Use_ Mounted_on {{ _headers_ }}
"""
    parser = ttp(template=template, log_level="ERROR")
    parser.add_input(data)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "Available": "1457328",
                    "Filesystem": "tmpfs",
                    "K1_blocks": "1457328",
                    "Mounted_on": "/sys/fs/cgroup",
                    "Use_": "0%",
                    "Used": "0",
                },
                {
                    "Available": "8251560",
                    "Filesystem": "/dev/mapper/centos-root",
                    "K1_blocks": "14034944",
                    "Mounted_on": "",
                    "Use_": "2%",
                    "Used": "5783384",
                },
                {
                    "Available": "817732",
                    "Filesystem": "/dev/sda1",
                    "K1_blocks": "1038336",
                    "Mounted_on": "/boot",
                    "Use_": "22%",
                    "Used": "220604",
                },
            ]
        ]
    ]


# test_headers_last_column_empty()


def test_with_garbage():
    template = """
<input load="text">
interface Lo0
 ip address 124.171.238.50/29
!
interface Lo1
 ip address 1.1.1.1/30
!
Port      Name               Status       Vlan       Duplex  Speed Type
Gi0/1     PIT-VDU213         connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/4                        connected    18         a-full  a-100 10/100/1000BaseTX
Gi0/16    pitrs2201 te1/1/4  connected    trunk        full   1000  1000BaseLX SFP
</input>

<group>
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ }}
</group>   
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [
        [
            [
                {
                    "Duplex": "a-full",
                    "Name": "PIT-VDU213",
                    "Port": "Gi0/1",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "a-full",
                    "Name": "",
                    "Port": "Gi0/4",
                    "Speed": "a-100",
                    "Status": "connected",
                    "Type": "10/100/1000BaseTX",
                    "Vlan": "18",
                },
                {
                    "Duplex": "full",
                    "Name": "pitrs2201 te1/1/4",
                    "Port": "Gi0/16",
                    "Speed": "1000",
                    "Status": "connected",
                    "Type": "1000BaseLX SFP",
                    "Vlan": "trunk",
                },
            ]
        ]
    ]


# test_with_garbage()


def test_headers_with_column():
    template = """
<input load="text">
Port      Name               Status       Vlan       Duplex  Speed Type
Gi0/1
Gi0/2     PIT-VDU212
Gi0/3     PIT-VDU212         notconnect
Gi0/4     PIT-VDU212         notconnect   18
Gi0/5     PIT-VDU212         notconnect   18         auto
Gi0/6     PIT-VDU212         notconnect   18         auto    auto
Gi0/7     PIT-VDU212         notconnect   18         auto    auto  10/100/1000BaseTX
</input>

<group name="columns_10">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(10) }}
</group>  

<group name="columns_7">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(7) }}
</group>   

<group name="columns_6">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(6) }}
</group>   

<group name="columns_5">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(5) }}
</group>   

<group name="columns_4">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(4) }}
</group>   

<group name="columns_3">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(3) }}
</group> 

<group name="columns_2">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(2) }}
</group> 

<group name="columns_1">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(1) }}
</group> 

<group name="columns_0">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(0) }}
</group> 

<group name="columns__1">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ | columns(-1) }}
</group> 

<group name="no_columns">
Port      Name               Status       Vlan       Duplex  Speed Type   {{ _headers_ }}
</group> 
"""
    parser = ttp(template=template, log_level="DEBUG")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=170)
    # fmt: off
    assert res == [[{'columns_0': [{'Duplex': '', 'Name': '', 'Port': 'Gi0/1', 'Speed': '', 'Status': '', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/2', 'Speed': '', 'Status': '', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/3', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/4', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
   'columns_1': [{'Duplex': '', 'Name': '', 'Port': 'Gi0/1', 'Speed': '', 'Status': '', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/2', 'Speed': '', 'Status': '', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/3', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/4', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
   'columns_10': {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'},
   'columns_2': [{'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/2', 'Speed': '', 'Status': '', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/3', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/4', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
   'columns_3': [{'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/3', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': ''},
                 {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/4', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
   'columns_4': [{'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/4', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
   'columns_5': [{'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
   'columns_6': [{'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                 {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
   'columns_7': {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'},
   'columns__1': [{'Duplex': '', 'Name': '', 'Port': 'Gi0/1', 'Speed': '', 'Status': '', 'Type': '', 'Vlan': ''},
                  {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/2', 'Speed': '', 'Status': '', 'Type': '', 'Vlan': ''},
                  {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/3', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': ''},
                  {'Duplex': '', 'Name': 'PIT-VDU212', 'Port': 'Gi0/4', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                  {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                  {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                  {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}],
   'no_columns': [{'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/5', 'Speed': '', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                  {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/6', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '', 'Vlan': '18'},
                  {'Duplex': 'auto', 'Name': 'PIT-VDU212', 'Port': 'Gi0/7', 'Speed': 'auto', 'Status': 'notconnect', 'Type': '10/100/1000BaseTX', 'Vlan': '18'}]}]]
    # fmt: on


# test_headers_with_column()

def test_headers_on_tabular_output():
    data = """

Partition Name   L3V  Index  Max. Aflex  Admin Count
----------------------------------------------------
sivr_icm         No   1      32          0
ent_mgmt         No   2      32          0
Cloud            No   3  *   32          0
lync             No   4      32          0
sap              No   5      32          0
config_mgmts     No   6      32          0
Uprising         No   7      32          0
ERC_MGMT         No   8      32          0
sc_sw_ctrl       No   9      32          0
cust_hub         No   10     32          0
A10-CIS          No   11     32          0
SAP_Dev_Admin    No   12 *   32          0
sentry_ext       No   13     32          0
web_ecom_srvs    No   14     32          0
dir_sec_svc      No   15     32          0
eng_ops          No   16     32          0
mw_mgmt          No   17     32          0
oracle_db_adm    No   18     32          0
idm_mgmt         No   19     32          0
info_mgmt        No   20 *   32          0
sa_ops_natapps   No   21     32          0
eng_supt         No   37 *   32          0
retail_apps      No   128    32          0    
    """
    template = """
Partition_Name   L3V  Index  Max__Aflex  Admin_Count {{ _headers_ }}
    """
    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res, width=170)
    assert res == [[[{'Admin_Count': '-----------', 'Index': '-------', 'L3V': '-----', 'Max__Aflex': '------------', 'Partition_Name': '-----------------'},
                     {'Admin_Count': '0', 'Index': '1', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'sivr_icm'},
                     {'Admin_Count': '0', 'Index': '2', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'ent_mgmt'},
                     {'Admin_Count': '0', 'Index': '3  *', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'Cloud'},
                     {'Admin_Count': '0', 'Index': '4', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'lync'},
                     {'Admin_Count': '0', 'Index': '5', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'sap'},
                     {'Admin_Count': '0', 'Index': '6', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'config_mgmts'},
                     {'Admin_Count': '0', 'Index': '7', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'Uprising'},
                     {'Admin_Count': '0', 'Index': '8', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'ERC_MGMT'},
                     {'Admin_Count': '0', 'Index': '9', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'sc_sw_ctrl'},
                     {'Admin_Count': '0', 'Index': '10', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'cust_hub'},
                     {'Admin_Count': '0', 'Index': '11', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'A10-CIS'},
                     {'Admin_Count': '0', 'Index': '12 *', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'SAP_Dev_Admin'},
                     {'Admin_Count': '0', 'Index': '13', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'sentry_ext'},
                     {'Admin_Count': '0', 'Index': '14', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'web_ecom_srvs'},
                     {'Admin_Count': '0', 'Index': '15', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'dir_sec_svc'},
                     {'Admin_Count': '0', 'Index': '16', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'eng_ops'},
                     {'Admin_Count': '0', 'Index': '17', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'mw_mgmt'},
                     {'Admin_Count': '0', 'Index': '18', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'oracle_db_adm'},
                     {'Admin_Count': '0', 'Index': '19', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'idm_mgmt'},
                     {'Admin_Count': '0', 'Index': '20 *', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'info_mgmt'},
                     {'Admin_Count': '0', 'Index': '21', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'sa_ops_natapps'},
                     {'Admin_Count': '0', 'Index': '37 *', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'eng_supt'},
                     {'Admin_Count': '0', 'Index': '128', 'L3V': 'No', 'Max__Aflex': '32', 'Partition_Name': 'retail_apps'}]]]
    
# test_headers_on_tabular_output()