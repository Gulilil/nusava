from agent.agent import Agent
import os
from utils.constant import DATA_DIR_PATHS

if __name__ == "__main__":
  nusava = Agent()

  document_name = "json_transstudio.md"
  document_description = "Data details of Trans Studio Mini Kupang"
  with open(os.path.join(DATA_DIR_PATHS['md'], document_name), "r", encoding="utf-8") as f:
    document_text = f.read()

  context = "The primary role of this agent is to answer prompt from user with relevant answer regarding the documents. The answer can be in english."

  model_component = nusava.model_component
  model_component.learn(document_text, document_name, document_description)
  model_component.config(context)

  prompt_generator_component = nusava.prompt_generator_component
  while True:
    user_input = input("Insert an input (q to quit): ")
    prompt = prompt_generator_component.generate_prompt_reply_chat(user_input)
    print(prompt)

    if (prompt == "q"):
      break
    else:
      result = model_component.answer(prompt)
      print(result)


  
  