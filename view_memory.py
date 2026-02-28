"""
Memory Database Viewer
View all stored conversations without resetting.
"""

import chromadb
from datetime import datetime

from config.config import MEMORY_DIR, MEMORY_COLLECTION

def view_memory():
    """Display all stored conversations."""
    print("=" * 80)
    print("Memory Database Viewer")
    print("=" * 80)
    
    try:
        client = chromadb.PersistentClient(path=str(MEMORY_DIR))
        collection = client.get_collection(name=MEMORY_COLLECTION)
        count = collection.count()
        
        print(f"\nTotal conversations stored: {count}")
        
        if count == 0:
            print("\nNo conversations found. The memory is empty.")
            return
        
        # Get all entries
        results = collection.get(
            include=["metadatas", "documents"]
        )
        
        print("\n" + "=" * 80)
        print("Stored Conversations")
        print("=" * 80)
        
        for i, (doc_id, metadata, document) in enumerate(
            zip(results["ids"], results["metadatas"], results["documents"]), 1
        ):
            timestamp = metadata.get("timestamp", 0)
            dt = datetime.fromtimestamp(timestamp)
            
            user_msg = metadata.get("user_message", "")
            assistant_msg = metadata.get("assistant_response", "")
            sentiment = metadata.get("sentiment_label", "unknown")
            emotion = metadata.get("emotion", "unknown")
            
            print(f"\n[{i}] {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Sentiment: {sentiment} | Emotion: {emotion}")
            print(f"    User: {user_msg[:100]}{'...' if len(user_msg) > 100 else ''}")
            print(f"    AI:   {assistant_msg[:100]}{'...' if len(assistant_msg) > 100 else ''}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error reading memory: {e}")

if __name__ == "__main__":
    view_memory()
