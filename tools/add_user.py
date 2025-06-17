from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = client['assas']  # Database name
users_collection = db['users']  # Collection name

# Insert user information
users = [
    {
        "username": "admin",
        "password": generate_password_hash("admin"),
        "email": "admin@example.com",
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
        "password": generate_password_hash("assas123"),
        "email": "markus@example.com",
        "institute": "Markus Institute",
        "role": "Researcher"
    }
]

# Insert users into the collection
users_collection.insert_many(users)
print("Users inserted successfully!")