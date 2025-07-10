"""Add users to ASSAS Data Hub MongoDB database with proper schema."""

import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from werkzeug.security import generate_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('assas_add_user')

# MongoDB connection setup
connectionstring = "mongodb://localhost:27017/"
client = MongoClient(connectionstring)
db = client['assas']
users_collection = db['users']

# Role mapping from old system to new system
ROLE_MAPPING = {
    'Administrator': ['admin'],
    'Researcher': ['researcher'],
    'User': ['viewer'],
    'Curator': ['curator']
}

def setup_indexes():
    """Setup database indexes, handling existing indexes properly."""
    try:
        logger.info("Setting up database indexes...")
        
        # Get existing indexes
        existing_indexes = users_collection.list_indexes()
        existing_index_names = [index['name'] for index in existing_indexes]
        logger.info(f"Existing indexes: {existing_index_names}")
        
        # Drop problematic indexes if they exist and recreate them properly
        indexes_to_recreate = ['email_1', 'username_1']
        
        for index_name in indexes_to_recreate:
            if index_name in existing_index_names:
                logger.info(f"Dropping existing index: {index_name}")
                users_collection.drop_index(index_name)
        
        # Create new indexes with proper specifications
        logger.info("Creating email index (unique)...")
        users_collection.create_index("email", unique=True, name="email_unique")
        
        logger.info("Creating username index (unique)...")
        users_collection.create_index("username", unique=True, name="username_unique")
        
        logger.info("Creating provider index...")
        users_collection.create_index("provider", name="provider_index")
        
        logger.info("Creating roles index...")
        users_collection.create_index("roles", name="roles_index")
        
        logger.info("Creating is_active index...")
        users_collection.create_index("is_active", name="is_active_index")
        
        logger.info("Indexes created successfully!")
        
    except OperationFailure as e:
        logger.error(f"Error setting up indexes: {e}")
        # Continue anyway - indexes are nice to have but not critical for basic functionality
    except Exception as e:
        logger.error(f"Unexpected error setting up indexes: {e}")

def create_user_document(username, password, email, institute, role):
    """Create a properly formatted user document."""
    # Map old role to new roles array
    roles = ROLE_MAPPING.get(role, ['viewer'])
    
    return {
        'username': username,
        'email': email,
        'name': username.title(),  # Capitalize first letter
        'provider': 'basic_auth',
        'roles': roles,
        'is_active': True,
        
        # Basic auth specific fields
        'basic_auth_password_hash': generate_password_hash(password),
        
        # Additional fields for compatibility
        'institute': institute,
        'legacy_role': role,  # Keep original role for reference
        
        # Timestamps
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'last_login': None,
        'login_count': 0,
        
        # Optional fields that might be populated later
        'avatar_url': None,
        'github_id': None,
        'github_profile': None,
        'bwidm_sub': None,
        'entitlements': [],
        'affiliations': []
    }

# User data with proper structure
users_data = [
    {
        "username": "admin",
        "password": "admin",
        "email": "jonas.dressner@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Administrator",
    },
    {
        "username": "jonas",
        "password": "r.adio_1",
        "email": "jonas.dressner2@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Researcher",
    },
    {
        "username": "markus",
        "password": "assas2025",
        "email": "markus.goetz@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Researcher",
    },
    {
        "username": "charlie",
        "password": "assas2025",
        "email": "charlotte.debus@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Researcher",
    },
    {
        "username": "jure",
        "password": "assas2025",
        "email": "jure.brence@ijs.si",
        "institute": "JSI (Slovenia)",
        "role": "Researcher",
    },
    {
        "username": "anastasia",
        "password": "assas2025",
        "email": "anastasia.stakhanova@kit.edu",
        "institute": "KIT (INR)",
        "role": "Researcher",
    },
    {
        "username": "alessandro",
        "password": "assas2025",
        "email": "a.longhi@tudelft.nl",
        "institute": "TU Delft (Netherlands)",
        "role": "Researcher",
    },
    {
        "username": "marcello",
        "password": "assas2025",
        "email": "marcello.savini2@unibo.it",
        "institute": "University of Bologna (Italy)",
        "role": "Researcher",
    },
    {
        "username": "bastien",
        "password": "assas2025",
        "email": "bastien.poubeau@asnr.fr",
        "institute": "ASNR (France)",
        "role": "Researcher",
    },
    {
        "username": "joan",
        "password": "assas2025",
        "email": "joan.fontanet@ciemat.es",
        "institute": "Ciemat (Spain)",
        "role": "Researcher",
    }
]

