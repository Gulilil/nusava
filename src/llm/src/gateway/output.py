import requests
import os
from dotenv import load_dotenv
load_dotenv()

class OutputGateway():
  """
  Output gateway to other module
  """
  def __init__(self, agent):
    """
    Instantiate output gateway to call the API of other module
    """
    # TODO To be adjusted
    self._agent_component = agent
    self.base_url = os.getenv("AUTOMATION_MODULE_URL")
    self.headers = {
      'Content-Type' : 'application/json'
    }


  def request_follow(self, username: str) -> bool:
    """
    Hit follow api in automation module
    """
    try:
      path = "/api/follow/"
      url = f"{self.base_url}{path}"
      data = {
          "target_username": username,
          "user_id": self._agent_component.user_id
      }

      # Check response
      response = requests.post(url, json=data)
      if (response.status_code == 200):
        return True
      else:
        response_json = response.json()
        print(f"[ERROR REQUEST FOLLOW] Status code: {response.status_code}. Error : {response_json['error']}")
        return False

    except Exception as e:
      print(f"[ERROR REQUEST FOLLOW] Error occured in requesting action `follow` to {username}: {e}")
      return False
  
  
  def request_like(self, post_id: str) -> bool:
    """
    Hit like api in automation module
    """
    try:
      path = "/api/like/"
      url = f"{self.base_url}{path}"
      data = {
          "media_id": post_id,
          "user_id": self._agent_component.user_id
      }

      # Check response
      response = requests.post(url, json=data)
      if (response.status_code == 200):
        return True
      else:
        response_json = response.json()
        print(f"[ERROR REQUEST LIKE] Status code: {response.status_code}. Error : {response_json['error']}")
        return False

    except Exception as e:
      print(f"[ERROR REQUEST LIKE] Error occured in requesting action `like` to {post_id}: {e}")
      return False
  

  def request_comment(self, post_id: str, comment_message:str) -> bool:
    """
    Hit comment api in automation module
    """
    try:
      path = "/api/comment/"
      url = f"{self.base_url}{path}"
      data = {
          "media_id": post_id,
          "comment": comment_message,
          "user_id": self._agent_component.user_id
      }

      # Check response
      response = requests.post(url, json=data)
      if (response.status_code == 200):
        return True
      else:
        response_json = response.json()
        print(f"[ERROR REQUEST COMMENT] Status code: {response.status_code}. Error : {response_json['error']}")
        return False

    except Exception as e:
      print(f"[ERROR REQUEST COMMENT] Error occured in requesting action `comment` to {post_id}: {e}")
      return False
  

  def request_post(self, img_url: str, caption_message:str) -> None:
    """
    Hit comment api in automation module
    """
    # TODO 

    try:
      path = "/api/post/"
      url = f"{self.base_url}{path}"
      data = {
          "image_path": img_url,
          "caption": caption_message,
          "user_id": self._agent_component.user_id
      }

      # Check response
      response = requests.post(url, json=data)
      if (response.status_code == 200):
        return True
      else:
        response_json = response.json()
        print(f"[ERROR REQUEST POST] Status code: {response.status_code}. Error : {response_json['error']}")
        return False

    except Exception as e:
      print(f"[ERROR REQUEST POST] Error occured in requesting action `post`: {e}")
      return False