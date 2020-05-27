import logging
import json
log = logging.getLogger(__name__)

try:
    from cerberus import Validator
    HAS_LIBS = True
except ImportError:
    log.error("ttp.validate, failed to import Cerberus library, make sure it is installed")
    HAS_LIBS = False
    
if HAS_LIBS:
    validator_engine = Validator()

def validate(data, schema, result="valid", add_fields="", info="", errors="", allow_unknown=True):
    """Function to validate data using Cerberus validation library and 
    return this dictionary
    {
        result field: True|False
        "info": check_info
        errors field: validation errors  
        additional fields from add_fields
    }
    Args::
        * schema - schema template variable name
        * result - name of the field to assign validation result
        * info - string, contain additionalinformation about test
        * errors - name of the field to assign validation errors
        * allow_unknown - informs cerberus to ignore uncknown keys
        * add_fields - comma separated string of key names to add to result
    """
    if not HAS_LIBS:
        return data
    # get validation schema from template variables
    schema_data = _ttp_["output_object"].template_obj.vars.get(schema, None)
    if not schema_data:
        log.error("ttp.output.validate, schema '{}' not found".format(schema))
        return data    
    # run validation
    validator_engine.allow_unknown = allow_unknown
    if "_anonymous_" in data:
        validation_result = validator_engine.validate(document=data["_anonymous_"], schema=schema_data)
    else:
        validation_result = validator_engine.validate(document=data, schema=schema_data)  
    # form result
    ret = {
        result: validation_result
    }
    if info:
        ret["info"] = info
    if errors:
        ret[errors] = validator_engine.errors
    # add additional fields
    add_fields = [i.strip() for i in add_fields.split(",")]
    for field_name in add_fields:
        if data.get(field_name):
            ret[field_name] = data[field_name]
        elif field_name in _ttp_["output_object"].template_obj.vars:
            ret[field_name] = data[field_name]
        elif field_name in _ttp_["global_vars"]:
            ret[field_name] = _ttp_["global_vars"][field_name]
    return ret