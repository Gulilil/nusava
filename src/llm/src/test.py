from agent.agent import Agent

if __name__ == "__main__":
  nusava = Agent()
  # nusava.run() # To run on Flask

  nusava.set_user("luca_bennett")
  # nusava.set_user("isabella_rivera")

  # nusava.process_data_hotel()

  # # Test action chat
  answer = nusava.action_reply_chat("Give me general informations and facilities of Tanto hotel.")
  # answer = nusava.action_reply_chat("Give me your 5 recommended Hotels and their locations.")
  # answer = nusava.action_reply_chat("Tell me the location of Tanto Hotel")
  # answer = nusava.action_reply_chat("Summarize me some reveiews of Tanto Hotel")
  print(answer)

  # # Test decision maker
  # for i in range(3):
  #   nusava.decide_action()

