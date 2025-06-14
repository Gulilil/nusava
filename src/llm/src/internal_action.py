from agent.agent import Agent
import asyncio
import sys
from instagrapi import Client
import json


async def internal_action(nusava: Agent, user_id: int) -> None:
    # Setup LLM
    user_id = user_id
    await nusava.set_user(user_id)
    await nusava.decide_action()


if __name__ == "__main__":
  """
  How to run:
    python internal_action.py <user_id>
  """

  try:
    # Read arguments
    args = sys.argv
    assert len(args) == 2, "[INVALID] Invalid amount of parameters"

    # Get User id
    user_id = args[1]

    # Initialize
    nusava = Agent()
    asyncio.run(internal_action(nusava, user_id))
  
  except Exception as e:
    print(f"[FAILED] Fail to run internal action: {e}")
