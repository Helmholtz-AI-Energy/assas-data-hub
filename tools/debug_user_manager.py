"""Debug the UserManager to see exactly what's happening."""

import sys
import os

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

# Add flask_app to Python path for relative imports
flask_app_path = os.path.join(project_root, "flask_app")
sys.path.insert(0, flask_app_path)

from flask_app.database.user_manager import UserManager
from pymongo import MongoClient


def debug_user_manager():
    """Debug the UserManager step by step."""
    print("=" * 60)
    print("DEBUGGING USER MANAGER")
    print("=" * 60)

    # Test direct MongoDB connection first
    print("\n1. Testing direct MongoDB connection...")
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["assas"]
        users_collection = db["users"]

        # Check connection
        client.admin.command("ping")
        print("✅ Direct MongoDB connection successful")

        # Count documents directly
        direct_count = users_collection.count_documents({})
        print(f"📊 Direct count: {direct_count} documents")

        if direct_count > 0:
            print("👥 Sample users from direct connection:")
            for i, user in enumerate(users_collection.find().limit(3)):
                print(
                    f"  {i+1}. {user.get('username', 'no username')} - {user.get('email', 'no email')}"
                )

        client.close()

    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        return

    print("\n2. Testing UserManager...")
    try:
        # Test UserManager
        user_manager = UserManager()
        print("✅ UserManager initialized successfully")

        # Test get_all_users method
        print("\n3. Testing get_all_users() method...")
        all_users = user_manager.get_all_users()
        print(f"📊 UserManager count: {len(all_users)} users")

        if all_users:
            print("👥 Sample users from UserManager:")
            for i, user in enumerate(all_users[:3]):
                print(
                    f"  {i+1}. {user.get('username', 'no username')} - {user.get('email', 'no email')}"
                )
                print(f"      Keys: {list(user.keys())}")
        else:
            print("❌ UserManager returned empty list!")

            # Let's check what the raw query returns
            print("\n4. Testing raw MongoDB query through UserManager...")
            try:
                raw_users = list(user_manager.users_collection.find({}))
                print(f"📊 Raw query count: {len(raw_users)} users")

                if raw_users:
                    print("👥 Sample from raw query:")
                    for i, user in enumerate(raw_users[:3]):
                        print(f"  {i+1}. {user}")

            except Exception as e:
                print(f"❌ Raw query failed: {e}")

        # Test specific queries
        print("\n5. Testing specific user queries...")

        # Try to get a user by username if we know one exists
        try:
            sample_user = user_manager.users_collection.find_one()
            if sample_user:
                username = sample_user.get("username")
                if username:
                    test_user = user_manager.get_user_by_username(username)
                    if test_user:
                        print(f"✅ get_user_by_username works: {username}")
                    else:
                        print(f"❌ get_user_by_username failed for: {username}")
        except Exception as e:
            print(f"❌ Specific query test failed: {e}")

    except Exception as e:
        print(f"❌ UserManager initialization failed: {e}")
        import traceback

        traceback.print_exc()


def test_admin_page_functions():
    """Test the functions that the admin page uses."""
    print("\n" + "=" * 60)
    print("TESTING ADMIN PAGE FUNCTIONS")
    print("=" * 60)

    try:
        # Create a minimal Flask app context for testing
        from flask import Flask

        app = Flask(__name__)

        with app.app_context():
            # Import admin functions - create simplified versions to avoid imports
            def get_user_stats_test():
                """Test version of get_user_stats."""
                try:
                    user_manager = UserManager()
                    all_users = user_manager.get_all_users()

                    stats = {
                        "total_users": len(all_users),
                        "active_users": sum(
                            1 for user in all_users if user.get("is_active", True)
                        ),
                        "github_users": sum(
                            1 for user in all_users if user.get("provider") == "github"
                        ),
                        "basic_auth_users": sum(
                            1
                            for user in all_users
                            if user.get("provider") == "basic_auth"
                        ),
                        "admin_users": sum(
                            1 for user in all_users if "admin" in user.get("roles", [])
                        ),
                    }

                    return stats

                except Exception as e:
                    print(f"Error in get_user_stats_test: {e}")
                    return {
                        "total_users": 0,
                        "active_users": 0,
                        "github_users": 0,
                        "basic_auth_users": 0,
                        "admin_users": 0,
                    }

            def get_users_data_test():
                """Test version of get_users_data."""
                try:
                    user_manager = UserManager()
                    all_users = user_manager.get_all_users()

                    users_data = []
                    for user in all_users:
                        roles = user.get("roles", [])
                        if isinstance(roles, list):
                            roles_str = ", ".join(roles)
                        else:
                            roles_str = str(roles) if roles else "No roles"

                        users_data.append(
                            {
                                "username": user.get("username", ""),
                                "email": user.get("email", ""),
                                "name": user.get("name", ""),
                                "provider": user.get("provider", ""),
                                "roles": roles_str,
                                "is_active": (
                                    "✓" if user.get("is_active", True) else "✗"
                                ),
                                "login_count": user.get("login_count", 0),
                            }
                        )

                    return users_data

                except Exception as e:
                    print(f"Error in get_users_data_test: {e}")
                    return []

            print("\n1. Testing get_user_stats()...")
            stats = get_user_stats_test()
            print(f"Stats: {stats}")

            print("\n2. Testing get_users_data()...")
            users_data = get_users_data_test()
            print(f"Users data count: {len(users_data)}")

            if users_data:
                print("Sample user data:")
                print(users_data[0])

    except Exception as e:
        print(f"❌ Admin page functions test failed: {e}")
        import traceback

        traceback.print_exc()


def check_database_structure():
    """Check the actual database structure to identify the issue."""
    print("\n" + "=" * 60)
    print("DATABASE STRUCTURE CHECK")
    print("=" * 60)

    try:
        client = MongoClient("mongodb://localhost:27017/")

        print("Available databases:")
        for db_name in client.list_database_names():
            if db_name not in ["admin", "config", "local"]:
                db = client[db_name]
                collections = db.list_collection_names()
                print(f"  📁 Database: {db_name}")

                for collection_name in collections:
                    collection = db[collection_name]
                    count = collection.count_documents({})
                    print(f"    📄 Collection: {collection_name} ({count} documents)")

                    # If this collection has documents, show sample
                    if count > 0 and "user" in collection_name.lower():
                        sample = collection.find_one()
                        if sample:
                            print(
                                f"        Sample document keys: {list(sample.keys())}"
                            )
                            print(
                                f"        Sample: {sample.get('username', 'no username')} - {sample.get('email', 'no email')}"
                            )

        client.close()

    except Exception as e:
        print(f"❌ Database structure check failed: {e}")


if __name__ == "__main__":
    debug_user_manager()
    test_admin_page_functions()
    check_database_structure()
