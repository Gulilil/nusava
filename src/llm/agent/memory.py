from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

class Memory():
  """
  Provides memory related to past experiences and interactions of the model with users
  The usage itself is closely related to Episodic Memory
  """

  # Max short term memory length that can be held 
  _max_message_limit : int = 16
  # Length of "short term memory" to be migrated
  _memory_length_migration: int = 10

  def __init__(
      self,
      agent_component: object
  ) -> None:
      """
      Use dictionary as memory store 
      """
      self._agent_component = agent_component
      self._memory= {}

  ######## STORE  ########

  def count(self) -> int:
      """
      Returns the number of values in memory.
      """
      return len(self._memory)


  def display_memory_all(self) -> None:
      """
      Display all the stored memory
      """
      idx = 1
      print("[DISPLAY MEMORY]:")
      for sender_id, memory_list in self._memory.items():
          print(f"{idx} {sender_id}:")
          for memory in memory_list:
             print(f"\t {memory}")
          idx += 1


  def display_memory_count(self) -> None:
      """
      Display the count of all the memory
      """
      idx = 1
      print("[DISPLAY MEMORY COUNT]:")
      for sender_id, memory_list in self._memory.items():
          print(f"{idx} {sender_id}:  {len(memory_list)} memory")
          idx += 1


  ######## STORE  ########

  async def store(self, sender_id: str, memory_data: dict) -> None:
      """
      Stores a value in memory.

      Bot data format: 
      { "role": "bot", 
        "content": "..."}

      Sender data format:
      { "role" : "user",
        "content" : "...."}

      """
      # Store as short term memory
      current_time = datetime.now(ZoneInfo("Asia/Jakarta"))
      memory_data["timestamp"] = current_time
      # Create a list if it is a new sender_id
      if (sender_id not in self._memory):
         self._memory[sender_id] = []
      self._memory[sender_id].append(memory_data)
      print(f"[STORING MEMORY] Successfully storing chat memory with {sender_id} as short-term memory")
      
      # Migrating memory if it reaches certain length
      if (len(self._memory[sender_id]) >= self._max_message_limit):
        memory_to_migrate = self._memory[sender_id][:self._memory_length_migration]
        success = await self._agent_component.summarize_and_store_memory(sender_id, memory_to_migrate)
        print(f"[MIGRATING MEMORY] Successfully migrating short-term memory with {sender_id} as long-term memory")
        # If already stored in vector, remove from short term memory
        if (success):
           self.delete(sender_id, self._memory_length_migration, is_all= False)

  
  ######## RETRIEVE ########

  def retrieve(self, sender_id: str) -> list:
      """
      Return the chat memory with certain sender
      """
      if (sender_id in self._memory):
        return self._memory[sender_id]
      else:
        return []
      

  def retrieve_all(self) -> dict:
     """
     Return all the memory
     """
     return self._memory
  

  ######## RETRIEVE ########

  def delete(self, sender_id: str, n_late: int, is_all: bool = False):
    """
    Delete memory of certain sender_id and truncate n_late memories (or all)
    """
    if (sender_id in self._memory):
      if (is_all):
        self._memory.pop(sender_id)
      else:
        # Truncate the n_late memory
        self._memory[sender_id] = self._memory[sender_id][n_late:]

    else:
      print(f"[ERROR DELETING MEMORY] No sender_id \"{sender_id}\" is found")

  def delete_all(self):
     """
     Delete all short term memory
     """
     self._memory = {}
    


"""
Example of Memory (FOR TESTING ONLY)
[ 
  {'role': 'user', 'content': 'Give me general informations of Tanto hotel.', 'timestamp': datetime(2025, 6, 12, 18, 47, 30, 669266)}, 
  {'role': 'bot', 'content': "The Tanto Hotel seems like a great choice for travelers! It's located in a strategic area, making it easy to explore various destinations. They offer a range of facilities, including meeting rooms and 24-hour reception services, which is super convenient. Plus, they have a restaurant on site serving delicious meals and complimentary Wi-Fi throughout the public areas. And as an added bonus, their location near Bandar Udara Umbu Mehang Kunda (WGP) airport makes it an ideal choice for travelers waiting for their next flight. Overall, I'd say Tanto Hotel is a great option for anyone looking for a comfortable and memorable stay!", 'timestamp': datetime(2025, 6, 12, 18, 48, 49, 398705)}, 
  {'role': 'user', 'content': 'Give me your 5 recommended Hotels in Nusa Tenggara. Please list it down along the name of the hotels', 'timestamp': datetime(2025, 6, 12, 18, 48, 49, 399705)}, 
  {'role': 'bot', 'content': "As an Eco-Tourism Influencer & Travel Filmmaker, I'm happy to recommend these 5 hotels in Nusa Tenggara:\n\n1. **NIHI Sumba** - member Leading Hotels of the World (5.0/5)\n2. **Triple 8 Suites** (4.7/5) \n3. **Bajo Nature Backpackers** (5.0/5)\n4. **Unicorn Hotel** (highly rated, but exact rating not available)\n5. **Victory Hotel Ruteng** (highly rated, but exact rating not available)\n\nThese hotels have received excellent reviews from travelers and offer a range of amenities and services to make your stay comfortable and enjoyable. I hope this helps you plan your trip to Nusa Tenggara!", 'timestamp': datetime(2025, 6, 12, 18, 50, 58, 794981)}, 
  {'role': 'user', 'content': 'Tell me the location of Tanto Hotel', 'timestamp': datetime(2025, 6, 12, 18, 50, 58, 795984)}, 
  {'role': 'bot', 'content': 'The Tanto Hotel is located at Jalan Prof. Dr. W. Z. Yohanes No. 14, Prailiu, Kambera, Waingapu, Sumba Timur.', 'timestamp': datetime(2025, 6, 12, 18, 51, 50, 570072)},
  {'role': 'user', 'content': 'Summarize me some reviews of Tanto Hotel. State the ratings and the description of some of the reviews too.', 'timestamp': datetime(2025, 6, 12, 18, 51, 50, 571041)}, 
  {'role': 'bot', 'content': "The Tanto Hotel has received mixed reviews from guests, with some praising its friendly staff, comfortable rooms, and good service, while others have complained about uncleanliness, unfriendly staff, and poor service. Some reviewers mentioned minor issues such as a non-functional phone in the room. It's worth noting that this summary only includes some of the available reviews and might not reflect the full range of opinions on Tanto Hotel.", 'timestamp': datetime(2025, 6, 12, 18, 55, 38, 272939)}
]
"""