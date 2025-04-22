import os

DATA_DIR_PATH = os.path.join(os.getcwd(), "llm", "data")
DATA_DIR_PATHS = {
  "md" : os.path.join(DATA_DIR_PATH, "md"),
  "pdf" : os.path.join(DATA_DIR_PATH, "pdf"),
  "json" : os.path.join(DATA_DIR_PATH, "json")
}

ACTIONS_LIST = [
  {
    "action": "follow",
    "description": "Follow another Instagram account."
  }, 
  {
    "action": "like",
    "description": "Like a post in Instagram."
  },
  {
    "action": "comment",
    "description": "Leave a comment in a post in Instagram."
  },
  {
    "action": "post",
    "description": "Upload a post in Instagram."
  },
  {
    "action": "reply chat",
    "description": "Reply a message in direct message chat room."
  },
  {
    "action": "reply comment",
    "description": "Reply a comment in a post in Instagram."
  },
  {
    "action": "none",
    "description": "Not to do any action"
  }
]