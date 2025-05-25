from parser.parser import Parser


if __name__ == "__main__":
  parser = Parser()
  parser.parse_json("trans_studio")
  parser.store_results()