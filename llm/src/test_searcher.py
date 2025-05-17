from searcher.searcher import Searcher

if __name__ == "__main__":
  searcher = Searcher()
  
  mongo_client = searcher.mongo_client
  db = mongo_client['data-mining']
  collection = db["hotel"]
  
  for doc in collection.find():
    print(doc)
