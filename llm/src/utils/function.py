from llama_index.core import Document
from llama_index.core.node_parser import SimpleNodeParser

# Convert json data, convert it to list of string iteratively
def json_to_string_list(data: dict, prefix: str, result_arr: list, max_limit_arr: int = 20):
  for key, val in data.items():
    adjusted_prefix = f"{prefix}-{key}"

    # Pass if the value is None
    if (val is None):
      continue

    if (isinstance(val, dict)):
      json_to_string_list(val, adjusted_prefix, result_arr)

    elif (isinstance(val, list)):
      # Pass if empty list
      if (len(val) == 0):
        continue

      if (isinstance(val[0], dict)):
        for idx, arr_val in enumerate(val[:min(len(val), max_limit_arr)]):
          json_to_string_list(arr_val, f"{adjusted_prefix}-{idx}", result_arr)
      else:
        val = [str(data_val) for data_val in val]
        data_str = f"{adjusted_prefix}: {', '.join(val)}"
        result_arr.append(data_str)
    else:
      data_str = f"{adjusted_prefix}: {str(val)}"
      result_arr.append(data_str)


# Make string text to Document type of LlamaIndex
def text_to_document(text_list: list[str]) -> list[Document]:
  return [Document(text=text) for text in text_list]


# Parse documents
def parse_documents(document_list: list[Document]) :
  parser = SimpleNodeParser()
  return parser.get_nodes_from_documents(document_list)