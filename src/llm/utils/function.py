from llama_index.core import Document
from llama_index.core.node_parser import SimpleNodeParser
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


def json_to_string_list(data, prefix: str, result_arr: list, max_limit_arr: int = 20):
    """
    Convert JSON-like data (dict or list) into a list of strings recursively.
    Supports starting from either a dict or a list.
    """
    if data is None:
        return
    if isinstance(data, dict):
        for key, val in data.items():
            adjusted_prefix = f"{prefix}-{key}" if prefix else key

            if val is None:
                continue

            if isinstance(val, dict):
                json_to_string_list(val, adjusted_prefix, result_arr, max_limit_arr)

            elif isinstance(val, list):
                if len(val) == 0:
                    continue

                if isinstance(val[0], dict):
                    for idx, arr_val in enumerate(val[:min(len(val), max_limit_arr)]):
                        json_to_string_list(arr_val, f"{adjusted_prefix}-{idx}", result_arr, max_limit_arr)
                else:
                    val_strs = [str(v) for v in val]
                    result_arr.append(f"{adjusted_prefix}: {', '.join(val_strs)}")
            else:
                result_arr.append(f"{adjusted_prefix}: {str(val)}")
    elif isinstance(data, list):
        for idx, item in enumerate(data[:min(len(data), max_limit_arr)]):
            json_to_string_list(item, f"{prefix}-{idx}" if prefix else str(idx), result_arr, max_limit_arr)
    else:
        # Primitive values at the top level
        result_arr.append(f"{prefix}: {str(data)}")


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
  

def get_province_from_location(location:str) -> Optional[str]:
  """
  Determine the province based on the location
  """
  ntt_substr = ['NUSA TENGGARA TIM', "EAST NUSA TENGGARA"]
  ntb_substr = ['NUSA TENGGARA BAR', "WEST NUSA TENGGARA"]

  for substr in ntt_substr:
    if (substr in location.upper()):
      return "ntt"
    
  for substr in ntb_substr:
    if (substr in location.upper()):
      return "ntb"

  print(f"[LOCATION UNDETERMINED] {location}")
  return None


def hotel_data_to_string_list(data: dict, max_limit_arr: int = 20) -> list[str]:
  """
  Convert hotel data to list of string
  """
  # Delete unnecessary columns
  if (data.get("_id")): 
    del data["_id"] 
  else:
    print(f"[NO ID FOUND TOURIST ATTRACTION] This is safe error. Only used as a log")

  # Use name as id, assuming it is unique for all data
  # If there is no name, then skip
  name = None 
  if ('name' in data):
    name = data['name']
    del data["name"]
  elif data['title']:
    name = data['title']
    del data["title"]
  if (name is None):
    print(f"[NAME NONE] Skipped")
    return None, None

  # Determined the location of attraction
  location = data['location']
  if (location is None):
    print(f"[LOCATION NONE] Skipped")
    return None, None
  # If the province is not determinable, then skip
  province = get_province_from_location(location)
  if (province is None): 
    return None, None

  # Define fields to be extracted
  # Basic info in idx 0, more info in idx 1
  basic_info_fields = ["location", "checkIn", "checkOut", "description", "url"]
  data_list = ["" for _ in range(2)]
  reviews_list = []
  
  data_list[0] = f"{name} Basic Information:\n"
  for key, val in data.items():
    if (key in basic_info_fields):
      data_list[0] += f"{key}: {val}\n"

    elif (key in ["facilities", "generalInformations", "policies", "additionalRules", "nearbyPlaces"]):
      temp_string_list = []
      json_to_string_list(val, key, temp_string_list)
      text_val = f"{name} {key}:\n"
      text_val += "\n".join(temp_string_list)
      data_list.append(text_val)

    elif (key == "reviews"):
      for i in range(min(len(val), max_limit_arr)):
        review = val[i]
        review_str = f"{name} Review {i+1}:\n"
        review_str += json_to_string(review, 0)
        reviews_list.append(review_str)

    else:
      if (isinstance(val, dict) or (isinstance(val, list))):
        text_val = f"{name} {key}:\n"
        temp_string_list = []
        json_to_string_list(val, key, temp_string_list)
        text_val += "\n".join(temp_string_list)
        data_list[1] += text_val + "\n"
      elif (isinstance(val, str)):
        text_val = f"{name} {key}: {val}\n"
        data_list[1] += text_val
  
  # Combine all information into a single list
  data_list.extend(reviews_list)
  data_list = [info for info in data_list if info.strip() != ""]  # Remove empty strings
  return data_list, province


def attraction_data_to_string_list(data: dict, max_limit_arr: int = 20) -> Tuple[Optional[list[str]], Optional[str]]:
  """
  Convert hotel data to list of string
  """
  # Delete unnecessary columns
  if (data.get("_id")): 
    del data["_id"] 
  else:
    print(f"[NO ID FOUND TOURIST ATTRACTION] This is safe error. Only used as a log")

  # Use title as id, assuming it is unique for all data
  # If there is no title, then skip 
  name = data.get("title", None)
  if (name is None):
    return None, None
  del data["title"]

  # Determined the location of attraction
  location = data['locationText'] if "locationText" in data else data['location']
  province = get_province_from_location(location)

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
  return data_list, province


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
