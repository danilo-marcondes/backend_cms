from bson import ObjectId
from werkzeug.security import generate_password_hash
import logging

class UserModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.users
        self.logger = logging.getLogger(__name__)

    def create_user(self, first_name, last_name, country, email, password, max_streams):
        
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
            'max_streams': max_streams
        }).inserted_id
        
        return user_id

    def get_user_by_email(self, email):
        return self.collection.find_one({'email': email})

    def get_user_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def update_user_stream_limit(self, user_id, stream_limit):
        
        result = self.collection.update_one({'_id' : ObjectId(user_id)}, {'$set' : {'max_streams': stream_limit}})

        if result.matched_count == 0:
            self.logger.warning(f"Falha ao atualizar limite de streams do usuário: {user_id}")
            return None

        self.logger.info(f"limite de streams atualizado para {stream_limit}. Usuário: {user_id}")

        return result