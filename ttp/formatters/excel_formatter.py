import logging
log = logging.getLogger(__name__)

try:
    from openpyxl import Workbook
except ImportError:
    log.critical("output.formatter_excel: openpyxl not installed, install: 'python -m pip install openpyxl'. Exiting")
    raise SystemExit()
		
_name_map_ = {
"excel_formatter": "excel"
}

def excel_formatter(data):
    """Method to format data as an .xlsx table using openpyxl module.
    """        
    # form table_tabs - list of dictionaries
    try:
        table = _ttp_["output_object"].attributes['load']['table']
    except KeyError:
        log.critical("output.formatter_excel: output tag missing table definition. Exiting")
        raise SystemExit()
    table_tabs = []
    for index, tab_det in enumerate(table):
        if 'tab_name' in tab_det:
            tab_name = tab_det.pop('tab_name')
        else:
            tab_name = "Sheet{}".format(index)
        # get attributes out of tab_det
        _ttp_["output_object"].get_attributes(data={
            "path": tab_det.get("path", []),
            "headers": tab_det.get("headers", None),
            "missing": tab_det.get("missing", ""),
            "key": tab_det.get("key", "")
        })
        # form tab table
        tab_table_data = _ttp_["formatters"]["table"](data)
        table_tabs.append({"name": tab_name, "data": tab_table_data})
    # create workbook
    wb = Workbook(write_only=True)
    for tab in table_tabs:
        ws = wb.create_sheet(title=tab["name"])
        [ws.append(row) for row in tab["data"]]
    return wb