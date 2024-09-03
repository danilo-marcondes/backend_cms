from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.users

    def create_user(self, username, first_name, last_name, country, email, password):
        if self.collection.find_one({'username': username}):
            return None
        hashed_password = generate_password_hash(password)
        user_id = self.collection.insert_one({
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'country': country,
            'email': email,
            'password': hashed_password,
            'max_streams': 3
        }).inserted_id
        return user_id

    def get_user_by_username(self, username):
        return self.collection.find_one({'username': username})

    def get_user_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})

    def verify_user_password(self, username, password):
        user = self.get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            return user
        return None

