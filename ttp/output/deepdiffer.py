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


def deepdiff_func(data, before, after, keep_results=False):
    """
    Function to compare two structures.
    
    * before - name of input that contains old data
    * after - name of input that contains new data
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
    result = DeepDiff(data[before_index], data[after_index], ignore_order=True, verbose_level=2)
    if keep_results:
        data.append({'deepdiff': result})
        return data
    else:
        return result