def line_number(data, new_field, context):
    span_length = context.match.end() - context.match.start()
    if _ttp_["parser_object"].DATANAME == "text_data":
        line_number = _ttp_["parser_object"].DATATEXT[:context.span_start + span_length].count("\n")
        return data, {"new_field": {new_field: line_number}}
    return data, True
