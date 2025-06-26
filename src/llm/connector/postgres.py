import os
import psycopg2
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
load_dotenv()


class PostgresConnector():
  """
  Connecting component to PostgreSQL: RDBMS for bot data
  """
  def __init__(self): 
    """
    Instantiate the database client
    """
    self.connection = psycopg2.connect(
          os.getenv("DB_PRODUCTION_URL")
          # host=os.getenv("POSTGRES_HOST"),      
          # port=os.getenv("POSTGRES_PORT"),           
          # database=os.getenv("POSTGRES_DB_NAME"),    
          # user=os.getenv("POSTGRES_USER"),     
          # password=os.getenv("POSTGRES_PASSWORD")  
      )
    self.cursor = self.connection.cursor()

  
  def get_username(self, user_id: str) -> tuple:
    """
    Get username based on the user_id
    """
    try:
      table_name = "bot_user"
      column_name = "username"
      self.cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE id={user_id}")
      data = self.cursor.fetchone()[0]
      return data
    except Exception as e:
      print(f"[ERROR POSTGRES] {e}")
      self.connection.rollback()
      return None 
  

  def get_persona_data(self, user_id: str) -> tuple:
    """
    Get persona data based on the user_id
    """
    try:
      table_name = "bot_user"
      column_name = "persona"
      self.cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE id={user_id}")
      data = self.cursor.fetchone()[0]
      return data
    except Exception as e:
      print(f"[ERROR POSTGRES] {e}")
      self.connection.rollback()
      return None 
  

  def get_config_data(self, user_id: str) -> tuple:
    """
    Get persona data based on the user_id
    Make sure to not change the order of the data returned
    """
    try:
      table_name = "bot_configuration"
      column_names = "temperature, top_k, max_token, max_iteration"
      self.cursor.execute(f"SELECT {column_names} FROM {table_name} WHERE user_id={user_id}")
      data = self.cursor.fetchone()
      return data
    except Exception as e:
      print(f"[ERROR POSTGRES] {e}")
      self.connection.rollback()
      return None 
  

  def get_scheduled_post_data(self, user_id: str) -> tuple:
      """
      Get scheduled post data that is ready to post:
      - scheduled_time is before current time (GMT+7)
      - is_posted is False
      """
      try:
          table_name = "bot_scheduledpost"
          column_names = "image_url, caption"

          # Get current time in GMT+7
          current_time_gmt7 = datetime.now(timezone.utc) + timedelta(hours=7)
          
          # Use parameterized query to prevent SQL injection
          query = f"""
              SELECT {column_names}
              FROM {table_name}
              WHERE user_id = %s
                AND scheduled_time < %s
                AND is_posted = FALSE
              LIMIT 1;
          """
          self.cursor.execute(query, (user_id, current_time_gmt7))
          data = self.cursor.fetchone()
          return data
      except Exception as e:
          print(f"[ERROR POSTGRES] {e}")
          self.connection.rollback()
          return None