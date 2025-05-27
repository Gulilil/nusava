from llm.src.database_connector.database_connector import DatabaseConnector
from model.model import Model

if __name__ == "__main__":
  db_connector = DatabaseConnector()

  hotels = ["Kalton Hotel", # 7 reviews
            "WelaBajo Hotel", # 40 reviews
            "Achazia Homestay", # 2 reviews
            "Dewondaru Home Stay", # 10 reviews
            ]

  model = Model()


  for hotel in hotels:
    print(hotel)
    text = db_connector.mongo_parse("hotel-cleaned", hotel)

    embeddings = model.embed(text)

    for i, chunk in enumerate(embeddings):
      vector_data = {
        "id" : f"Hotel-{hotel}-{i}",
        "values" : embeddings,
        "metadata" : {"category": "hotel"}
      }

      db_connector.pinecone_upsert(vector_data)

