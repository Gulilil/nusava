

class Persona():
  """
  This class contains the data on how the model represent itself to the user (persona)
  """

  IMPORTANT_FIELDS = ["age", "style", "occupation"]

  def __init__(self):
    """
    Instantiate persona
    """
    self._persona = None

  ######## PRIVATE ########

  def _check_persona_data_validity(self, persona_data: dict):
    """
    Check if all important fields exist in the data
    """
    try:
      for field in self.IMPORTANT_FIELDS:
        if (field not in persona_data or persona_data[field] is None or persona_data[field] == ""):
          return False
      return True
    except:
      return False

  ######## PUBLIC ########

  def display_persona(self):
    """
    Display persona data
    """
    for key, val in self._persona.items():
      print(f"{key} : {val}")

  def load_persona(self, persona_data: dict):
    """
    Load persona data from a json
    """
    assert self._check_persona_data_validity(persona_data), "[FAILED] Persona data is not valid"
    self._persona = persona_data


  def reset_persona(self):
    """
    Reset persona data
    """
    self._persona = None


  def get_typing_style(self):
    """
    Get typing style of the persona
    """
    return self._persona['age'], self._persona['style'], self._persona['occupation']