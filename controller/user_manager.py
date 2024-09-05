from logs import logger_config

#Valor padrão para max streams
MAX_STREAMS = 3

app_logger = logger_config.setup_logger('user_manager', 'logs/user_manager.log')

def register_user(user_model=None, data=None):
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    country = data.get('country')
    password = data.get('password')

    #Verifica se os dados são válidos
    if not user_model:
        app_logger.error(f"Erro ao iniciar stream. Missing dependencies: {data}")
        return 500, {'message': 'Missing dependencies'}
    if not email or not first_name or not last_name or not country or not password:
        app_logger.warn(f"Erro ao tentar registrar novo usuário: {data}")
        return 400, {'message': 'Invalid data'}

    #Verifica se o usuário já existe
    user_exists = user_model.get_user_by_email(email)
    if user_exists:
        app_logger.warn(f"Erro ao tentar registrar novo usuário. Usuário já existe: {data}")
        return 403, {'message': f'Erro ao tentar registrar novo usuário. Usuário já existe: {email}'}
    
    user_id = user_model.create_user(first_name, last_name, country, email, password, MAX_STREAMS)
    if not user_id:
        app_logger.warn(f"Falha ao criar usuário: {data}")
        return 400, {'message': 'Falha ao criar usuário'}
    
    app_logger.info(f"Usuário registrado com sucesso: {data}")
    return 201, {'message': 'Usuário registrado', 'user_id': str(user_id)}


def update_stream_limit(user_model=None, stream_model=None, data=None):
    
    user_id = data.get('user_id')
    stream_limit = data.get('stream_limit')

    #Verifica se os dados são válidos
    if not user_model or not stream_model:
        app_logger.error(f"Erro ao iniciar stream. Missing dependencies: {data}")
        return 500, {'message': 'Missing dependencies'}
    if not user_id or not stream_limit:
        return 400, {'message' : 'Invalid data'}
    
    active_streams = stream_model.read_sessions(user_id)

    if active_streams > stream_limit:
        app_logger.info(f"Não foi possível alterar o limite. O novo limite é inferior ao número de streams simultâneos atual: {user_id}")
        return 400, {'Message' : 'Não foi possível alterar o limite. O novo limite é inferior ao número de streams simultâneos atual.'}
    
    result = user_model.update_user_stream_limit(user_id, stream_limit)
    if not result:
        app_logger.info(f"limite de streams atualizado, max_streams: {stream_limit}, user_id: {user_id}")
        return 400, {'message': 'Falha ao atualizar limite de streams do usuário'}
    return 200, {'message': 'limite de streams atualizado', 'max_streams': stream_limit, 'user_id': user_id}
