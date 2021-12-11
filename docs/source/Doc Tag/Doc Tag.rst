Doc Tag
=======

Doc tag allows to add any notes or documentation to TTP template. In addition content of all ``doc`` tags
assigned to ``__doc__`` attribute of the template objects within TTP parser object.

.. warning:: Doc tag cannot contain ``<`` and ``>`` characters, have to use escape sequences instead - ``&lt`` and ``&gt``

Single template can contain as many ``<doc>`` tags as required at the top level of the document.

**Example**

In this template ``<doc>`` tag helps to document information about the template and it's usage::

    <doc>
    TTP template to parse Cisco IOS "show ip arp" output.

    Template can be invoked using Netmiko run_ttp method like this:

        import pprint
        from netmiko import ConnectHandler

        net_connect = ConnectHandler(
            device_type="cisco_ios",
            host="1.2.3.4",
            username="admin",
            password="admin",
        )

        res = net_connect.run_ttp("ttp://misc/netmiko/cisco.ios.arp.txt", res_kwargs={"structure": "flat_list"})

        pprint.pprint(res)
    </doc>


    <input>
    commands = [
        "show ip arp"
    ]
    </input>

    <group method="table" to_int="age">
    {{ protocol }} {{ ip | IP }} {{ age | replace("-", "-1") }} {{ mac | mac_eui }} {{ type | let("interface", "Uncknown") }}
    {{ protocol }} {{ ip | IP }} {{ age | replace("-", "-1") }} {{ mac | mac_eui }} {{ type }} {{ interface | resuball("short_interface_names") }}
    </group>

