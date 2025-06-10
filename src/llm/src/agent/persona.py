from typing import Tuple

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

  def _check_persona_data_validity(self, persona_data: dict) -> bool:
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

  def display_persona(self) -> None:
    """
    Display all persona data
    """
    for key, val in self._persona.items():
      print(f"{key} : {val}")

  def _display_persona_summary(self) -> None:
    """
    Display summary of persona data
    """
    print(f"[PERSONA SUMMARY] Current persona is: {self._persona['age']} years old with the occupation of {self._persona['occupation']} and the characterstics to be {self._persona['style']}" 
          + f" The name is {self._persona['name']}." if 'name' in self._persona else "")

  def load_persona(self, persona_data: dict) -> None:
    """
    Load persona data from a json
    """
    assert self._check_persona_data_validity(persona_data), "[FAILED] Persona data is not valid"
    self._persona = persona_data
    self._display_persona_summary()


  def get_typing_style(self) -> Tuple[str, str, str]:
    """
    Get typing style of the persona
    """
    return self._persona['age'], self._persona['style'], self._persona['occupation']