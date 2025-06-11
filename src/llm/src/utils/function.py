from llama_index.core import Document
from llama_index.core.node_parser import SimpleNodeParser

# def json_to_string_list(data: dict, prefix: str, result_arr: list, max_limit_arr: int = 20):
#   """
#   Convert json data, convert it to list of string iteratively
#   """
#   for key, val in data.items():
#     adjusted_prefix = f"{prefix}-{key}"

#     # Pass if the value is None
#     if (val is None):
#       continue

#     if (isinstance(val, dict)):
#       json_to_string_list(val, adjusted_prefix, result_arr)

#     elif (isinstance(val, list)):
#       # Pass if empty list
#       if (len(val) == 0):
#         continue

#       if (isinstance(val[0], dict)):
#         for idx, arr_val in enumerate(val[:min(len(val), max_limit_arr)]):
#           json_to_string_list(arr_val, f"{adjusted_prefix}-{idx}", result_arr)
#       else:
#         val = [str(data_val) for data_val in val]
#         data_str = f"{adjusted_prefix}: {', '.join(val)}"
#         result_arr.append(data_str)
#     else:
#       data_str = f"{adjusted_prefix}: {str(val)}"
#       result_arr.append(data_str)


def json_to_string(data : dict, indent: int = 0) -> str:
  """
  Convert json data to string with indentation
  Assuming the data is a dictionary with key-value pairs
  """
  result = ""
  for key, value in data.items():
      result += (" "*2*indent) + f"{key}: {value}\n"
  return result


def hotel_data_to_string_list(data: dict, max_limit_arr: int = 20) -> list[str]:
  """
  Convert hotel data to list of string
  """
  # Delete unnecessary columns
  del data["_id"]
  # Use title as id, assuming it is unique for all data
  name = data["title"]
  del data["title"]

  # Define fields to be extracted
  basic_info_fields = ["location", "checkIn", "checkOut", "description", "traveloka_url", "tiket_url"]
  facilities_fields = ["facilities"]
  general_info_fields = ["generalInformations"]
  data_list = ["" for _ in range(4)]
  reviews_list = []
  
  data_list[0] = f"{name} Basic Information:\n"
  data_list[3] = f"{name} Other Information:\n"
  for key, val in data.items():
    if (key in basic_info_fields):
      data_list[0] += f"  {key}: {val}\n"
    elif (key in facilities_fields):
      data_list[1] = f"{name} Facilities:\n"
      data_list[1] += json_to_string(val, 1)
    elif (key in general_info_fields):
      data_list[2] = f"{name} General Information:\n"
      data_list[2] += json_to_string(val, 1)
    elif (key == "reviews"):
      for i in range(min(len(val), max_limit_arr)):
        review = val[i]
        review_str = f"{name} Review {i+1}:\n"
        review_str += json_to_string(review, 1)
        reviews_list.append(review_str)
    else:
      if (isinstance(val, dict)):
        text_val = f"  {name} {key}:\n"
        text_val += json_to_string(val, 2)
        data_list[3] += text_val + "\n"
      elif (isinstance(val, str)):
        text_val = f"{name} {key}: val\n"
        data_list[3] += text_val
  
  # Combine all information into a single list
  data_list.extend(reviews_list)
  data_list = [info for info in data_list if info.strip() != ""]  # Remove empty strings
  return data_list


def text_to_document(text_list: list[str]) -> list[Document]:
  """
  Make string text to Document type of LlamaIndex
  """
  return [Document(text=text) for text in text_list]


def parse_documents(document_list: list[Document]) -> list:
  """
  Parse documents using LlamaIndex parser
  """
  parser = SimpleNodeParser()
  return parser.get_nodes_from_documents(document_list)


def display_nested_list(nested_list:list, indent: int = 0) -> None:
  """
  Display nested list with indentation
  """
  for item in nested_list:
    if isinstance(item, list):
      display_nested_list(item, indent + 1)
    else:
      print((" " * 2 * indent) + item)
      print("========================")


def clean_quotation_string(text: str) -> str:
  if ("\"" == text[0] and "\"" == text[-1]):
    return text[1:-1]
  else:
    return text