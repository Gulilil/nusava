from agent.agent import Agent
import asyncio


async def process(nusava: Agent) -> None:

  # # Setup (IMPORTANT)
  user_id = 1
  await nusava.set_user(user_id)


if __name__ == "__main__":
  """
  This function is run manually. 
  It is used to migrate the data from MongoDB to Pinecone.
  This function will not be run on server's runtime.
  """
  nusava = Agent()
  asyncio.run(process(nusava))
