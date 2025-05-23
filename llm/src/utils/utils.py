

def json_to_string_list(data: dict, prefix: str, result_arr: list):

  for key, val in data.items():
    adjusted_prefix = f"{prefix}-{key}"
    if (isinstance(val, dict)):
      json_to_string_list(val, adjusted_prefix, result_arr)
    else:
      data_str = f"{adjusted_prefix}: {str(val)}"
      result_arr.append(data_str)

  return data_str