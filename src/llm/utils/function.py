from llama_index.core import Document
from llama_index.core.node_parser import SimpleNodeParser
from datetime import datetime, timedelta, timezone

def json_to_string_list(data: dict, prefix: str, result_arr: list, max_limit_arr: int = 20):
  """
  Convert json data, convert it to list of string iteratively
  Use result_arr as the output list
  """
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


def json_to_string(data : dict, indent: int = 0) -> str:
  """
  Convert json data to string with indentation
  Assuming the data is a dictionary with key-value pairs
  """
  result = ""
  for key, value in data.items():
      result += (" "*2*indent) + f"{key}: {value}\n"
  return result


def text_to_document(text_list: list[str]) -> list[Document]:
  """
  Make string text to Document type of LlamaIndex
  """
  return [Document(text=text) for text in text_list]


def sanitize_text_to_list(text: str) -> list[str]:
  text_splitted = text.split("\n")
  return [subtext for subtext in text_splitted if (len(subtext.strip()) > 0)]


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


def attraction_data_to_string_list(data: dict, max_limit_arr: int = 20) -> list[str]:
  """
  Convert hotel data to list of string
  """
  # Delete unnecessary columns
  del data["_id"]
  # Use title as id, assuming it is unique for all data
  name = data["title"]
  del data["title"]

  # Define fields to be extracted
  general_info_fields = ["locationText", "location", "url", "contact", "phoneNumberText", "description", "rating", "label"]
  more_info_fields = ["moreInfo", "guide"]
  data_list = ["" for _ in range(2)]
  reviews_list = []
  opening_hours_list = []
  
  data_list[0] = f"{name} Basic Information:\n"
  for key, val in data.items():
    if (key in general_info_fields):
      data_list[0] += f"  {key}: {val}\n"
    elif (key in more_info_fields):
      if (isinstance(val, dict)):
        data_list[1] += json_to_string(val, 1)
      else:
        data_list[1] += f"  {key}: {val}\n"
    elif ((key == "reviews" or key == "allReviews") and len(val)> 0):
      for i in range(min(len(val), max_limit_arr)):
        review = val[i]
        review_str = f"{name} Review {i+1}:\n"
        review_str += json_to_string(review, 1)
        reviews_list.append(review_str)
    elif (key == "openingHours" and len(val) > 0):
      for i in range(len(val)):
        opening_hour = val[i]
        opening_hour_str = json_to_string(opening_hour, 1)
        opening_hours_list.append(opening_hour_str)

  # Combine all information into a single list
  data_list.extend(reviews_list)
  data_list.extend(opening_hours_list)
  data_list = [info for info in data_list if info.strip() != ""]  # Remove empty strings
  return data_list


def adjust_scheduled_time(scheduled_time_str: str) -> datetime:
    """
    Adjust the scheduled time so it does not return time earlier then current time.
    If it is earlier, return the date to be tomorrow's date but leave the hour as it is
    """
    # Define UTC+7 timezone
    utc_plus_7 = timezone(timedelta(hours=7))

    # Parse input time and make it timezone-aware in UTC+7
    scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S")
    scheduled_time = scheduled_time.replace(tzinfo=utc_plus_7)

    # Get current time in UTC+7
    current_time = datetime.now(timezone.utc).astimezone(utc_plus_7)

    # Compare and adjust if needed
    if scheduled_time < current_time:
      scheduled_time = scheduled_time.replace(
          year=current_time.year,
          month=current_time.month,
          day=current_time.day
      ) + timedelta(days=1)
    return scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
