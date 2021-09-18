"""
Validate results using YANG modules.

Dependencies:

 - yangson: python -m pip install yangson; https://github.com/CZ-NIC/yangson

On each call, generates YANG library data in JSON format in accordance with
RFC7895. YANG library used to validate results structures for compatibility
with certain YANG modules.

YANG library can be provided within output tag or using yang_mod_lib attribute,
in that case, YANG JSON library generation step will be skipped. That
can increase execution time.

YANGSON git repository tools/python/mkylib.py script can be used to generates
YANG JSON library of YANG modules used for validation.
"""
import logging
import json
import os
import traceback

log = logging.getLogger(__name__)

try:
    from yangson.statement import ModuleParser
    from yangson import DataModel
    from yangson import enumerations

    HAS_LIBS = True
except ImportError:
    log.error(
        "ttp.yang_validate, failed to import Cerberus library, make sure it is installed"
    )
    HAS_LIBS = False

data_kws = [
    "augment",
    "container",
    "leaf",
    "leaf-list",
    "list",
    "rpc",
    "notification",
    "identity",
]
"""Keywords of statements that contribute nodes to the schema tree."""

modmap = {}
"""Dictionary for collecting module data."""

submodmap = {}
"""Dictionary for collecting submodule data."""


def _module_entry(yfile):
    """Add entry for one file containing YANG module text.
    Args:
        yfile (file): File containing a YANG module or submodule.
    """
    ytxt = yfile.read()
    mp = ModuleParser(ytxt)
    mst = mp.statement()
    submod = mst.keyword == "submodule"
    import_only = True
    rev = ""
    features = []
    includes = []
    rec = {}
    for sst in mst.substatements:
        if not rev and sst.keyword == "revision":
            rev = sst.argument
        elif import_only and sst.keyword in data_kws:
            import_only = False
        elif sst.keyword == "feature":
            features.append(sst.argument)
        elif submod:
            continue
        elif sst.keyword == "namespace":
            rec["namespace"] = sst.argument
        elif sst.keyword == "include":
            rd = sst.find1("revision-date")
            includes.append((sst.argument, rd.argument if rd else None))
    rec["import-only"] = import_only
    rec["features"] = features
    if submod:
        rec["revision"] = rev
        submodmap[mst.argument] = rec
    else:
        rec["includes"] = includes
        modmap[(mst.argument, rev)] = rec


def _make_library(ydir):
    """
    Make JSON library of YANG modules.
    Args:
        ydir (str): Name of the directory with YANG (sub)modules.
    """
    for infile in os.listdir(ydir):
        if not infile.endswith(".yang"):
            continue
        with open(
            "{ydir}/{infile}".format(ydir=ydir, infile=infile), "r", encoding="utf-8"
        ) as yf:
            _module_entry(yf)
    marr = []
    for (yam, mrev) in modmap:
        men = {"name": yam, "revision": mrev}
        sarr = []
        mrec = modmap[(yam, mrev)]
        men["namespace"] = mrec["namespace"]
        fts = mrec["features"]
        imp_only = mrec["import-only"]
        for (subm, srev) in mrec["includes"]:
            sen = {"name": subm}
            try:
                srec = submodmap[subm]
            except KeyError:
                print("Submodule {} not available.".format(subm))
                return 1
            if srev is None or srev == srec["revision"]:
                sen["revision"] = srec["revision"]
            else:
                print("Submodule {} revision mismatch.".format(subm))
                return 1
            imp_only = imp_only or srec["import-only"]
            fts += srec["features"]
            sarr.append(sen)
        if fts:
            men["feature"] = fts
        if sarr:
            men["submodule"] = sarr
        men["conformance-type"] = "import" if imp_only else "implement"
        marr.append(men)
    res = {"ietf-yang-library:modules-state": {"module-set-id": "", "module": marr}}
    return json.dumps(res, indent=2)


def validate_yangson(
    instance_data,
    yang_mod_dir,
    yang_mod_lib=None,
    validation_scope="all",
    content_type="all",
    to_xml=False,
    metadata=True,
):
    """
    Validate instance_data for compliance with YANG modules at
    yang_mod_dir directory.

    Args:
        instance_data (dictionary or list): parsing results to validate
        yang_mod_dir (str): OS path to directory with YANG modules
        yang_mod_lib (str): optional, OS path to file with JSON-encoded YANG library data [RFC7895]
        content_type (str): optional, content type
            as per https://yangson.labs.nic.cz/enumerations.html
            supported - all, config, nonconfig
        validation_scope (str): optional, validation scope
            as per https://yangson.labs.nic.cz/enumerations.html
            supported - all, semantics, syntax
        to_xml (bool): default is False, converts results to XML if True
        metadata (bool): default is True, return data with validation results

    Returns:

        Dictionary of if metadata is True::
            {
                "result": instance_data or to_xml results,
                "exception": {},
                "valid": {},
                "comment": ""
            }

        If metadata is False returns results as is on successful validation or False otherwise

        If metadata is False but to_xml is True, return parsing results converted to XML string
    """
    if to_xml:
        from xml.etree import cElementTree as ET
    ret = {
        "result": [] if to_xml else instance_data,
        "exception": {},
        "valid": {},
        "comment": "",
    }

    if not HAS_LIBS:
        ret["comment"] = "Failed to import yangson library, make sure it is installed."
        ret["exception"] = {0: "ImportError"}
        ret["valid"] = {0: False}
    output_tag_load = _ttp_["output_object"].tag_load

    # load yang_modules_library and instantiate DataModel object
    try:
        if output_tag_load and isinstance(output_tag_load, str):
            yang_modules_library = output_tag_load
        elif yang_mod_lib:
            with open(yang_mod_lib, "r") as f:
                yang_modules_library = f.read()
        else:
            yang_modules_library = _make_library(yang_mod_dir)
        dm = DataModel(yltxt=yang_modules_library, mod_path=[yang_mod_dir])
    except:
        ret["exception"] = traceback.format_exc()
        ret["success"] = False
        ret[
            "comment"
        ] = "Failed to instantiate DataModel, check YANG library and path to YANG modules."
        if not metadata:
            return False
        else:
            return ret

    # decide on scopes and content
    if validation_scope == "all":
        scope = enumerations.ValidationScope.all
    elif validation_scope == "semantics":
        scope = enumerations.ValidationScope.semantics
    elif validation_scope == "syntax":
        scope = enumerations.ValidationScope.syntax
    if content_type == "all":
        ctype = enumerations.ContentType.all
    elif content_type == "config":
        ctype = enumerations.ContentType.config
    elif content_type == "nonconfig":
        ctype = enumerations.ContentType.nonconfig

    # run validation of data
    if isinstance(instance_data, list):
        for index, item in enumerate(instance_data):
            try:
                inst = dm.from_raw(item)
                inst.validate(scope=scope, ctype=ctype)
                ret["valid"][index] = True
                if to_xml:
                    ret["result"].append(ET.tostring(inst.to_xml(), encoding="unicode"))
            except:
                if not metadata:
                    return False
                ret["exception"][index] = traceback.format_exc()
                ret["valid"][index] = False
    elif isinstance(instance_data, dict):
        try:
            inst = dm.from_raw(instance_data)
            inst.validate(scope=scope, ctype=ctype)
            ret["valid"] = True
            if to_xml:
                ret["result"] = ET.tostring(inst.to_xml(), encoding="unicode")
        except:
            if not metadata:
                return False
            ret["exception"] = traceback.format_exc()
            ret["valid"] = False

    # return results
    if not metadata:
        return ret["result"]
    else:
        return ret
