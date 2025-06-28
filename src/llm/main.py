from agent.agent import Agent
import asyncio

nusava = Agent()
app = nusava.input_gateway_component.app
if __name__ == "__main__":
  asyncio.run(nusava.run())   # To run on Flask
