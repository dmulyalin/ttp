import logging
log = logging.getLogger(__name__)

try:
    from deepdiff import DeepDiff
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False
    log.error('ttp.output failed to import deepdiff library, make sure it is installed')

_name_map_ = {
"deepdiff_func": "deepdiff"
}


def deepdiff_func(data, before, after, add_field=False, **kwargs):
    """
    Function to compare two structures.
    
    * before - name of input that contains old data
    * after - name of input that contains new data
	* add_key - name of the key to add to data instead of replacing it
	* kwargs - arguments supported by deepdiff DeepDiff class e.g. ignore_order or verbose_level
    """
    if not isinstance(data, list):
        return data
    # get template object of this output
    template_obj = _ttp_['output_object'].template_obj
    if not template_obj:
        return data
    # get 'before' input index
    before_index = list(template_obj.inputs.keys()).index(before)
    after_index = list(template_obj.inputs.keys()).index(after)
    # run compare
    result = DeepDiff(data[before_index], data[after_index], **kwargs)
    # return results
    if add_field:
        data.append({add_field: result})
        return data
    else:
        return result