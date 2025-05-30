from flask import Flask, request, jsonify

class InputGateway():

  def __init__(self, agent):
    """
    Instantiate Flask as the framework for the API and the gateway
    """
    self.app = Flask(__name__)
    self.agent = agent
    self.setup_routes()
    

  def _check_data_validity(self, data: dict, fields_to_check : list) -> bool:
    """
    Check validity of the data, making sure that the data and the fields inside the data are not empty
    """
    if (data is None):
      return False, "Data is not found!"
    for field in fields_to_check:
      if (field not in data):
        return False, f"Missing {field} field!"
    return True, ""

  
  def setup_routes(self):
    """
    Setup routing for the API
    Is used for input from other module (External-trigger Action)
    
    Returning format:
    {
      answer : str
    }
    """

    @self.app.route("/chat", methods=['POST'])
    def respond_chat():
      """
      Respond to input chat from user, returning the reply to the inputted message
      Field format : 
      {
        user_id : str,
        chat_message : str
      }
      """
      data = request.get_json()
      is_valid, error_message = self._check_data_validity(data, ['user_id', 'chat_message'])
      if (not is_valid):
        return jsonify({"error": error_message}), 400

      # Proceed to process
      user_id = data['user_id']
      chat_message = data['chat_message']
      answer = self.agent.action_reply_chat(user_id, chat_message)
      return jsonify({"answer": answer})

    @self.app.route("/comment", methods=['POST'])
    def respond_comment():
      """
      Respond to input comment from user, returning the reply to the comment
      Field format : 
      {
        comment_message : str,
        post_caption: str, 
        previous_comments : list[str]
      }
      """
      data = request.get_json()
      is_valid, error_message = self._check_data_validity(data, ["comment_message", "post_caption", "previous_comments"])
      if (not is_valid):
        return jsonify({"error": error_message}), 400
      
      # Proceed to process
      comment_message = data['comment_message']
      post_caption = data['post_caption']
      previous_comments = data['previous_comments']
      answer = self.agent.action_reply_comment(comment_message, post_caption, previous_comments)
      return jsonify({"answer": answer})


    @self.app.route("/post", methods=['POST'])
    def respond_post():
      """
      Respond to post input from dashboard, will be scheduled
      Field format : 
      {
        image_url : str,
        caption_text : str,
        caption_keywords : list[str]
      }
      """
      data = request.get_json()
      is_valid, error_message = self._check_data_validity(data, ["image_url", "caption_text", "caption_keywords"])
      if (not is_valid):
        return jsonify({"error": error_message}), 400
      
      # Proceed to process
      img_url = data['img_url']
      caption_text = data['caption_text']
      caption_keywords = data['caption_keywords']
      answer = self.agent.action_post(img_url, caption_text, caption_keywords)
      return jsonify({"answer": answer})

  def run(self, host : str = "0.0.0.0", port: int = 7000):
    """
    Run the system in specific ip and port 
    """
    self.app.run(host=host, port=port)

  