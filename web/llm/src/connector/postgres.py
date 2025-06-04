import os
import psycopg2

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
          host=os.getenv("POSTGRES_HOST"),      
          port=os.getenv("POSTGRES_PORT"),           
          database=os.getenv("POSTGRES_DB_NAME"),    
          user=os.getenv("POSTGRES_USER"),     
          password=os.getenv("POSTGRES_PASSWORD")  
      )
    self.cursor = self.connection.cursor()
  

  def get_persona_data(self, user_id: str):
    """
    Get persona data based on the user_id
    """
    # TODO To be adjusted
    table_name = "persona"
    self.cursor.execute(f"SELECT persona_data FROM {table_name} WHERE user_id=\'{user_id}\'")
    data = self.cursor.fetchone()[0]
    return data
  

  def get_config_data(self, user_id: str):
    """
    Get persona data based on the user_id
    """
    # TODO To be adjusted
    table_name = "config"
    self.cursor.execute(f"SELECT temperature, top_k, max_token, max_iteration FROM {table_name} WHERE user_id=\'{user_id}\'")
    data = self.cursor.fetchone()
    return data