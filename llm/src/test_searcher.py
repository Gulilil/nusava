from searcher.searcher import Searcher
from model.model import Model

if __name__ == "__main__":
  searcher = Searcher()

  hotels = ["Kalton Hotel", # 7 reviews
            "WelaBajo Hotel", # 40 reviews
            "Achazia Homestay", # 2 reviews
            "Dewondaru Home Stay", # 10 reviews
            ]

  model = Model()

  for hotel in hotels:
    print(hotel)
    doc = searcher.parse("hotel", hotel)
    embeddings = model.embed(doc)
    print(f"Number of embeddings: {len(embeddings)}")
    print(f"Length of each embedding: {len(embeddings[0])}")

