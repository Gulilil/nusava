from agent.agent import Agent
import asyncio


async def test(nusava: Agent) -> None:
  # nusava.run() # To run on Flask

  # # Setup (IMPORTANT)
  user_id = 1
  # user_id = 3
  await nusava.set_user(user_id)


  # # Test process data
  # nusava.process_data_hotel()
  nusava.process_data_post()
  # nusava.process_data_association_rule()
  # nusava.process_data_tourist_attraction()
  await nusava.process_labelling_communities()


  # # Test action chat
  # print(await nusava.action_reply_chat("Hi There!", "nusava_test"))
  # print(await nusava.action_reply_chat("Give me general informations of Tanto hotel.", "nusava_test"))
  # print(await nusava.action_reply_chat("Give me your 5 recommended Hotels in Nusa Tenggara. Please list it down along the name of the hotels", "nusava_test"))
  # print(await nusava.action_reply_chat("Tell me the location of Tanto Hotel", "nusava_test"))
  # print(await nusava.action_reply_chat("Summarize me some reviews of Tanto Hotel. State the ratings and the description of some of the reviews too.", "nusava_test"))
  # print(await nusava.action_reply_chat("Tell me the check-in and check-out time of Siola Hotel", "nusava_test"))
  # print(await nusava.action_reply_chat("I would like to go to Nusa Tenggara in a near future. Can you recommend me any tourist attraction?", "nusava_test"))
  # print(await nusava.action_reply_chat("It seems La Boheme Bajo Hostel and Sahid T-MORE Kupang are some good hotels. Can you give recommendation of any other hotels like those two?", "nusava_test"))


  # # Test action post
  # caption_message = await nusava.action_generate_caption("Image of Kuta beach in Bali when sunset", ["beach", "holiday", "beautiful", "nature", "pretty", "sunkissed"], "Make it short and simple. Do not use hashtags.")
  # await nusava.action_schedule_post("", caption_message)
  # caption_message = await nusava.action_generate_caption("Images of destination places in Singapore consists of Universal Studio, Merlion, and Orchard Road", ["holiday", "fun", "friends", "urban travel", "city"])
  # await nusava.action_schedule_post("", caption_message)
  # caption_message = await nusava.action_generate_caption("Image of the Eiffel Tower during golden hour", ["Paris", "Eiffel", "romantic", "city", "travel", "light"], "Simple and charming. Avoid clichés.")
  # await nusava.action_schedule_post("", caption_message)
  # caption_message = await nusava.action_generate_caption("Image of a hot air balloon flying over Cappadocia's rocky landscape", ["Cappadocia", "balloon", "sunrise", "landscape", "unique", "explore"], "Use a light and magical tone.")
  # await nusava.action_schedule_post("", caption_message)
  # caption_message = await nusava.action_generate_caption("Image of tourists hiking to a viewpoint overlooking a Norwegian fjord", ["Norway", "fjord", "hike", "nature", "fresh", "breathtaking"], "Make it invigorating and scenic.")
  # await nusava.action_schedule_post("", caption_message)
  # caption_message = await nusava.action_generate_caption("Image of the Great Wall of China stretching across green hills", ["China", "GreatWall", "heritage", "travel", "epic", "history"], "Capture the scale and legacy.")
  # await nusava.action_schedule_post("", caption_message)
  # caption_message = await nusava.action_generate_caption("Image of Machu Picchu ruins with misty mountains in the background", ["Peru", "MachuPicchu", "history", "nature", "hiking", "awe"], "Make it reflective and respectful.")
  # await nusava.action_schedule_post("", caption_message)

  # # Test decision maker
  # await nusava.decide_action()





if __name__ == "__main__":
  nusava = Agent()
  asyncio.run(test(nusava))


