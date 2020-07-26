import logging
import logging.handlers
import json

log = logging.getLogger(__name__)

def syslog(data):
    attributes = _ttp_["output_object"].attributes['load']
    address = attributes.get('address', None)
    port = int(attributes.get('port', 514))   
    facility = attributes.get('facility', 77)
    path = attributes.get('path', [])    
    # initiate isolated logger
    if address is None:
        log.error("ttp.returners.syslog: no remote syslog address found, doing nothing...")
        return 
    syslog_logger = logging.getLogger("_Custom_Syslog_Logger_")
    syslog_logger.propagate = False
    syslog_logger.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address=(address, port,), facility=facility)
    handler.append_nul = False
    syslog_logger.addHandler(handler)
    # normalize source_data to list:
    source_data = []
    source_data += data if isinstance(data, list) else [data]
    # send data
    for datum in source_data:
        item = _ttp_["output"]["traverse"](datum, path)
        if not item: # skip empty results
            continue
        elif isinstance(item, list):
            [syslog_logger.info(json.dumps(i)) for i in item]
        elif isinstance(item, dict):
            syslog_logger.info(json.dumps(item))
    # clean up
    handler.close()
    del handler
    del syslog_logger