from agent.agent import Agent
import asyncio


async def test(nusava: Agent) -> None:
  # nusava.run() # To run on Flask

  # # Setup (IMPORTANT)
  user_id = 1
  # user_id = 3
  await nusava.set_user(user_id)


  # # Test action chat
  # # General
  # print(await nusava.action_reply_chat("Hi There!", "Gulilii"))
  # # Hotels
  # print(await nusava.action_reply_chat("Give me general informations of Tanto hotel.", "Gulilii"))
  # print(await nusava.action_reply_chat("Give me your 5 recommended Hotels in Nusa Tenggara. Please list it down along the name of the hotels", "Gulilii"))
  # print(await nusava.action_reply_chat("Tell me the exact location of Tanto Hotel", "Gulilii"))
  # print(await nusava.action_reply_chat("Summarize me some reviews of Tanto Hotel. State the ratings and the description of some of the reviews too.", "Gulilii"))
  # print(await nusava.action_reply_chat("Tell me the check-in and check-out time of Siola Hotel", "Gulilii"))
  # print(await nusava.action_reply_chat("Based on Harbour Shuttle by Bajo Taxi tourist attractions. Give me some of your recommended hotels.", "Gulilii"))

  # # Tourist attraction  
  # print(await nusava.action_reply_chat("I would like to go to Nusa Tenggara in a near future. Can you recommend me any tourist attraction?", "Gulilii"))
  # # Association rule
  # print(await nusava.action_reply_chat("It seems La Boheme Bajo Hostel and Sahid T-MORE Kupang are some good hotels. Can you give recommendation of any other hotels like those two?", "Gulilii"))


  # # Test action post
  # caption_message = await nusava.action_generate_caption("Image of Kuta beach in Bali when sunset", ["beach", "holiday", "beautiful", "nature", "pretty", "sunkissed"], "Make it short and simple. Do not use hashtags.")
  # await nusava.action_schedule_post("https://www.balimagictour.com/wp-content/uploads/kuta-beach.jpg", caption_message)
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


  # Test choose community
  # await nusava.choose_community()


  # Test decision maker, include like, follow, post
  # await nusava.decide_action()



if __name__ == "__main__":
  nusava = Agent()
  asyncio.run(test(nusava))


