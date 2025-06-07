import requests
import os
from dotenv import load_dotenv
load_dotenv()

class OutputGateway():
  """
  Output gateway to other module
  """
  def __init__(self):
    """
    Instantiate output gateway to call the API of other module
    """
    # TODO To be adjusted
    self.base_url = os.getenv("AUTOMATION_MODULE_URL")
    self.headers = {
      'Content-Type' : 'application/json'
    }


  def request_statistics(self, user_id: str):
    """
    Hit statistics api in automation module
    """
    path = "/statistics"
    url = f"{self.base_url}{path}"
    # TODO 

    return


  def request_follow(self, user_id: str):
    """
    Hit follow api in automation module
    """
    path = "/follow"
    url = f"{self.base_url}{path}"
    # TODO 

    return
  
  
  def request_like(self, post_id: str):
    """
    Hit like api in automation module
    """
    path = "/like"
    url = f"{self.base_url}{path}"
    # TODO 

    return
  

  def request_comment(self, post_id: str, comment_message:str):
    """
    Hit comment api in automation module
    """
    path = "/comment"
    url = f"{self.base_url}{path}"
    # TODO 

    return
  

  def request_post(self, img_url: str, caption_message:str):
    """
    Hit comment api in automation module
    """
    path = "/post"
    url = f"{self.base_url}{path}"
    # TODO 
    
    return