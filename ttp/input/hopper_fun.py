import getpass
from hopper import hopper
import logging
log = logging.getLogger(__name__)

_name_map_ = {
"hopper_fun": "hopper"
}

def hopper_fun(input_name, **kwargs):
    devices = kwargs.get("devices", [])
    commands = kwargs.get("commands", [])
    credentials = kwargs.get("credentials", [])
    max_connections = kwargs.get("max_connections", 1)
    process_output = kwargs.get("process_output", "pyte")
    username = kwargs.get("username", None)
    password = kwargs.get("password", None)
    if username == "get_user_input":
        username = input('{}, enter username: '.format(input_name))
    if password == "get_user_pass":
        password = getpass.getpass('{}, enter password: '.format(input_name))
    credentials.append((username, password,))
    log.info("TTP hopper_fun: sending - '{}', to - '{}'".format(commands, devices))
    # get data from devices
    hopperObj = hopper()
    result = hopperObj.run(
        devices=devices, 
        commands=commands, 
        credentials=credentials, 
        max_connections=max_connections, 
        process_output=process_output
    )
    log.info("TTP hopper_fun: received output from {} devices".format(len(result.keys())))
    return list(result.values())