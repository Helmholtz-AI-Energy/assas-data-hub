import logging

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

logger = logging.getLogger('assas_app')

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = client['assas']  # Database name
users_collection = db['users']  # Collection name

# Insert user information
users = [
    {
        "username": "admin",
        "password": generate_password_hash("admin"),
        "email": "jonas.dressner@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Administrator"
    },
    {
        "username": "jonas",
        "password": generate_password_hash("r.adio_1"),
        "email": "jonas.dressner@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Researcher"
    },
    {
        "username": "markus",
        "password": generate_password_hash("assas2025"),
        "email": "markus.goetz@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Researcher"
    }
]

# Insert users into the collection
users_collection.delete_many({})  # Clear existing users
users_collection.insert_many(users)

users = users_collection.find()
for user in users:
    logger.info(f"Inserted user: {user['username']} with email: {user['email']} and role: {user['role']}")

logger.info("Users inserted successfully.")