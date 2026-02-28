"""
Memory Database Reset Utility
Clears all stored conversations from ChromaDB.
Use this to start fresh or clear test data.
"""

import sys
from pathlib import Path
import shutil

from config.config import MEMORY_DIR, MEMORY_COLLECTION

def confirm_reset():
    """Ask user to confirm before deleting data."""
    print("=" * 60)
    print("Memory Database Reset Utility")
    print("=" * 60)
    print(f"\nThis will DELETE all stored conversations from:")
    print(f"  {MEMORY_DIR}")
    print(f"\nCollection: {MEMORY_COLLECTION}")
    print("\n⚠️  WARNING: This action CANNOT be undone!")
    print("\nAre you sure you want to continue?")
    
    response = input("Type 'yes' to confirm: ").strip().lower()
    return response == "yes"

def reset_memory():
    """Delete the ChromaDB memory directory."""
    if not MEMORY_DIR.exists():
        print(f"\n✓ Memory directory doesn't exist. Nothing to delete.")
        return
    
    try:
        # Count entries before deletion
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(MEMORY_DIR))
            collection = client.get_collection(name=MEMORY_COLLECTION)
            count = collection.count()
            print(f"\nFound {count} conversation entries.")
        except:
            count = "unknown"
            print(f"\nMemory directory exists.")
        
        # Delete the directory
        shutil.rmtree(MEMORY_DIR)
        print(f"\n✓ Deleted memory directory: {MEMORY_DIR}")
        
        # Recreate empty directory
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created fresh memory directory")
        
        print(f"\n{'=' * 60}")
        print("✓ Memory reset complete!")
        print("=" * 60)
        print("\nThe next time you run the app, it will start with a clean slate.")
        
    except Exception as e:
        print(f"\n✗ Error during reset: {e}")
        sys.exit(1)

def main():
    print("\n")
    
    if not confirm_reset():
        print("\n✗ Reset cancelled. No data was deleted.")
        sys.exit(0)
    
    reset_memory()

if __name__ == "__main__":
    main()
