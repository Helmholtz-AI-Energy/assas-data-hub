"""Show the actual content of the MongoDB assas.users collection."""

import logging
import json
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('show_db_content')

def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def show_database_content():
    """Show the actual content of the MongoDB database."""
    try:
        # Connect to MongoDB (using the same connection as your tools)
        connectionstring = "mongodb://localhost:27017/"
        print(f"\nConnecting to MongoDB at {connectionstring}")
        client = MongoClient(connectionstring)
        db = client['assas']
        users_collection = db['users']
        
        print("=" * 80)
        print("MONGODB DATABASE CONTENT")
        print("=" * 80)
        print(f"Database: assas")
        print(f"Collection: users")
        print(f"Connection: {connectionstring}")
        print("=" * 80)
        
        # Check if database exists
        db_list = client.list_database_names()
        print(f"\nAvailable databases: {db_list}")
        
        if 'assas' not in db_list:
            print("\n❌ Database 'assas' does not exist!")
            return
        
        # Check collections in the database
        collections = db.list_collection_names()
        print(f"\nCollections in 'assas' database: {collections}")
        
        if 'users' not in collections:
            print("\n❌ Collection 'users' does not exist!")
            return
        
        # Get total count
        total_users = users_collection.count_documents({})
        print(f"\n📊 Total documents in users collection: {total_users}")
        
        if total_users == 0:
            print("\n❌ No users found in the collection!")
            return
        
        # Show indexes
        print(f"\n📋 INDEXES:")
        print("-" * 40)
        for index in users_collection.list_indexes():
            print(f"  - {index['name']}: {index.get('key', {})}")
            if index.get('unique'):
                print(f"    (UNIQUE)")
        
        # Show all users
        print(f"\n👥 USER DOCUMENTS:")
        print("-" * 40)
        
        users = list(users_collection.find())
        
        for i, user in enumerate(users, 1):
            print(f"\n[{i}] USER DOCUMENT:")
            print("-" * 20)
            
            # Print in a readable format
            for key, value in user.items():
                if key == '_id':
                    print(f"  {key}: {value} (ObjectId)")
                elif isinstance(value, datetime):
                    print(f"  {key}: {value.isoformat()}")
                elif isinstance(value, list):
                    print(f"  {key}: {value}")
                elif isinstance(value, dict):
                    print(f"  {key}: {json.dumps(value, indent=4, default=json_serializer)}")
                else:
                    print(f"  {key}: {value}")
            
            print("-" * 20)
        
        # Show summary statistics
        print(f"\n📈 SUMMARY STATISTICS:")
        print("-" * 40)
        
        # Count by provider
        provider_stats = {}
        role_stats = {}
        active_stats = {'active': 0, 'inactive': 0}
        institute_stats = {}
        
        for user in users:
            # Provider stats
            provider = user.get('provider', 'unknown')
            provider_stats[provider] = provider_stats.get(provider, 0) + 1
            
            # Role stats
            roles = user.get('roles', [])
            if isinstance(roles, list):
                for role in roles:
                    role_stats[role] = role_stats.get(role, 0) + 1
            elif roles:
                role_stats[roles] = role_stats.get(roles, 0) + 1
            
            # Active stats
            if user.get('is_active', True):
                active_stats['active'] += 1
            else:
                active_stats['inactive'] += 1
            
            # Institute stats
            institute = user.get('institute', 'Unknown')
            institute_stats[institute] = institute_stats.get(institute, 0) + 1
        
        print(f"Providers: {provider_stats}")
        print(f"Roles: {role_stats}")
        print(f"Active Status: {active_stats}")
        print(f"Institutes: {institute_stats}")
        
        # Show raw JSON for first user
        if users:
            print(f"\n🔍 FIRST USER AS RAW JSON:")
            print("-" * 40)
            print(json.dumps(users[0], indent=2, default=json_serializer))
        
        print("\n" + "=" * 80)
        print("DATABASE CONTENT DISPLAY COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Error showing database content: {e}")
        print(f"\n❌ Error: {e}")
    finally:
        try:
            client.close()
        except:
            pass

def show_config_database():
    """Try to show content using config database connection."""
    try:
        print("\n" + "=" * 80)
        print("TRYING CONFIG DATABASE CONNECTION")
        print("=" * 80)
        
        # Try the config connection (port 27018)
        client = MongoClient("mongodb://127.0.0.1:27018/")
        db = client['assas']
        users_collection = db['users']
        
        print(f"Connection: mongodb://127.0.0.1:27018/")
        
        # Check if this works
        total_users = users_collection.count_documents({})
        print(f"Total users found: {total_users}")
        
        if total_users > 0:
            print("\n👥 USERS (using config connection):")
            for user in users_collection.find():
                print(f"  - {user.get('username', 'unknown')} ({user.get('email', 'no email')})")
        
    except Exception as e:
        print(f"Config connection failed: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    print("Checking MongoDB content...")
    
    # Try the tools connection first (port 27017)
    show_database_content()
    
    # Also try the config connection (port 27018)
    show_config_database()