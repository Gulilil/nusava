import os

DATA_DIR_PATH = os.path.join(os.getcwd(), "llm", "data")
DATA_DIR_PATHS = {
  "md" : os.path.join(DATA_DIR_PATH, "md"),
  "pdf" : os.path.join(DATA_DIR_PATH, "pdf"),
  "json" : os.path.join(DATA_DIR_PATH, "json")
}