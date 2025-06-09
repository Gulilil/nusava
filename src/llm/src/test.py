from agent.agent import Agent

if __name__ == "__main__":
  nusava = Agent()
  # nusava.run() # To run on Flask

  user_id = 1
  nusava.set_user(user_id)
  # nusava.set_user("isabella_rivera")

  # nusava.process_data_hotel()

  # # Test action chat
  # answer = nusava.action_reply_chat("Give me general informations  of Tanto hotel.")
  # answer = nusava.action_reply_chat("Give me your 5 recommended Hotels")
  # answer = nusava.action_reply_chat("Tell me the location of Tanto Hotel")
  # answer = nusava.action_reply_chat("Summarize me some reveiews of Tanto Hotel")

  # # Test action post
  # answer = nusava.action_generate_caption("Image of Kuta beach in Bali when sunset", ["beach", "holiday", "beautiful", "nature", "pretty", "sunkissed"], "Make it short and simple. Do not use hashtags.")
  answer = nusava.action_generate_caption("Images of destination places in Singapore consists of Universal Studio, Merlion, and Orchard Road", ["holiday", "fun", "friends", "urban travel", "city"], "Make it short and simple. Do not use hashtags.")  


  # # Test decision maker
  # for i in range(3):
  #   nusava.decide_action()

