from model.model import Model
from parser.parser import Parser

if __name__ == "__main__":
  # hotel_tiket_json = "scraping-tiket-hotel-details.json"
  # hote_traveloka_json = "scraping-traveloka-hotel-details.json"
  transstudio_json = "transstudio.json"
  sempro_pdf = "Laporan-TA-Capstone-13521116.pdf"

  parser = Parser()
  parser.parse_json(transstudio_json)
  parser.parse_document(sempro_pdf)
  documents, metadata = parser.get_results()


  context = "The primary role of this agent is to answer prompt from user with relevant answer regarding the documents. The answer can be in english."
  model = Model()
  model.learn(documents, metadata)
  model.config(context)

  while True:
    prompt = input("Insert a prompt (q to quit): ")

    if (prompt == "q"):
      break
    else:
      result = model.answer(prompt)
      print(result)


  