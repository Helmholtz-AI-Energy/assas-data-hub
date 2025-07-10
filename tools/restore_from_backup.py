"""Script to restore collections using AssasDatabaseHandler.restore_collections method."""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from assas_database.assasdb.assas_database_handler import AssasDatabaseHandler
from pymongo import MongoClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def restore_files_collection():
    """Restore the files collection from backup using AssasDatabaseHandler."""
    
    # Configuration
    BACKUP_DIRECTORY = "D:/03_Projekte/backup"
    CONNECTION_STRING = "mongodb://localhost:27017/"
    DATABASE_NAME = "assas"
    COLLECTION_NAME = "files"
    
    logger.info("Starting collection restore process...")
    logger.info(f"Backup directory: {BACKUP_DIRECTORY}")
    logger.info(f"Target database: {DATABASE_NAME}")
    logger.info(f"Target collection: {COLLECTION_NAME}")
    
    # Check if backup directory exists
    backup_path = Path(BACKUP_DIRECTORY)
    if not backup_path.exists():
        logger.error(f"Backup directory does not exist: {BACKUP_DIRECTORY}")
        return False
    
    # Check if files.bson exists
    files_bson_path = backup_path / "files.bson"
    if not files_bson_path.exists():
        logger.error(f"files.bson not found in backup directory: {files_bson_path}")
        return False
    
    logger.info(f"Found backup file: {files_bson_path}")
    
    try:
        # Create MongoDB client
        client = MongoClient(CONNECTION_STRING)
        
        # Test connection
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
        # Check collection count before restore
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        count_before = collection.count_documents({})
        logger.info(f"Documents in collection before restore: {count_before}")
        
        # Create AssasDatabaseHandler with restore_from_backup=True
        logger.info("Initializing AssasDatabaseHandler...")
        db_handler = AssasDatabaseHandler(
            client=client,
            backup_directory=BACKUP_DIRECTORY,
            database_name=DATABASE_NAME,
            file_collection_name=COLLECTION_NAME,
            restore_from_backup=True  # This triggers restore_collections() in __init__
        )
        
        # Check collection count after restore
        count_after = collection.count_documents({})
        new_documents = count_after - count_before
        
        logger.info("Restore completed!")
        logger.info(f"Documents before restore: {count_before}")
        logger.info(f"Documents after restore: {count_after}")
        logger.info(f"New documents added: {new_documents}")
        
        # Clean up
        db_handler.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during restore: {e}")
        return False

def restore_manually():
    """Manually call restore_collections method without using __init__ flag."""
    
    # Configuration
    BACKUP_DIRECTORY = "D:/03_Projekte/assas-data-hub/assas_database/backup"
    CONNECTION_STRING = "mongodb://localhost:27017/"
    DATABASE_NAME = "assas"
    COLLECTION_NAME = "files"
    
    try:
        # Create MongoDB client
        client = MongoClient(CONNECTION_STRING)
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
        # Check collection count before restore
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        count_before = collection.count_documents({})
        logger.info(f"Documents in collection before restore: {count_before}")
        
        # Create AssasDatabaseHandler without auto-restore
        logger.info("Creating AssasDatabaseHandler...")
        db_handler = AssasDatabaseHandler(
            client=client,
            backup_directory=BACKUP_DIRECTORY,
            database_name=DATABASE_NAME,
            file_collection_name=COLLECTION_NAME,
            restore_from_backup=False  # Don't auto-restore
        )
        
        # Manually call restore_collections
        logger.info("Calling restore_collections() manually...")
        db_handler.restore_collections()
        
        # Check collection count after restore
        count_after = collection.count_documents({})
        new_documents = count_after - count_before
        
        logger.info("Manual restore completed!")
        logger.info(f"Documents before restore: {count_before}")
        logger.info(f"Documents after restore: {count_after}")
        logger.info(f"New documents added: {new_documents}")
        
        # Clean up
        db_handler.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during manual restore: {e}")
        return False

def show_backup_info():
    """Show information about available backup files."""
    
    BACKUP_DIRECTORY = "D:/03_Projekte/assas-data-hub/assas_database/backup"
    backup_path = Path(BACKUP_DIRECTORY)
    
    if not backup_path.exists():
        logger.error(f"Backup directory does not exist: {BACKUP_DIRECTORY}")
        return
    
    logger.info(f"Backup directory: {BACKUP_DIRECTORY}")
    logger.info("Available backup files:")
    
    bson_files = list(backup_path.glob("*.bson"))
    if not bson_files:
        logger.warning("No .bson files found in backup directory")
        return
    
    for bson_file in bson_files:
        file_size = bson_file.stat().st_size
        logger.info(f"  - {bson_file.name}: {file_size:,} bytes")

if __name__ == "__main__":
    print("ASSAS Database Collection Restore Script")
    print("=" * 50)
    
    # Show backup information
    show_backup_info()
    
    print("\nChoose restore method:")
    print("1. Auto-restore (using restore_from_backup=True in constructor)")
    print("2. Manual restore (calling restore_collections() explicitly)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        logger.info("Starting auto-restore...")
        success = restore_files_collection()
    elif choice == "2":
        logger.info("Starting manual restore...")
        success = restore_manually()
    else:
        logger.info("Starting auto-restore (default)...")
        success = restore_files_collection()
    
    if success:
        print("\n✅ Restore completed successfully!")
    else:
        print("\n❌ Restore failed!")