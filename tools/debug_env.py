"""Debug environment variables and database names."""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient

def debug_environment():
    print("=" * 60)
    print("ENVIRONMENT VARIABLES DEBUG")
    print("=" * 60)
    
    # Check environment variables
    connectionstring = os.getenv('CONNECTIONSTRING', 'NOT SET')
    mongo_db_name = os.getenv('MONGO_DB_NAME', 'NOT SET')
    
    print(f"CONNECTIONSTRING env var: {connectionstring}")
    print(f"MONGO_DB_NAME env var: {mongo_db_name}")
    
    # What UserManager would actually use
    connection_string = "mongodb://localhost:27017/"  # Hardcoded in your UserManager
    db_name = os.getenv('MONGO_DB_NAME', 'assas')
    
    print(f"UserManager connection: {connection_string}")
    print(f"UserManager database: {db_name}")
    
    print("\n" + "=" * 60)
    print("DATABASE EXPLORATION")
    print("=" * 60)
    
    client = MongoClient("mongodb://localhost:27017/")
    
    # List all databases
    print("Available databases:")
    for db_name_available in client.list_database_names():
        db = client[db_name_available]
        collections = db.list_collection_names()
        print(f"  📁 {db_name_available}")
        for collection in collections:
            if 'user' in collection.lower():
                count = db[collection].count_documents({})
                print(f"    📄 {collection}: {count} documents")
    
    # Test specific database combinations
    print(f"\nTesting specific database/collection combinations:")
    
    test_combinations = [
        ('assas', 'users'),
        ('assas', 'user'),
        ('test', 'users'),
        ('admin', 'users'),
        ('local', 'users'),
    ]
    
    for db_name, collection_name in test_combinations:
        try:
            db = client[db_name]
            collection = db[collection_name]
            count = collection.count_documents({})
            if count > 0:
                print(f"  ✅ {db_name}.{collection_name}: {count} documents")
                # Show sample user
                sample = collection.find_one()
                if sample:
                    username = sample.get('username', 'unknown')
                    email = sample.get('email', 'unknown')
                    print(f"      Sample: {username} ({email})")
            else:
                print(f"  ❌ {db_name}.{collection_name}: 0 documents")
        except Exception as e:
            print(f"  ❌ {db_name}.{collection_name}: Error - {e}")
    
    client.close()

if __name__ == "__main__":
    debug_environment()