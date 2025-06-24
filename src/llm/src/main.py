from agent.agent import Agent

nusava = Agent()
app = nusava.input_gateway_component.app

if __name__ == "__main__":
  nusava.run() # To run on Flask
