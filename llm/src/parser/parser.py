from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.json import JSONReader
from llama_index.core import Document

import os
from dotenv import load_dotenv
import json
load_dotenv()

from utils.constant import DATA_DIR_PATHS

class Parser():
  # Initialization
  def __init__(self, result_type: str = "markdown"): 
    # result_type = ["markdown", "text"]

    # Setup parser
    self.parser = LlamaParse(
        result_type=result_type,
        num_workers=4,
        max_timeout=5000
    )
    # Setup all the .pdf files as the files to be extracted
    self.pdf_file_extractor = {".pdf": self.parser}
    # Results container
    self.results = []


  # Parse documents
  def parse_document(self, filename: str) -> None:
    # Read all documents 
    filename = f"{filename}.pdf" if ".pdf" not in filename else filename
    filename = os.path.join(DATA_DIR_PATHS['pdf'], filename)
    print(f"[PARSER] Parsing pdf {filename}")
    document = SimpleDirectoryReader(input_files=[filename], file_extractor= self.pdf_file_extractor).load_data()

    # Store in a list of dictionary
    self.results.append({
      "filename" : os.path.basename(filename),
      "type": "pdf",
      "document": document
    })


  # Parse json
  def parse_json(self, filename: str, level: int = 1) -> None:
    filename = f"{filename}.json" if ".json" not in filename else filename
    filename = os.path.join(DATA_DIR_PATHS['json'], filename)
    print(f"[PARSER] Parsing json {filename}")
    
    # Load JSONReader
    reader = JSONReader()
    document = reader.load_data(input_file=filename)

    # Store in a list of dictionary
    self.results.append({
      "filename" : os.path.basename(filename),
      "type": "json",
      "document": document
    })


  # Store document
  def store_results(self) -> None:
    # Will be stored inside ./data/json
    for data_dict in self.results:
      store_filename = os.path.join(DATA_DIR_PATHS['md'], f"{data_dict['type']}_{data_dict['filename'].split('.')[0]}.md")
      with open(store_filename, "w", encoding="utf-8") as f:
        f.write(data_dict['text'])
        f.close()

      print(f"[STORE] Store result in {store_filename}")


  # Get parsed based on filename
  def get_result(self, filename):
    for data_dict in self.results:
      if (data_dict['filename'] == filename):
        return data_dict['text']
    return None
