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
        "role": "Administrator",
    },
    {
        "username": "jonas",
        "password": generate_password_hash("r.adio_1"),
        "email": "jonas.dressner@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Researcher",
    },
    {
        "username": "markus",
        "password": generate_password_hash("assas2025"),
        "email": "markus.goetz@kit.edu",
        "institute": "KIT (SCC)",
        "role": "Researcher",
    },
    {
        "username": "jure",
        "password": generate_password_hash("assas2025"),
        "email": "jure.brence@ijs.si",
        "institute": "JSI (Slovenia)",
        "role": "Researcher",
    },
    {
        "username": "anastasia",
        "password": generate_password_hash("assas2025"),
        "email": "anastasia.stakhanova@kit.edu",
        "institute": "KIT (INR)",
        "role": "Researcher",
    },
    {
        "username": "alessandro",
        "password": generate_password_hash("assas2025"),
        "email": "a.longhi@tudelft.nl",
        "institute": "TU Delft (Netherlands)",
        "role": "Researcher",
    },
    {
        "username": "marcello",
        "password": generate_password_hash("assas2025"),
        "email": "marcello.savini2@unibo.it",
        "institute": "University of Bologna (Italy)",
        "role": "Researcher",
    },
    {
        "username": "bastien",
        "password": generate_password_hash("assas2025"),
        "email": "bastien.poubeau@asnr.fr",
        "institute": "ASNR (France)",
        "role": "Researcher",
    },
    {
        "username": "joan",
        "password": generate_password_hash("assas2025"),
        "email": "joan.fontanet@ciemat.es",
        "institute": "Ciemat (Spain)",
        "role": "Researcher",
    },
    {
        "username": "gaetan",
        "password": generate_password_hash("assas2025"),
        "email": "blondet@phimeca.com",
        "institute": "Phimeca (France)",
        "role": "Researcher",
    },
    {
        "username": "solenn",
        "password": generate_password_hash("assas2025"),
        "email": "dumont@phimeca.com",
        "institute": "Phimeca (France)",
        "role": "Researcher",
    },
    {
        "username": "albert",
        "password": generate_password_hash("assas2025"),
        "email": "albert.malkhasyan@belv.be",
        "institute": "Bel V (Belgium)",
        "role": "Researcher",
    }
]

# Insert users into the collection
users_collection.delete_many({})  # Clear existing users
users_collection.insert_many(users)

users = users_collection.find()
for user in users:
    logger.info(f"Inserted user: {user['username']} with email: {user['email']} and role: {user['role']}")

logger.info("Users inserted successfully.")