from typing import Tuple
from utils.function import json_to_string_list


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

  def get_persona(self) -> None:
    """
    Return persona data
    """
    return self._persona

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
    persona_summary = f"[PERSONA SUMMARY] Current persona is: {self._persona['age']} years old with the occupation of {self._persona['occupation']} and the characterstics to be {self._persona['style']}"
    if ('name' in self._persona):
      persona_summary += f" The name is {self._persona['name']}."
    print(persona_summary)


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
  

  def get_persona_str(self):
    """
    Call persona data as string
    """
    persona_str_list = []
    json_to_string_list(self._persona, "persona", persona_str_list)
    persona_str = "\n".join(persona_str_list)
    return persona_str
