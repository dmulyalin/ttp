import sys
sys.path.insert(0,'../..')
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
    assert res == [[[{'Duplex': 'a-full',
    'Name': 'PIT-VDU213',
    'Port': 'Gi0/1',
    'Speed': 'a-100',
    'Status': 'connected',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'a-full',
    'Name': 'PIT-VDU211',
    'Port': 'Gi0/2',
    'Speed': 'a-100',
    'Status': 'connected',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': 'PIT-VDU212',
    'Port': 'Gi0/3',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'a-full',
    'Name': '',
    'Port': 'Gi0/4',
    'Speed': 'a-100',
    'Status': 'connected',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/5',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/6',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/7',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/8',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/9',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/10',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/11',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/12',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/13',
    'Speed': 'auto',
    'Status': 'disabled',
    'Type': '10/100/1000BaseTX',
    'Vlan': '1'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/14',
    'Speed': 'auto',
    'Status': 'disabled',
    'Type': '10/100/1000BaseTX',
    'Vlan': '1'},
   {'Duplex': 'full',
    'Name': '',
    'Port': 'Gi0/15',
    'Speed': '1000',
    'Status': 'connected',
    'Type': '1000BaseLX SFP',
    'Vlan': 'trunk'},
   {'Duplex': 'full',
    'Name': 'pitrs2201 te1/1/4',
    'Port': 'Gi0/16',
    'Speed': '1000',
    'Status': 'connected',
    'Type': '1000BaseLX SFP',
    'Vlan': 'trunk'}]]]
    
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
    assert res == [[[{'LocPrf': '',
    'Metric': '0',
    'Network': '*>e11.11.1.111/32',
    'Next_Hop': '12.123.12.1',
    'Path': '65000 ?',
    'Weight': '0'},
   {'LocPrf': '',
    'Metric': '0',
    'Network': '*>e222.222.222.2/32',
    'Next_Hop': '12.123.12.1',
    'Path': '65000 ?',
    'Weight': '0'},
   {'LocPrf': '',
    'Metric': '0',
    'Network': '*>e333.33.333.333/32',
    'Next_Hop': '12.123.12.1',
    'Path': '65000 ?',
    'Weight': '0'}]]]
    
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
    assert res == [[[{'Duplex': 'a-full',
    'Name': 'PIT-VDU213',
    'Port': 'Gi0/1',
    'Speed': 'a-100',
    'Status': 'connected',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'a-full',
    'Name': 'PIT-VDU211',
    'Port': 'Gi0/2',
    'Speed': 'a-100',
    'Status': 'connected',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': 'PIT-VDU212',
    'Port': 'Gi0/3',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'a-full',
    'Name': '',
    'Port': 'Gi0/4',
    'Speed': 'a-100',
    'Status': 'connected',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/5',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/6',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/7',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/8',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/9',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/10',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/11',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/12',
    'Speed': 'auto',
    'Status': 'notconnect',
    'Type': '10/100/1000BaseTX',
    'Vlan': '18'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/13',
    'Speed': 'auto',
    'Status': 'disabled',
    'Type': '10/100/1000BaseTX',
    'Vlan': '1'},
   {'Duplex': 'auto',
    'Name': '',
    'Port': 'Gi0/14',
    'Speed': 'auto',
    'Status': 'disabled',
    'Type': '10/100/1000BaseTX',
    'Vlan': '1'},
   {'Duplex': 'full',
    'Name': '',
    'Port': 'Gi0/15',
    'Speed': '1000',
    'Status': 'connected',
    'Type': '1000BaseLX SFP',
    'Vlan': 'trunk'},
   {'Duplex': 'full',
    'Name': 'pitrs2201 te1/1/4',
    'Port': 'Gi0/16',
    'Speed': '1000',
    'Status': 'connected',
    'Type': '1000BaseLX SFP',
    'Vlan': 'trunk'}]]]
    
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
    assert res == [[[{'Duplex': 'a-full',
                      'Name': 'PIT-VDU213',
                      'Port': 'Gi0/1',
                      'Speed': 'a-100',
                      'Status': 'connected',
                      'Type': '10/100/1000BaseTX',
                      'Vlan': '18'},
                     {'Duplex': 'auto',
                      'Name': 'PIT-VDU212',
                      'Port': 'Gi0/3',
                      'Speed': 'auto',
                      'Status': 'notconnect',
                      'Type': '10/100/1000BaseTX',
                      'Vlan': '18'},
                     {'Duplex': 'auto',
                      'Name': '',
                      'Port': 'Gi0/5',
                      'Speed': 'auto',
                      'Status': 'notconnect',
                      'Type': '10/100/1000BaseTX',
                      'Vlan': '18'},
                     {'Duplex': 'full',
                      'Name': '',
                      'Port': 'Gi0/15',
                      'Speed': '1000',
                      'Status': 'connected',
                      'Type': '1000BaseLX SFP',
                      'Vlan': 'trunk'},
                     {'Duplex': 'full',
                      'Name': 'pitrs2201 te1/1/4',
                      'Port': 'Gi0/16',
                      'Speed': '1000',
                      'Status': 'connected',
                      'Type': '1000BaseLX SFP',
                      'Vlan': 'trunk'}]]]
    
# test_headers_indicator_columns_merged()

def test_headers_indicator_tab_indented_header():
    template = """
<input load="text">
	Network            Next Hop            Metric     LocPrf     Weight Path
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
    assert res == [[[{'LocPrf': '',
    'Metric': '0',
    'Network': '*>ef11.11.1.111/32',
    'Next_Hop': '12.123.12.1',
    'Path': '65000 ?',
    'Weight': '0'},
   {'LocPrf': '',
    'Metric': '0',
    'Network': '*>ef222.222.222.2/32',
    'Next_Hop': '12.123.12.1',
    'Path': '65000 ?',
    'Weight': '0'},
   {'LocPrf': '',
    'Metric': '0',
    'Network': '*>ef333.333.333.333/32',
    'Next_Hop': '12.123.12.1',
    'Path': '65000 ?',
    'Weight': '0'}]]]
    
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
    pprint.pprint(res)
    
# test_headers_docs_example()