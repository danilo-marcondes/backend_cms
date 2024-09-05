import stream_manager
import threading
from model import session, user
from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
from database import get_db
from controller import user_manager
from logs import logger_config

app = Flask(__name__)

# Configuração do Swagger
app.config['SWAGGER'] = {
    'title': 'Concurrent Streaming Manager API',
    'uiversion': 3
}
swagger = Swagger(app)

app_logger = logger_config.setup_logger('logs/app.log')

app_logger.info("Inicializando o BD")
db = get_db()

# Criando de instâncias dos modelos
user_model = user.UserModel(db)
sessions_model = session.SessionsModel(db)

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
    app_logger.info(f'/user/register: {request.json}')
    data = request.json
    result = user_manager.register_user(user_model, data)
    app_logger.info(f'/user/register: {result}')
    return jsonify(result[1]), result[0]

#Rota para atualizar o limite de streams de um usuário
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

#Rota para iniciar um stream
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

#Rota para encerrar um stream
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
