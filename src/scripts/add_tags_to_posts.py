import re
import os
import sys
from typing import List, Dict
import pymongo
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm.src.connector.mongo import MongoConnector

load_dotenv()


def extract_tags_from_caption(caption: str) -> List[str]:
    """
    Extract hashtags from caption and clean them up.
    Returns a list of cleaned tags without the # symbol.
    """
    if not caption:
        return []
    
    # Find all hashtags in the caption
    hashtags = re.findall(r'#(\w+)', caption)
    
    # Clean up tags - lowercase and remove duplicates
    cleaned_tags = []
    seen = set()
    
    for tag in hashtags:
        # Convert to lowercase
        tag_lower = tag.lower()
        
        # Split camelCase or PascalCase tags
        # e.g., "beachLife" -> ["beach", "life"]
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', tag)
        
        if len(words) > 1:
            # Add the full tag
            if tag_lower not in seen:
                cleaned_tags.append(tag_lower)
                seen.add(tag_lower)
            
            # Add individual words as separate tags
            for word in words:
                word_lower = word.lower()
                if word_lower not in seen and len(word_lower) > 2:  # Skip very short words
                    cleaned_tags.append(word_lower)
                    seen.add(word_lower)
        else:
            # Single word tag
            if tag_lower not in seen:
                cleaned_tags.append(tag_lower)
                seen.add(tag_lower)
    
    return cleaned_tags


def process_communities_add_tags(limit=None):
    """
    Read all communities data from MongoDB and add tags to each post.
    
    Args:
        limit: Maximum number of communities to process (None for all)
    """
    mongo = MongoConnector()
    
    # Get all communities
    communities = mongo.get_data("communities")
    print(f"Found {len(communities)} communities in database")
    
    # Limit the number of communities to process
    if limit:
        communities = communities[:limit]
        print(f"Processing only first {limit} communities")
    
    total_posts = 0
    updated_communities = 0
    
    for community in communities:
        community_id = community.get("community_id", "unknown")
        posts = community.get("posts", [])
        
        if not posts:
            print(f"Community {community_id} has no posts, skipping...")
            continue
        
        updated_posts = []
        posts_updated_count = 0
        
        for post in posts:
            caption = post.get("caption", "")
            
            # Extract tags from caption
            tags = extract_tags_from_caption(caption)
            
            # Add tags to post
            post["tags"] = tags
            updated_posts.append(post)
            
            if tags:
                posts_updated_count += 1
                total_posts += 1
        
        # Update the community with posts that now have tags
        if posts_updated_count > 0:
            mongo.update_one_data(
                "communities",
                {"community_id": community_id},
                {"posts": updated_posts}
            )
            updated_communities += 1
            print(f"Updated community {community_id}: {posts_updated_count}/{len(posts)} posts with tags")
    
    print(f"\nSummary:")
    print(f"- Total communities processed: {len(communities)}")
    print(f"- Communities updated: {updated_communities}")
    print(f"- Total posts with tags added: {total_posts}")


def display_sample_results():
    """
    Display a few sample posts with their extracted tags.
    """
    mongo = MongoConnector()
    
    # Get one community as a sample
    communities = mongo.get_data("communities", {})
    
    if not communities:
        print("No communities found")
        return
    
    # Find a community with posts that have tags
    for community in communities[:5]:  # Check first 5 communities
        posts = community.get("posts", [])
        
        for post in posts[:3]:  # Check first 3 posts
            if post.get("tags"):
                print(f"\nPost ID: {post.get('id', 'unknown')}")
                print(f"Caption preview: {post.get('caption', '')[:100]}...")
                print(f"Extracted tags: {post.get('tags', [])}")


if __name__ == "__main__":
    print("Starting to add tags to posts in communities collection...")
    
    try:
        # Process only 10 communities
        process_communities_add_tags()
        
        print("\n" + "="*50)
        print("Sample results:")
        print("="*50)
        
        # Show some sample results
        display_sample_results()
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()