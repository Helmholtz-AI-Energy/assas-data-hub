"""Show the actual content of the MongoDB assas.users collection."""

import logging
import json
import argparse
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("show_db_content")


def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def show_database_content(database: str = "assas", collection: str = "users"):
    """Show the actual content of the MongoDB database."""
    try:
        # Connect to MongoDB (using the same connection as your tools)
        connectionstring = "mongodb://localhost:27017/"
        print(f"\nConnecting to MongoDB at {connectionstring}")
        client = MongoClient(connectionstring)
        db = client[database]
        users_collection = db[collection]

        print("=" * 80)
        print("MONGODB DATABASE CONTENT")
        print("=" * 80)
        print(f"Database: {database}")
        print(f"Collection: {collection}")
        print(f"Connection: {connectionstring}")
        print("=" * 80)

        # Check if database exists
        db_list = client.list_database_names()
        print(f"\nAvailable databases: {db_list}")

        if database not in db_list:
            print(f"\n❌ Database '{database}' does not exist!")
            return

        # Check collections in the database
        collections = db.list_collection_names()
        print(f"\nCollections in '{database}' database: {collections}")

        if collection not in collections:
            print(f"\n❌ Collection '{collection}' does not exist!")
            return

        # Get total count
        total_users = users_collection.count_documents({})
        print(f"\n📊 Total documents in {collection} collection: {total_users}")

        if total_users == 0:
            print(f"\n❌ No documents found in the {collection} collection!")
            return

        # Show indexes
        print(f"\n📋 INDEXES:")
        print("-" * 40)
        for index in users_collection.list_indexes():
            print(f"  - {index['name']}: {index.get('key', {})}")
            if index.get("unique"):
                print(f"    (UNIQUE)")

        # Show all documents
        print(f"\n👥 {collection.upper()} DOCUMENTS:")
        print("-" * 40)

        documents = list(users_collection.find())

        for i, doc in enumerate(documents, 1):
            print(f"\n[{i}] DOCUMENT:")
            print("-" * 20)

            # Print in a readable format
            for key, value in doc.items():
                if key == "_id":
                    print(f"  {key}: {value} (ObjectId)")
                elif isinstance(value, datetime):
                    print(f"  {key}: {value.isoformat()}")
                elif isinstance(value, list):
                    print(f"  {key}: {value}")
                elif isinstance(value, dict):
                    print(
                        f"  {key}: {json.dumps(value, indent=4, default=json_serializer)}"
                    )
                else:
                    print(f"  {key}: {value}")

            print("-" * 20)

        # Show summary statistics (only for users collection)
        if collection == "users":
            print(f"\n📈 SUMMARY STATISTICS:")
            print("-" * 40)

            # Count by provider
            provider_stats = {}
            role_stats = {}
            active_stats = {"active": 0, "inactive": 0}
            institute_stats = {}

            for doc in documents:
                # Provider stats
                provider = doc.get("provider", "unknown")
                provider_stats[provider] = provider_stats.get(provider, 0) + 1

                # Role stats
                roles = doc.get("roles", [])
                if isinstance(roles, list):
                    for role in roles:
                        role_stats[role] = role_stats.get(role, 0) + 1
                elif roles:
                    role_stats[roles] = role_stats.get(roles, 0) + 1

                # Active stats
                if doc.get("is_active", True):
                    active_stats["active"] += 1
                else:
                    active_stats["inactive"] += 1

                # Institute stats
                institute = doc.get("institute", "Unknown")
                institute_stats[institute] = institute_stats.get(institute, 0) + 1

            print(f"Providers: {provider_stats}")
            print(f"Roles: {role_stats}")
            print(f"Active Status: {active_stats}")
            print(f"Institutes: {institute_stats}")

        # Show raw JSON for first document
        if documents:
            print(f"\n🔍 FIRST DOCUMENT AS RAW JSON:")
            print("-" * 40)
            print(json.dumps(documents[0], indent=2, default=json_serializer))

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


def show_config_database(database: str = "assas", collection: str = "users"):
    """Try to show content using config database connection."""
    try:
        print("\n" + "=" * 80)
        print("TRYING CONFIG DATABASE CONNECTION")
        print("=" * 80)

        # Try the config connection (port 27018)
        client = MongoClient("mongodb://127.0.0.1:27018/")
        db = client[database]
        collection_obj = db[collection]

        print(f"Connection: mongodb://127.0.0.1:27018/")

        # Check if this works
        total_docs = collection_obj.count_documents({})
        print(f"Total documents found: {total_docs}")

        if total_docs > 0:
            print(f"\n👥 {collection.upper()} (using config connection):")
            for doc in collection_obj.find():
                if collection == "users":
                    print(f"  - {doc.get('username', 'unknown')} ({doc.get('email', 'no email')})")
                else:
                    print(f"  - Document ID: {doc.get('_id')}")

    except Exception as e:
        print(f"Config connection failed: {e}")
    finally:
        try:
            client.close()
        except:
            pass


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Show the content of MongoDB database and collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python show_database_content.py                           # Default: assas_dev.users
  python show_database_content.py -d assas -c users         # Specific database and collection
  python show_database_content.py --database assas_prod     # Different database
  python show_database_content.py -c files                  # Different collection
        """
    )
    
    parser.add_argument(
        "-d", "--database",
        default="assas_dev",
        help="Database name (default: assas_dev)"
    )
    
    parser.add_argument(
        "-c", "--collection", 
        default="users",
        help="Collection name (default: users)"
    )
    
    parser.add_argument(
        "--config-port",
        action="store_true",
        help="Also try connection on port 27018 (config database)"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    print("Checking MongoDB content...")

    args = parse_arguments()
    
    print(f"Using database: {args.database}")
    print(f"Using collection: {args.collection}")

    # Try the tools connection first (port 27017)
    show_database_content(database=args.database, collection=args.collection)

    # Also try the config connection (port 27018) if requested
    if args.config_port:
        show_config_database(database=args.database, collection=args.collection)
