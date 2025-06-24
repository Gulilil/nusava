from agent.agent import Agent
from gateway.input import InputGateway

nusava = Agent()
gateway = InputGateway(agent_component=nusava)
app = gateway.app  # <- gunicorn needs this `app` object