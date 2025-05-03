from parser.parser import Parser


if __name__ == "__main__":
  parser = Parser()
  parser.parse_json("scraping-tiket-hotel-details")
  parser.parse_json("scraping-traveloka-hotel-details")
  parser.store_results()