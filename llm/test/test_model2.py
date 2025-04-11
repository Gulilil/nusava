from llm.src.model.model import Model
import os
from utils.constant import DATA_DIR_PATHS

if __name__ == "__main__":
  document_name = "pdf_Laporan-TA-Capstone-13521116.md"
  document_description = "Thesis about developing Social Media Bots agent using LLM and Data Mining to imitate influencer's behavior"
  with open(os.path.join(DATA_DIR_PATHS['md'], document_name), "r", encoding="utf-8") as f:
    document_text = f.read()

  context = "The primary role of this agent is to answer prompt from user with relevant answer regarding the documents. The answer can be in english."

  model = Model()
  model.learn(document_text, document_name, document_description)
  model.config(context)

  while True:
    prompt = input("Insert a prompt (q to quit): ")

    if (prompt == "q"):
      break
    else:
      result = model.answer(prompt)
      print(result)


  