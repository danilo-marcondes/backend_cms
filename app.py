import models, stream_manager
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from flasgger import Swagger, swag_from
import threading

app = Flask(__name__)

# Configuração do Swagger
app.config['SWAGGER'] = {
    'title': 'Concurrent Streaming Manager API',
    'uiversion': 3
}
swagger = Swagger(app)

#Carregando variáveis
load_dotenv()

# Configuração do logger
handler = RotatingFileHandler('logs/cms.log', maxBytes=100000, backupCount=1, encoding='UTF-8')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

app.logger.setLevel(logging.INFO)

# Configuração da URI do MongoDB Atlas
app.logger.info("Configurando o BD")
db_user = os.getenv('DB_USERNAME')
db_pass = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_client = MongoClient(f'mongodb+srv://{db_user}:{db_pass}@{db_host}/?retryWrites=true&w=majority')

# Inicialize o BD
app.logger.info("Inicializando o BD")
db_name = os.getenv('DB_NAME')
db_collection = os.getenv('DB_COLLECTION')
db = db_client[db_name]
collection = db[db_collection]

# Verifique se a conexão foi bem-sucedida
try:
    db.command('ping')
    app.logger.info("Conectado ao MongoDB Atlas com sucesso!")
except Exception as e:
    app.logger.error(f"Falha na conexão ao MongoDB Atlas: {e}")
    raise

# Criando de instâncias dos modelos
user_model = models.UserModel(db)
sessions_model = models.SessionsModel(db)


# Criar um dicionário de locks por usuário (Técnica Mutex)
user_locks = {}

def get_user_lock(user_id):
    if user_id not in user_locks:
        user_locks[user_id] = threading.Lock()
    return user_locks[user_id]

#Rota para registrar um novo usuário
@app.route('/user/register', methods=['POST'])
@swag_from('docs/register.yaml')
def register():
    
    data = request.json
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    country = data.get('country')
    password = data.get('password')

    #Valida campos obrigatórios
    if email == None or first_name == None or last_name == None or country == None or password == None:
        app.logger.warn(f"Erro ao tentar registrar novo usuário: {data}")
        return jsonify({'message': 'Invalid data.'}), 400
    
    user_id = user_model.create_user(first_name, last_name, country, email, password)
    
    #Verifica se o usuário já existe
    if not user_id:
        app.logger.warn(f"Erro ao tentar registrar novo usuário. Usuário já existe: {data}")
        return jsonify({"message": "User already exists"}), 400
    
    app.logger.info(f"Usuário registrado com sucesso: {data}")
    return jsonify({"message": "User registered", "user_id": str(user_id)}), 201

@app.route('/user/stream_limit', methods=['PATCH'])
@swag_from('docs/updatestreamlimit.yaml')
def update_user_streams():

    data = request.json
    user_id = data.get('user_id')
    max_streams = data.get('stream_limit')

    # Bloqueia o user para prenivir multiplas atualizações ao mesmo tempo
    user_lock = get_user_lock(user_id)
    with user_lock:
        result = stream_manager.update_stream_limit(user_id=user_id, stream_limit=max_streams, user_model=user_model, stream_model=sessions_model)
        if result[0] == 401:
            app.logger.warn(f'Não foi possível alterar o limite. O novo limite é inferior ao número de streams simultâneos atual. | user_id: {user_id}')

        return jsonify(result[1]), result[0]

@app.route('/start_stream', methods=['POST'])
@swag_from('docs/start.yaml')
def start_stream():
    
    data = request.json
    user_id = data.get('user_id')

    app.logger.info(f"Tentativa de iniciar stream pelo usuário ID: {user_id}")
    
    # Bloqueia o user para prenivir multiplas atualizações ao mesmo tempo
    user_lock = get_user_lock(user_id)
    with user_lock:

        #Inicia stream, modulo stream manager
        result = stream_manager.manage_stream('start', user_id=user_id, user_model=user_model, stream_model=sessions_model)

        if result[0] == 201:
            app.logger.info(f"Stream iniciado com sucesso para o usuário ID: {user_id}, Stream ID: {result[1]['stream_id']}")
        else:
            app.logger.warning(f"Falha ao iniciar stream para o usuário ID: {user_id}")
        
        return jsonify(result[1]), result[0]
    
@app.route('/stop_stream', methods=['POST'])
@swag_from('docs/stop.yaml')
def stop_stream():

    data = request.json
    user_id = data.get('user_id')
    stream_id = data.get('stream_id')

    app.logger.info(f"Tentativa de encerrar stream, usuário ID: {user_id}, streamID: {stream_id}")
    
    # Bloqueia o user para prenivir multiplas atualizações ao mesmo tempo
    user_lock = get_user_lock(user_id)
    with user_lock:

        #Encerra stream, modulo stream manager
        result = stream_manager.manage_stream('stop', user_id=user_id, stream_id=stream_id, user_model=user_model, stream_model=sessions_model)

        if result[0] == 200:
            response = {"message": f"Stream encerrado com sucesso."}
        elif result[0] == 404:
            response = {"message": f"Stream não encontrado."}
        else:
            response = result[1]
        
        return jsonify(response), result[0]


if __name__ == '__main__':
    app.run(debug=True)
