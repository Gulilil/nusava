from flask import Flask, request, jsonify
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()


class InputGateway():
  """
  Input gateway for other module
  """
  def __init__(self, 
               agent_component, 
               host : str = os.getenv("LLM_MODULE_HOST"), 
               port : str = os.getenv("LLM_MODULE_PORT")):
    """
    Instantiate Flask as the framework for the API and the gateway
    """
    self.app = Flask(__name__)
    self._agent_component = agent_component
    self.host = host
    self.port = port
    self.setup_routes()
    

  def _check_data_validity(self, 
                           data: dict, 
                           fields_to_check : list) -> bool:
    """
    Check validity of the data, making sure that the data and the fields inside the data are not empty
    """
    if (data is None):
      return False, "Data is not found!"
    for field in fields_to_check:
      if (field not in data):
        return False, f"Missing {field} field!"
    return True, ""

  ######## SETUP INPUT ########
  
  def setup_routes(self) -> None:
    """
    Setup routing for the API
    Is used for input from other module (External-trigger Action)
    
    Returning format:
    {
      response : str
    }
    """

    @self.app.route("/user", methods=['POST'])
    async def set_user():
      """
      Set user_id to the agent
      Field format : 
      {
        user_id : str
      }
      """
      try:
        data = request.get_json()
        is_valid, error_message = self._check_data_validity(data, ['user_id'])
        if (not is_valid):
          return jsonify({"error": error_message}), 400
        
        # Proceed to process
        user_id = data['user_id']
        await self._agent_component.set_user(user_id)
        return jsonify({"response": True}), 200
      except Exception as error: 
        return jsonify({"error": str(error)}), 400

    @self.app.route("/persona", methods=['POST'])
    def set_persona():
      """
      Respond to change persona input from dashboard
      """
      try:
        self._agent_component.set_persona()
        return jsonify({"response": True}), 200
      except Exception as error: 
        return jsonify({"error": str(error)}), 400

    @self.app.route("/config", methods=['POST'])
    def set_config():
      """
      Respond to change model configuration input from dashboard
      """
      try:
        self._agent_component.set_config()
        return jsonify({"response": True}), 200
      except Exception as error: 
        return jsonify({"error": str(error)}), 400
      
    ######## ACTIONS INPUT ########

    @self.app.route("/chat", methods=['POST'])
    async def respond_chat():
      """
      Respond to input chat from user, returning the reply to the inputted message
      Field format : 
      {
        chat_message : str,
        sender_id: str
      }
      """
      try:
        data = request.get_json()
        is_valid, error_message = self._check_data_validity(data, ['chat_message', 'sender_id'])
        if (not is_valid):
          return jsonify({"error": error_message}), 400

        # Proceed to process
        chat_message = data['chat_message']
        sender_id = data['sender_id']
        response = await self._agent_component.action_reply_chat(chat_message, sender_id)
        return jsonify({"response": response}), 200
      except Exception as error: 
        return jsonify({"error": str(error)}), 400
      
    @self.app.route("/post", methods=['POST'])
    async def respond_schedule_post():
      """
      Respond to schedule post input from dashboard, will be scheduled
      Field format : 
      {
        image_url: str, 
        caption_message: str, 
      }
      """
      try:
        data = request.get_json()
        is_valid, error_message = self._check_data_validity(data, ["image_url", "caption_message"])
        if (not is_valid):
          return jsonify({"error": error_message}), 400
        
        # Proceed to process
        img_url = data['image_url']
        caption_message= data['caption_message']
        # Process and schedule the post
        schedule_time, reason = await self._agent_component.action_schedule_post(img_url, caption_message)

        return jsonify({"scheduled_time": schedule_time, "reason": reason}), 200
      except Exception as error: 
        return jsonify({"error": str(error)}), 400

    @self.app.route("/caption", methods=['POST'])
    async def respond_generate_caption():
      """
      Respond to post input from dashboard, returning the caption for the post
      Field format : 
      {
        image_description: str, 
        caption_keywords : list[str],
        additional_context: str (optional)
      }
      """
      try:
        data = request.get_json()
        is_valid, error_message = self._check_data_validity(data, ["image_description", "caption_keywords"])
        if (not is_valid):
          return jsonify({"error": error_message}), 400
        
        # Proceed to process
        img_description = data['image_description']
        caption_keywords = data['caption_keywords']
        additional_context = data.get('additional_context', None)
        # Process and schedule the action post
        caption_message = await self._agent_component.action_generate_caption(img_description, caption_keywords, additional_context)

        return jsonify({"response": caption_message}), 200
      except Exception as error: 
        return jsonify({"error": str(error)}), 400
    

  def run(self) -> None:
    """
    Run the system in specific ip and port 
    """
    self.app.run(host=self.host, port=self.port)

  