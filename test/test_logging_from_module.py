from ttp import ttp

test217="""
<input load="text" name='in1' preference="merge">
user.name@host-site-sw1> show configuration interfaces | display set 
set interfaces vlan unit 17 description "som if descript"
set interfaces vlan unit 17 family inet address 20.17.1.253/23 vrrp-group 25 virtual-address 20.17.1.254
set interfaces vlan unit 17 family inet address 20.17.1.252/23
</input>

<group name="bla" output="not exists" func_not_exists="bla">
set interfaces {{ interface }} unit {{ unit }} family inet address {{ ip | to_ip }} vrrp-group {{ vrrp_id }} virtual-address {{ vrrp_vip }}
set interfaces {{ interface }} unit {{ unit }} description "{{ description | ORPHRASE }}"
{{ hostname | set("hostname") }}
{{ group | set("group-0") }}
</group>
"""

parser_Obj = ttp(template=test217, log_level="DEBUG", log_file="myfile.txt")
parser_Obj.result(format='json', returner='terminal')