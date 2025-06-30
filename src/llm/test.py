from agent.agent import Agent
import asyncio


async def test(nusava: Agent) -> None:
  # nusava.run() # To run on Flask

  # # Setup (IMPORTANT)
  user_id = 1
  await nusava.set_user(user_id)


  # # Test action chat
  # # General
  # print(await nusava.action_reply_chat("Hi There!", "gulilii"))
  # print(await nusava.action_reply_chat("What is your favorite color?", "gulilii"))
  # print(await nusava.action_reply_chat("What do you do for a living?", "gulilii"))
  # # Tourism
  print(await nusava.action_reply_chat("Give me general informations of Tanto hotel.", "gulilii"))
  print(await nusava.action_reply_chat("Give me your 5 recommended Hotels in Nusa Tenggara. Please list it down along the name of the hotels", "gulilii"))
  print(await nusava.action_reply_chat("Tell me the exact location of Tanto Hotel", "gulilii"))
  # print(await nusava.action_reply_chat("Summarize me some reviews of Tanto Hotel. State the ratings and the description of some of the reviews too.", "gulilii"))
  # print(await nusava.action_reply_chat("Tell me the check-in and check-out time of Siola Hotel", "gulilii"))
  # print(await nusava.action_reply_chat("Based on Harbour Shuttle by Bajo Taxi tourist attractions. Give me some of your recommended hotels.", "gulilii"))
  # # Other
  # print(await nusava.action_reply_chat("Can you explain me more about the differences between JavaScript and Python?", "gulilii"))
  # print(await nusava.action_reply_chat("Provide me a recipe details to make Nasi Goreng", "gulilii"))


  # # Tourist attraction  
  # print(await nusava.action_reply_chat("I would like to go to Nusa Tenggara in a near future. Can you recommend me any tourist attraction?", "gulilii"))
  # # Association rule
  # print(await nusava.action_reply_chat("It seems La Boheme Bajo Hostel and Sahid T-MORE Kupang are some good hotels. Can you give recommendation of any other hotels like those two?", "gulilii"))


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


  # Test decision maker, include like, follow, post
  # await nusava.decide_action()



if __name__ == "__main__":
  nusava = Agent()
  asyncio.run(test(nusava))


