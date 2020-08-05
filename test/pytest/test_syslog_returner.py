import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

def test_syslog_returner():
    template = """
<input load="text">
router-2-lab#show ip arp
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  10.1.13.4               -   0050.5685.14d6  ARPA   GigabitEthernet3.13
Internet  10.1.13.5               -   0050.5685.14d7  ARPA   GigabitEthernet4.14
</input>

<input load="text">
router-3-lab#show ip arp
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  10.1.13.1              98   0050.5685.5cd1  ARPA   GigabitEthernet1.11
Internet  10.1.13.3               -   0050.5685.14d5  ARPA   GigabitEthernet2.12
</input>

<vars>hostname="gethostname"</vars>

<group name="arp_table*" method="table">
Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
Internet  {{ ip }}  -                   {{ mac }}  ARPA   {{ interface }}
{{ hostname | set(hostname) }}
</group>

<output returner="syslog" load="python">
servers="192.168.1.175"
port="10514"
path="arp_table"
iterate=True
facility=77
</output>
"""
    parser = ttp(template=template)
    parser.parse()
	
# uncomment to test, need some syslog server running to test, for instance all-in-one graylog VM
# test_syslog_returner()