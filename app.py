import controller.stream_manager as stream_manager
import controller.user_manager as user_manager

from database import get_db
from logs import logger_config
from model import session, user

from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from

app = Flask(__name__)

# Configuração do Swagger
app.config['SWAGGER'] = {
    'title': 'Concurrent Streaming Manager API',
    'uiversion': 3
}
swagger = Swagger(app)

app_logger = logger_config.setup_logger('app', 'logs/app.log')

app_logger.info("Inicializando o BD")
db = get_db()

# Criando de instâncias dos modelos
user_model = user.UserModel(db)
sessions_model = session.SessionsModel(db)

#Rota para registrar um novo usuário
@app.route('/user/register', methods=['POST'])
@swag_from('docs/register.yaml')
def register():
    
    data = request.json
    app_logger.info(f'/user/register: {data}')

    result = user_manager.register_user(user_model, data)
    app_logger.info(f'/user/register: {result}')
    
    return jsonify(result[1]), result[0]

#Rota para atualizar o limite de streams de um usuário
@app.route('/user/stream_limit', methods=['PATCH'])
@swag_from('docs/updatestreamlimit.yaml')
def update_user_streams():

    data = request.json
    app_logger.info(f'/user/stream_limit: {data}')

    result = user_manager.update_stream_limit(user_model, sessions_model, data)
    app_logger.info(f'/user/stream_limit: {result}')
    
    return jsonify(result[1]), result[0]

#Rota para iniciar um stream
@app.route('/start_stream', methods=['POST'])
@swag_from('docs/start.yaml')
def start_stream():
    
    data = request.json
    app_logger.info(f'/user/start_stream: {data}')

    #Inicia stream, modulo stream manager
    result = stream_manager.manage_stream('start', user_model=user_model, stream_model=sessions_model, data=data)
    
    app_logger.info(f'/user/start_stream: {result}')
    
    return jsonify(result[1]), result[0]

#Rota para encerrar um stream
@app.route('/stop_stream', methods=['POST'])
@swag_from('docs/stop.yaml')
def stop_stream():

    data = request.json
    app_logger.info(f'/user/stop_stream: {data}')
    
    #Encerra stream, modulo stream manager
    result = stream_manager.manage_stream('stop', user_model=user_model, stream_model=sessions_model, data=data)

    app_logger.info(f'/user/stop_stream: {result}')

    return jsonify(result[1]), result[0]


if __name__ == '__main__':
    app.run(debug=True)
