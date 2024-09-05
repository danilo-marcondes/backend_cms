from bson import ObjectId
import logging


class SessionsModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.sessions
        self.logger = logging.getLogger(__name__)

    def read_sessions(self, user_id):
        
        #Retorna a quantidade de sessões do usuário
        active_streams = self.collection.count_documents({'user_id': ObjectId(user_id), 'active': True})
        if active_streams == None:
            active_streams = 0
        print(f'Active streams: {active_streams} | user: {user_id}')
        return active_streams
    
    def start_stream(self, user_id):

        active_streams = self.read_sessions(user_id)

        user = self.db.users.find_one({'_id': ObjectId(user_id)})
        if not user or active_streams >= user['max_streams']:
            self.logger.warning(f"Falha ao iniciar stream: Limite de streams atingido ou usuário inválido. User ID: {user_id}")
            return None, active_streams
        
        stream_id = self.collection.insert_one({'user_id': ObjectId(user_id), 'active': True}).inserted_id
        current_streams = active_streams + 1
        self.logger.info(f"Stream iniciado com sucesso: Stream ID: {stream_id}, User ID: {user_id}, Current Streams: {current_streams}")

        return stream_id, current_streams

    def stop_stream(self, stream_id):

        steam_is_active = self.collection.find_one({'_id': ObjectId(stream_id), 'active' : True})
        
        if steam_is_active != None:
            result = self.collection.update_one({'_id': ObjectId(stream_id)}, {'$set': {'active': False}})
        
            if result.matched_count == 0:
                self.logger.warning(f"Falha ao parar stream. Stream ID: {stream_id}")
                return None
            
            self.logger.info(f"Stream parado com sucesso: Stream ID: {stream_id}")
            return result
        
        self.logger.warning(f"Falha ao parar stream: Stream não encontrado ou já parado. Stream ID: {stream_id}")
        return None

