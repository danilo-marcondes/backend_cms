from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

MAX_STREAMS = 3

class UserModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.users

    def create_user(self, first_name, last_name, country, email, password):
        
        #Procura se o usuário já existe
        if self.collection.find_one({'email': email}):
            return None
        
        #Criptografa a senha
        hashed_password = generate_password_hash(password)
        
        #Insere o novo usuário no BD
        user_id = self.collection.insert_one({
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'country': country,
            'password': hashed_password,
            'max_streams': MAX_STREAMS
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