def clear_existing_users():
    """Clear existing users from the database."""
    try:
        logger.info("Clearing existing users...")
        result = users_collection.delete_many({})
        logger.info(f"Deleted {result.deleted_count} existing users")
        return True
    except Exception as e:
        logger.error(f"Error clearing users: {e}")
        return False

def insert_users(user_documents):
    """Insert users into the database with error handling."""
    try:
        logger.info(f"Inserting {len(user_documents)} users...")
        
        # Try bulk insert first
        try:
            result = users_collection.insert_many(user_documents, ordered=False)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} users via bulk insert")
            return True
        except Exception as bulk_error:
            logger.warning(f"Bulk insert failed: {bulk_error}")
            logger.info("Trying individual inserts...")
            
            # Fall back to individual inserts
            successful_inserts = 0
            failed_inserts = 0
            
            for doc in user_documents:
                try:
                    users_collection.insert_one(doc)
                    successful_inserts += 1
                    logger.info(f"Inserted user: {doc['username']}")
                except Exception as e:
                    failed_inserts += 1
                    logger.error(f"Failed to insert user {doc['username']}: {e}")
            
            logger.info(f"Individual inserts completed: {successful_inserts} successful, {failed_inserts} failed")
            return successful_inserts > 0
            
    except Exception as e:
        logger.error(f"Error during user insertion: {e}")
        return False

def verify_users():
    """Verify inserted users."""
    try:
        logger.info("\n=== VERIFICATION ===")
        
        total_users = users_collection.count_documents({})
        logger.info(f"Total users in database: {total_users}")
        
        # Check basic auth users
        basic_auth_users = list(users_collection.find({
            "basic_auth_password_hash": {"$exists": True, "$ne": None}
        }))
        logger.info(f"Users with basic auth: {len(basic_auth_users)}")
        
        # List all users
        logger.info("\n=== ALL USERS ===")
        for user in users_collection.find():
            logger.info(f"User: {user['username']}")
            logger.info(f"  Email: {user['email']}")
            logger.info(f"  Roles: {user['roles']}")
            logger.info(f"  Institute: {user.get('institute', 'N/A')}")
            logger.info(f"  Provider: {user['provider']}")
            logger.info(f"  Has Password: {'Yes' if user.get('basic_auth_password_hash') else 'No'}")
            logger.info(f"  Created: {user['created_at']}")
            logger.info("  ---")
        
        # Check for duplicates
        pipeline = [
            {"$group": {"_id": "$username", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(users_collection.aggregate(pipeline))
        if duplicates:
            logger.warning(f"Found duplicate usernames: {duplicates}")
        else:
            logger.info("No duplicate usernames found")
            
    except Exception as e:
        logger.error(f"Error during verification: {e}")

def main():
    """Main function to add users to database."""
    try:
        # Clear existing users first
        if not clear_existing_users():
            logger.error("Failed to clear existing users")
            return False
        
        # Setup indexes
        setup_indexes()
        
        # Create user documents
        user_documents = []
        for user_data in users_data:
            doc = create_user_document(
                username=user_data['username'],
                password=user_data['password'],
                email=user_data['email'],
                institute=user_data['institute'],
                role=user_data['role']
            )
            user_documents.append(doc)
        
        # Insert users
        if not insert_users(user_documents):
            logger.error("Failed to insert users")
            return False
        
        # Verify insertion
        verify_users()
        
        logger.info("✓ User creation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✓ All users have been successfully added to the database!")
        print("You can now log in with:")
        print("  Username: admin")
        print("  Password: admin")
        print("  URL: http://localhost:5000/auth/basic/login")
    else:
        print("\n✗ There were errors during user creation. Check the logs above.")