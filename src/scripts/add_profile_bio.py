import re
import os
import sys
from typing import List, Dict
import pymongo
from dotenv import load_dotenv
import requests

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm.src.connector.mongo import MongoConnector

load_dotenv()

def hit_rapi_api(user_id: str):
  url = "https://instagram-premium-api-2023.p.rapidapi.com/v1/user/by/id"

  querystring = {"id": user_id}

  headers = {
    "x-rapidapi-key": "feda1f0ff8msh486ddf5c06655f2p1dd6aejsn9013135cabb5",
    "x-rapidapi-host": "instagram-premium-api-2023.p.rapidapi.com"
  }

  response = requests.get(url, headers=headers, params=querystring)
  
  if (response.status_code == 200):
    response_json = response.json()
    # Return biography if exists, otherwise empty string
    return response_json.get("biography", "")
  
  return ""  # Return empty string if API call fails

def process_communities_add_influencer_bio(limit = None):
  mongo = MongoConnector()

  # Get all communities
  communities = mongo.get_data("communities")
  print(f"Found {len(communities)} communities in database")

  if limit: 
    communities = communities[:limit]
    print(f"Processing only first {limit} communities")

  total_influencers = 0
  updated_communities = 0

  for community in communities:
    community_id = community.get("community_id", "unknown")
    influencers = community.get("influencers", [])

    if not influencers:
      print(f"Community {community_id} has no influencers, skipping...")
      continue

    updated_influencers = []
    influencers_updated_count = 0

    for influencer in influencers:
      user_id = influencer.get("id")
      
      if user_id:
        # Get biography from API
        bio = hit_rapi_api(str(user_id))
        
        # Add biography to influencer
        influencer["biography"] = bio
        updated_influencers.append(influencer)
        
        if bio:  # Only count if bio was actually added
          influencers_updated_count += 1
          total_influencers += 1
        
        print(f"Processing influencer {user_id}: {'Added bio' if bio else 'No bio found'}")
      else:
        # Keep influencer as is if no ID
        updated_influencers.append(influencer)
    
    # Update the community with influencers that now have bios
    if influencers_updated_count > 0:
      mongo.update_one_data(
        "communities",
        {"community_id": community_id},
        {"influencers": updated_influencers}
      )
      updated_communities += 1
      print(f"Updated community {community_id}: {influencers_updated_count}/{len(influencers)} influencers with bios")
  
  print(f"\nSummary:")
  print(f"- Total communities processed: {len(communities)}")
  print(f"- Communities updated: {updated_communities}")
  print(f"- Total influencers with bios added: {total_influencers}")


def display_sample_results():
  """
  Display a few sample influencers with their bios.
  """
  mongo = MongoConnector()
  
  # Get communities to check results
  communities = mongo.get_data("communities", {})
  
  if not communities:
    print("No communities found")
    return
  
  print("\nSample influencers with biographies:")
  samples_shown = 0
  
  for community in communities[:10]:  # Check first 10 communities
    influencers = community.get("influencers", [])
    
    for influencer in influencers:
      if influencer.get("biography") and samples_shown < 5:
        print(f"\nInfluencer ID: {influencer.get('id')}")
        print(f"Username: {influencer.get('username', 'unknown')}")
        print(f"Biography: {influencer.get('biography', '')[:100]}...")
        samples_shown += 1
    
    if samples_shown >= 5:
      break

  
if __name__ == "__main__":
  print("Starting to add user's bio to communities' influencers")

  try:
    # Process only 10 communities
    process_communities_add_influencer_bio()
    
    print("\n" + "="*50)
    print("Sample results:")
    print("="*50)
    
    # Show sample results
    display_sample_results()
    
  except Exception as e:
    print(f"Error occurred: {str(e)}")
    import traceback
    traceback.print_exc()