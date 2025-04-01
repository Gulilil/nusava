from parser.parser import Parser

if __name__ == "__main__":
  parser = Parser()
  parser.parse_documents()
  parser.store_results()
  