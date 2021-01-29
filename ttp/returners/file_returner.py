import time
import logging
import os

_name_map_ = {"file_returner": "file"}

log = logging.getLogger(__name__)
ctime = time.strftime("%Y-%m-%d_%H-%M-%S")


def file_returner(D, **kwargs):
    """Method to write data into file
    Args:
        url (str): os path there to save files
        filename (str): name of the file
    """
    url = kwargs.get("url", "./Output/")
    if "filename" in kwargs:
        filename = kwargs["filename"]
        try:
            fkwargs = _ttp_["global_vars"].copy()
            fkwargs.update(_ttp_["vars"])
            filename = filename.format(**fkwargs)
        except Exception as e:
            log.error("file_returner: failed format filename - '{}'".format(e))
    else:
        filename = "output_{}.txt".format(ctime)
    # if no filename provided, add outputter name to filename
    if not kwargs.get("filename", False):
        filename = _ttp_["output_object"].name + "_" + filename
    # check if path exists already, create it if not:
    if not os.path.exists(url):
        os.mkdir(url)
    # form file path:
    file_path = os.path.join(url, filename)
    # save excel workbook to file:
    if hasattr(D, "save") and hasattr(D, "worksheets"):
        log.info("output.returner_file: saving excel workbook")
        if not file_path.endswith(".xlsx"):
            file_path += ".xlsx"
        D.save(file_path)
    # save data to text file
    else:
        log.info("output.returner_file: saving text results to file")
        with open(file_path, "w") as f:
            if not isinstance(D, str):
                f.write(str(D))
            else:
                f.write(D)
