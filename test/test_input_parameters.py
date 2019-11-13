template = """
<input name="my_input" load="yaml">
my_params:
  key1: val1
  key2: val2
  
more_params:
  - item1
  - item2
  - item3
</input>

<group name = "{{ timestamp }}.{{ interface }}">
{{ interface }} is up, line protocol is up
     {{ in_pkts}} packets input, 25963 bytes, 0 no buffer
     {{ out_pkts }} packets output, 26812 bytes, 0 underruns
</group>
"""

from ttp import ttp
import pprint

parser = ttp(template=template)
pprint.pprint(parser.get_input_load())