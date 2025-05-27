from llama_index.core import Document

def json_to_string_list(data: dict, prefix: str, result_arr: list):

  for key, val in data.items():
    adjusted_prefix = f"{prefix}-{key}"
    if (isinstance(val, dict)):
      json_to_string_list(val, adjusted_prefix, result_arr)

    elif (isinstance(val, list)):
      if (isinstance(val[0], dict)):
        for idx, arr_val in enumerate(val):
          json_to_string_list(arr_val, f"{adjusted_prefix}-{idx}", result_arr)
      else:
        val = [str(data_val) for data_val in val]
        data_str = f"{adjusted_prefix}: {', '.join(val)}"
        result_arr.append(data_str)
    else:
      data_str = f"{adjusted_prefix}: {str(val)}"
      result_arr.append(data_str)


def text_to_document(text_list: list[str]) -> list[Document]:
  return [Document(text=text) for text in text_list]