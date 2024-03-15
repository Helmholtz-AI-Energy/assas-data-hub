
import logging
import pandas
import json
import uuid
import bson

from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson import json_util

logger = logging.getLogger('assas_app')

class User(UserMixin):
    
    def __init__(
        self,
        id,
        username,
        firstname,
        lastname,
        institute,
        password,
        email,
        admin,
        active=True
        ) -> None:
        
        self.id = id
        self._username = username,
        self._firstname = firstname,
        self._lastname = lastname,
        self._institute = institute,
        self._password = password
        self._email = email
        self._admin = admin
        self.active = active
        
    def get_user_document(self):
        
        user_document = {}
        
        user_document['id'] = bson.Binary.from_uuid(self.id)
        user_document['username'] = self._username
        user_document['firstname'] = self._firstname
        user_document['lastname'] = self._lastname
        user_document['institute'] = self._institute
        user_document['password'] = self._password
        user_document['email'] = self._email
        user_document['admin'] =  self._admin
        user_document['active'] = self.active
        
        return user_document
    
    def username(self) -> str:
        
        return self._username
    
    def firstname(self) -> str:
        
        return self._firstname
    
    def lastname(self) -> str:
        
        return self._lastname
    
    def institute(self) -> str:
        
        return self._institute
    
    def password(self) -> str:
        
        return self._password
    
    def email(self) -> str:
        
        return self._email
    
    def admin(self) -> str:
        
        return self._admin
    
    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

class AssasUserManager:

    def __init__(self):
        
        self.client = MongoClient('mongodb://localhost:27017/')

        self.db_handle = self.client['assas']
        self.user_collection = self.db_handle['user']
        #self.drop_user_collection()
        
    def drop_user_collection(self):

        self.user_collection.drop()
        
    def insert_user(self, user: User):
        
        logger.info(f'insert user: {user.get_user_document()}')
        
        self.user_collection.insert_one(user.get_user_document())
        
    def get_user(self, username: str):
        
        return self.user_collection.find_one({'username': username})
    
    def get_user_id(self, id: ObjectId):
        
        return self.user_collection.find_one(ObjectId(id))
    
    def get_user_o(self, username: str) -> User:
        
        user_info = self.user_collection.find_one({'username': username})
        if user_info:
            logger.info(f'found user: {user_info}')
            return User(user_info['id'], user_info['username'], user_info['firstname'], user_info['lastname'], user_info['institute'],user_info['password'],user_info['email'],user_info['admin'])
        else:
            return None    
        
    def update_password(self, username: str, password: str):
        
        user = self.user_collection.find_one({'username': username})
        username = user['username']
        logger.info(f'found user: {username}')
        
        old_password = user['password']
        
        self.user_collection.update_one({'password': old_password}, { "$set": { "password": password } })
        
    @staticmethod
    def parse_json(data):
        return json.loads(json_util.dumps(data))
    
    def get_all_user(self):
        
        users = self.parse_json(self.user_collection.find())
        logger.info(f'get all users {users}')
                
        return users
       
def add_user(username, firstname, lastname, institute, password, email, admin):
    
    logger.info(f'add user ({username} {firstname} {lastname} {institute} {password} {email} {admin})')
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    user = User(uuid.uuid4(), username, firstname, lastname, institute, hashed_password, email, admin)
    
    manager = AssasUserManager()
    manager.insert_user(user)
    
def update_password(username, password):
    
    logger.info(f'update password ({username} {password})')
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    AssasUserManager().update_password(username, hashed_password)

def show_users():

    users = AssasUserManager().get_all_user()
    user_list = []
    i = 0
    for user in users:
        logger.info(f'iterate ({user})')
        user_list.append(
            {
                'username': user['username'],
                'firstname': user['firstname'],
                'lastname': user['lastname'],
                'institute': user['institute'],
                'email': user['email'],
                'admin': user['admin'],
            }
        )
        logger.info(f'iterate list ({user_list[i]})')
        i=i+1

    return user_list

def create_admin_user():
  
    if AssasUserManager().get_user('Admin') is None:
        
        logger.info(f'create admin user')
        add_user('Admin','Jonas','Dressner','SCC','r.adio_1','jonas.dressner@kit.edu','True')
        
    
    else:
        logger.info(f'admin user already created')
