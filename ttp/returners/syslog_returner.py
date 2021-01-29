import logging
import logging.handlers
import json
import time
import traceback

log = logging.getLogger(__name__)


def syslog(data, **kwargs):
    # get kwargs
    servers = kwargs.get("servers", None)
    servers = [servers] if isinstance(servers, str) else servers
    if not servers:
        log.error(
            "ttp.returners.syslog: no syslog servers addresses found, doing nothing..."
        )
        return
    port = int(kwargs.get("port", 514))
    facility = kwargs.get("facility", 77)
    path = kwargs.get("path", [])
    iterate = kwargs.get("iterate", True)
    interval = kwargs.get("interval", 1) / 1000
    # normalize source_data to list:
    source_data = data if isinstance(data, list) else [data]
    # initiate isolated logger
    syslog_logger = logging.getLogger("_Custom_Syslog_Logger_")
    syslog_logger.propagate = False
    syslog_logger.setLevel(logging.INFO)
    for server in servers:
        handler = logging.handlers.SysLogHandler(
            address=(server, port), facility=facility
        )
        handler.append_nul = False
        syslog_logger.addHandler(handler)
        # send data
        for datum in source_data:
            if not datum:
                log.error(
                    "TTP:syslog returner, datum '{}' is empty, path: '{}'".format(
                        str(datum), path
                    )
                )
                continue
            try:
                item = _ttp_["output"]["traverse"](datum, path)
            except:
                tb = traceback.format_exc()
                log.error(
                    "TTP:syslog returner, failed traverse data, path: '{}', error:\n'{}\ndatum: {}..".format(

                        path, tb, str(datum)[:120]
                    )
                )
                continue
            if not item:  # skip empty results
                continue
            elif isinstance(item, list) and iterate:
                for i in item:
                    time.sleep(interval)
                    try:
                        syslog_logger.info(json.dumps(i))
                    except:
                        tb = traceback.format_exc()
                        log.error(
                            "TTP:syslog returner, failed send log item; path: '{}', error:\n'{}".format(
                                path, tb
                            )
                        )
            else:
                time.sleep(interval)
                try:
                    syslog_logger.info(json.dumps(item))
                except:
                    tb = traceback.format_exc()
                    log.error(
                        "TTP:syslog returner, failed send log item; path: '{}', error:\n'{}".format(
                            path, tb
                        )
                    )
        # clean up
        handler.close()
        syslog_logger.removeHandler(handler)
    del syslog_logger
