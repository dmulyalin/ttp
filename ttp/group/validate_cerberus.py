import logging
log = logging.getLogger(__name__)

try:
    from cerberus import Validator
    HAS_LIBS = True
except ImportError:
    log.error("ttp.cerberus, failed to import Cerberus library, make sure it is installed")
    HAS_LIBS = False
    
if HAS_LIBS:
    validator_engine = Validator()

_name_map_ = {
    "cerberus_validate": "cerberus"
}

def cerberus_validate(data, schema, log_errors=False, allow_unknown=True, add_errors=False):
    """Function to validate data using validation libraries, such as Cerberus.
    """
    if not HAS_LIBS:
        return data, None
    # get validation schema        
    schema_data = _ttp_["parser_object"].vars.get(schema, None)
    if not schema_data:
        log.error("ttp.validate, schema '{}' not found".format(schema))
        return data, None          
    # run validation
    validator_engine.allow_unknown = allow_unknown
    ret = validator_engine.validate(document=data, schema=schema_data)
    if ret == False:
        if log_errors:
            log.warning("ttp.validate, data: '{}', Cerberus validation errors: {}".format(data, str(validator_engine.errors))) 
        if add_errors:
            data["validation_errors"] = validator_engine.errors
            return data, None
    return data, ret
    
def validate(data, schema, add_field="", test_info="", add_errors=False, log_errors=False, allow_unknown=True):
    """Function to validate data using Cerberus validation library and either return dictionary of:
    {
        valid: True:False
        check_info: check_info
    }
    or, if add_field is not empty, add new field to data with True|False 
    value depending on validation    results
    """
    if not HAS_LIBS:
        return data, None
    # get validation schema        
    schema_data = _ttp_["parser_object"].vars.get(schema, None)
    if not schema_data:
        log.error("ttp.validate, schema '{}' not found".format(schema))
        return data, None          
    # run validation
    validator_engine.allow_unknown = allow_unknown
    ret = validator_engine.validate(document=data, schema=schema_data)
    # log errors if told to do so
    if ret == False and log_errors:
        log.warning("ttp.validate, data: '{}', Cerberus validation errors: {}".format(data, str(validator_engine.errors))) 
    # decide to add new field or replace results
    if add_field.strip() != "":  
        data[add_field] = ret
    else:
        data = {
            "valid": ret
        }
    # add validation errors ifrequested to do so
    if add_errors:
        data["validation_errors"] = validator_engine.errors
    if test_info.strip():
        data["test_info"] = test_info
    return data, None  