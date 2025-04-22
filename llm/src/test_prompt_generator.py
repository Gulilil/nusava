from prompt_generator.prompt_generator import PromptGenerator

if __name__ == "__main__":
  pg = PromptGenerator()
  prompt = pg.generate_prompt_decide_action("post", "post a picture of a cat")
  print(prompt)
