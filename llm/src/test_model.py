from model.model import Model
import os
from utils.constant import DATA_DIR_PATHS

if __name__ == "__main__":
  document_text_list = []
  document_name_list = []
  document_description_list = []
  
  # document_name = "transstudio_json"
  # document_description = "Ticket details of Trans Studio Mini Kupang"
  # with open(os.path.join(DATA_DIR_PATHS['md'], document_name), "r", encoding="utf-8") as f:
  #   document_text = f.read()
  # document_text_list.append(document_text)
  # document_name_list.append(document_name)
  # document_description_list.append(document_description)

  document_name = "json_scraping-tiket-hotel-details.md"
  document_description = "Ticket details for hotel bookings from Tiket source"
  with open(os.path.join(DATA_DIR_PATHS['md'], document_name), "r", encoding="utf-8") as f:
    document_text = f.read()
  document_text_list.append(document_text)
  document_name_list.append(document_name)
  document_description_list.append(document_description)

  document_name = "json_scraping-traveloka-hotel-details.md"
  document_description = "Ticket details for hotel bookings from Traveloka source"
  with open(os.path.join(DATA_DIR_PATHS['md'], document_name), "r", encoding="utf-8") as f:
    document_text = f.read()
  document_text_list.append(document_text)
  document_name_list.append(document_name)
  document_description_list.append(document_description)

  context = "The primary role of this agent is to answer prompt from user with relevant answer regarding the documents. The answer can be in english."

  model = Model()
  model.learn(document_text_list, document_name_list, document_description_list)
  model.config(context)

  while True:
    prompt = input("Insert a prompt (q to quit): ")

    if (prompt == "q"):
      break
    else:
      result = model.answer(prompt)
      print(result)


  