from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

import os
from dotenv import load_dotenv
load_dotenv()

from constant.constant import PDF_DATA_DIR_PATH, MD_DATA_DIR_PATH

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
    self.file_extractor = {".pdf": self.parser}

  # Parse documents
  def parse_documents(self, keyword: str = ""):
    # List documents
    files_path = [os.path.join(PDF_DATA_DIR_PATH, filename) for filename in os.listdir(PDF_DATA_DIR_PATH) if keyword in filename]
    # Read all documents 
    self.results = []
    for file in (files_path):
      print(f"[PARSER] Parsing {file}")
      documents = SimpleDirectoryReader(input_files=[file], file_extractor= self.file_extractor).load_data()
      document_text_list = []
      # Make document text into a long string
      for document in documents:
        document_text_list.append(document.text)
      # Store in a list of dictionary
      self.results.append({
        "filename" : os.path.basename(file),
        "text": "\n\n".join(document_text_list)
      })

  # Store document
  def store_results(self):
    # Will be stored inside ./data/json
    for data_dict in self.results:
      store_filename = os.path.join(MD_DATA_DIR_PATH, data_dict['filename'].replace(".pdf", ".md"))
      with open(store_filename, "w", encoding="utf-8") as f:
        f.write(data_dict['text'])
        f.close()

      print(f"[STORE] Store result in {store_filename}")
