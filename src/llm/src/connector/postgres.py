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
  

  def get_persona_data(self, user_id: str) -> tuple:
    """
    Get persona data based on the user_id
    """
    table_name = "bot_user"
    column_name = "persona"
    self.cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE id=\'{user_id}\'")
    data = self.cursor.fetchone()[0]
    return data
  

  def get_config_data(self, user_id: str) -> tuple:
    """
    Get persona data based on the user_id
    Make sure to not change the order of the data returned
    """
    # TODO To be adjusted
    table_name = "bot_configuration"
    column_names = "temperature, top_k, max_token, max_iteration"
    self.cursor.execute(f"SELECT {column_names} FROM {table_name} WHERE user_id=\'{user_id}\'")
    data = self.cursor.fetchone()
    return data