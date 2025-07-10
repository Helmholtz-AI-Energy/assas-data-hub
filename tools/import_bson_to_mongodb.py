"""Import documents from files.bson into MongoDB assas.files collection."""

import logging
from pathlib import Path
from pymongo import MongoClient
import bson

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_bson_to_mongodb(bson_file_path: str, connection_string: str = "mongodb://localhost:27017/"):
    """Import BSON file into MongoDB collection."""
    
    # Check if BSON file exists
    bson_path = Path(bson_file_path)
    if not bson_path.exists():
        logger.error(f"BSON file not found: {bson_file_path}")
        return False
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        db = client['assas']
        collection = db['files']
        
        logger.info(f"Connected to MongoDB: {connection_string}")
        logger.info(f"Target database: assas")
        logger.info(f"Target collection: files")
        
        # Read and import BSON file
        documents = []
        
        with open(bson_path, 'rb') as bson_file:
            # Read all documents from BSON file
            while True:
                try:
                    # Decode each BSON document
                    doc = bson.decode(bson_file.read(4096))  # Read in chunks
                    if doc:
                        documents.append(doc)
                    else:
                        break
                except Exception:
                    # End of file or corrupt data
                    break
        
        if not documents:
            logger.warning("No documents found in BSON file")
            return False
        
        logger.info(f"Found {len(documents)} documents to import")
        
        # Clear existing collection (optional - comment out if you want to keep existing data)
        # collection.delete_many({})
        # logger.info("Cleared existing collection")
        
        # Insert documents
        if len(documents) == 1:
            result = collection.insert_one(documents[0])
            logger.info(f"Inserted 1 document with ID: {result.inserted_id}")
        else:
            result = collection.insert_many(documents)
            logger.info(f"Inserted {len(result.inserted_ids)} documents")
        
        # Verify insertion
        total_count = collection.count_documents({})
        logger.info(f"Total documents in collection: {total_count}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Error importing BSON file: {e}")
        return False

if __name__ == "__main__":
    # Configuration
    BSON_FILE_PATH = "D:/03_Projekte/backup/files.bson"  # Update this path
    CONNECTION_STRING = "mongodb://localhost:27017/"
    
    # Import the BSON file
    success = import_bson_to_mongodb(BSON_FILE_PATH, CONNECTION_STRING)
    
    if success:
        print("✅ BSON import completed successfully!")
    else:
        print("❌ BSON import failed!")