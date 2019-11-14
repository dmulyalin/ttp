import logging
log = logging.getLogger(__name__)

try:
    from cerberus import Validator
    HAS_LIBS = True
except ImportError:
    log.error("ttp.validate, failed to import Cerberus library, make sure it is installed")
    HAS_LIBS = False

def validate(data, schema, log_errors=False, allow_unknown=True, add_errors=False):
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
    validator_engine = Validator(schema_data, allow_unknown=allow_unknown)
    ret = validator_engine.validate(data)
    if ret == False:
        if log_errors:
            log.warning("ttp.validate, data: '{}', Cerberus validation errors: {}".format(data, str(validator_engine.errors))) 
        if add_errors:
            data["validation_errors"] = validator_engine.errors
            return data, None
    return data, ret