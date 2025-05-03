from parser.parser import Parser


if __name__ == "__main__":
  parser = Parser()
  parser.parse_json("transstudio")
  parser.parse_document("Laporan-TA-Capstone-13521116")
  parser.parse_json("scraping-traveloka-hotel-details")
  parser.store_results()