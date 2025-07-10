"""Transfer all documents from assas_dev.files to assas.files collection."""

import logging
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, ConnectionFailure

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transfer_files_collection(connection_string: str = "mongodb://localhost:27017/"):
    """Transfer all documents from assas_dev.files to assas.files."""
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        
        # Test connection
        client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {connection_string}")
        
        # Source and target databases/collections
        source_db = client['assas_dev']
        source_collection = source_db['files']
        
        target_db = client['assas']
        target_collection = target_db['files']
        
        # Check source collection
        source_count = source_collection.count_documents({})
        logger.info(f"Source collection (assas_dev.files): {source_count} documents")
        
        if source_count == 0:
            logger.warning("Source collection is empty. Nothing to transfer.")
            client.close()
            return True
        
        # Check target collection before transfer
        target_count_before = target_collection.count_documents({})
        logger.info(f"Target collection (assas.files) before transfer: {target_count_before} documents")
        
        # Optional: Clear target collection first (uncomment if you want to replace all data)
        # target_collection.delete_many({})
        # logger.info("Cleared target collection")
        
        # Read all documents from source
        logger.info("Reading documents from source collection...")
        documents = list(source_collection.find({}))
        logger.info(f"Retrieved {len(documents)} documents from source")
        
        # Transfer documents to target collection
        logger.info("Transferring documents to target collection...")
        
        try:
            if len(documents) == 1:
                result = target_collection.insert_one(documents[0])
                logger.info(f"Inserted 1 document with ID: {result.inserted_id}")
            else:
                # Use insert_many with ordered=False to continue on duplicates
                result = target_collection.insert_many(documents, ordered=False)
                logger.info(f"Inserted {len(result.inserted_ids)} documents")
                
        except BulkWriteError as e:
            # Handle duplicate key errors
            successful_inserts = len(documents) - len(e.details.get('writeErrors', []))
            duplicate_errors = len(e.details.get('writeErrors', []))
            logger.info(f"Transfer completed with some duplicates:")
            logger.info(f"  - Successfully inserted: {successful_inserts} documents")
            logger.info(f"  - Duplicate/error documents: {duplicate_errors}")
        
        # Verify transfer
        target_count_after = target_collection.count_documents({})
        new_documents = target_count_after - target_count_before
        
        logger.info("Transfer Summary:")
        logger.info(f"  - Source documents: {source_count}")
        logger.info(f"  - Target before: {target_count_before}")
        logger.info(f"  - Target after: {target_count_after}")
        logger.info(f"  - New documents added: {new_documents}")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        logger.error(f"Error during transfer: {e}")
        return False

def transfer_with_upsert(connection_string: str = "mongodb://localhost:27017/"):
    """Transfer with upsert to handle duplicates gracefully."""
    
    try:
        client = MongoClient(connection_string)
        client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {connection_string}")
        
        source_collection = client['assas_dev']['files']
        target_collection = client['assas']['files']
        
        source_count = source_collection.count_documents({})
        logger.info(f"Source collection: {source_count} documents")
        
        if source_count == 0:
            logger.warning("Source collection is empty.")
            client.close()
            return True
        
        # Transfer with upsert (replace existing documents with same _id)
        logger.info("Starting upsert transfer...")
        
        transferred = 0
        updated = 0
        
        for doc in source_collection.find({}):
            # Use upsert based on _id
            result = target_collection.replace_one(
                {"_id": doc["_id"]}, 
                doc, 
                upsert=True
            )
            
            if result.upserted_id:
                transferred += 1
            elif result.modified_count > 0:
                updated += 1
        
        logger.info(f"Transfer completed:")
        logger.info(f"  - New documents: {transferred}")
        logger.info(f"  - Updated documents: {updated}")
        logger.info(f"  - Total processed: {transferred + updated}")
        
        # Final verification
        final_count = target_collection.count_documents({})
        logger.info(f"Final target collection count: {final_count}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Error during upsert transfer: {e}")
        return False

def show_collection_sample():
    """Show sample documents from both collections for verification."""
    
    try:
        client = MongoClient("mongodb://localhost:27017/")
        
        logger.info("Sample documents from collections:")
        
        # Sample from source
        source_collection = client['assas_dev']['files']
        source_sample = source_collection.find_one()
        if source_sample:
            logger.info(f"Source sample (assas_dev.files): {list(source_sample.keys())}")
        
        # Sample from target
        target_collection = client['assas']['files']
        target_sample = target_collection.find_one()
        if target_sample:
            logger.info(f"Target sample (assas.files): {list(target_sample.keys())}")
        
        client.close()
        
    except Exception as e:
        logger.error(f"Error showing samples: {e}")

if __name__ == "__main__":
    print("MongoDB Collection Transfer Script")
    print("="*50)
    
    # Show current state
    show_collection_sample()
    
    print("\nChoose transfer method:")
    print("1. Simple transfer (insert_many)")
    print("2. Upsert transfer (replace existing)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        logger.info("Starting simple transfer...")
        success = transfer_files_collection()
    elif choice == "2":
        logger.info("Starting upsert transfer...")
        success = transfer_with_upsert()
    else:
        logger.info("Starting simple transfer (default)...")
        success = transfer_files_collection()
    
    if success:
        print("\n✅ Transfer completed successfully!")
        show_collection_sample()
    else:
        print("\n❌ Transfer failed!")