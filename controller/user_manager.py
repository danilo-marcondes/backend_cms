# user_manager.py
def register_user(user_model, data):
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    country = data.get('country')
    password = data.get('password')

    #Verifica se os dados são válidos
    if not email or not first_name or not last_name or not country or not password:
        #app.logger.warn(f"Erro ao tentar registrar novo usuário: {data}")
        return 400, {'message': 'Invalid data'}

    user_id = user_model.create_user(first_name, last_name, country, email, password)
    #Verifica se o usuário já existe
    if not user_id:
        #app.logger.warn(f"Erro ao tentar registrar novo usuário. Usuário já existe: {data}")
        return 400, {'message': 'User already exists'}

    #app.logger.info(f"Usuário registrado com sucesso: {data}")
    return 201, {'message': 'User registered', 'user_id': str(user_id)}

def update_stream_limit(user_id, max_streams, user_model, sessions_model):
    active_streams = sessions_model.read_sessions(user_id)
    if active_streams > max_streams:
        return 400, {'message': 'New limit is lower than active streams'}
    
    result = user_model.update_user_stream_limit(user_id, max_streams)
    if not result:
        return 400, {'message': 'Failed to update stream limit'}
    return 200, {'message': 'Stream limit updated'}

