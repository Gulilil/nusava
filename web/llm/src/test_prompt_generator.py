from prompt_generator.prompt_generator import PromptGenerator

if __name__ == "__main__":
  pg = PromptGenerator()
  # prompt = pg.generate_prompt_decide_action(None, None)
  # print(prompt)
  prompt = pg.generate_prompt_comment("Some sort of caption", "Make an engaging and supportive comment", None)
  print(prompt)
  # prompt = pg.generate_prompt_post_caption(["cheap", "recommended", "relaxing"], "No.1 Hotel in Nusa Tenggara Timur with the best price", None)
  # print(prompt)
