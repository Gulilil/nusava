from agent.agent import Agent
import asyncio


async def test(nusava: Agent) -> None:
  # nusava.run() # To run on Flask

  # # Setup (IMPORTANT)
  user_id = 1
  # user_id = 2
  await nusava.set_user(user_id)


  # # Test process data
  # nusava.process_data_hotel()


  # # Test action chat
  # print(await nusava.action_reply_chat("Give me general informations of Tanto hotel.", "nusava_test"))
  # print(await nusava.action_reply_chat("Give me your 5 recommended Hotels in Nusa Tenggara. Please list it down along the name of the hotels", "nusava_test"))
  # print(await nusava.action_reply_chat("Tell me the location of Tanto Hotel", "nusava_test"))
  # print(await nusava.action_reply_chat("Summarize me some reviews of Tanto Hotel. State the ratings and the description of some of the reviews too.", "nusava_test"))
  # print(await nusava.action_reply_chat("Tell me the check-in and check-out time of Siola Hotel", "nusava_test"))


  # # Test action post
  # print(await nusava.action_generate_caption("Image of Kuta beach in Bali when sunset", ["beach", "holiday", "beautiful", "nature", "pretty", "sunkissed"], "Make it short and simple. Do not use hashtags."))
  # print(await nusava.action_generate_caption("Image of Kuta beach in Bali when sunset", ["beach", "holiday", "beautiful", "nature", "pretty", "sunkissed"], "Make it short and simple. Do not use hashtags."))
  # print(await nusava.action_generate_caption("Images of destination places in Singapore consists of Universal Studio, Merlion, and Orchard Road", ["holiday", "fun", "friends", "urban travel", "city"]))
  

  # # Test decision maker
  # for i in range(3):
  #   nusava.decide_action()



if __name__ == "__main__":
  nusava = Agent()
  asyncio.run(test(nusava))


