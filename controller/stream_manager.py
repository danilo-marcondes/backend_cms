from logs import logger_config

app_logger = logger_config.setup_logger('stream_manager', 'logs/stream_manager.log')

def manage_stream(action, stream_id=None, user_model=None, stream_model=None, data=None):

    user_id = data.get('user_id')
    stream_id = data.get('stream_id')

    if not user_model or not stream_model:
        app_logger.error(f"Erro ao iniciar stream. Missing dependencies.")
        return 500, {'message': 'Missing dependencies'}
    
    if action == 'start':
        
        if not user_id:
            app_logger.warn(f"Erro ao iniciar stream. Falta user_id: {data}")
            return 404, {'message': 'Missing user_id'}
    
        user = user_model.get_user_by_id(user_id)
        if not user:
            app_logger.warn(f"User not found: {user_id}")
            return 404, {'message': f'User not found: {user_id}'}
        
        stream_id, current_streams = stream_model.start_stream(user_id)
        if not stream_id:
            app_logger.warn(f"Stream limit reached, current_streams: {current_streams} for user_id: {user_id}")
            return 403, {'message': 'Stream limit reached', 'current_streams' : current_streams}
        
        app_logger.info(f"Stream started, stream_id: {str(stream_id)} for user_id: {user_id}, 'current_streams' : {current_streams}")
        return 201, {'message': 'Stream started', 'stream_id': str(stream_id), 'current_streams' : current_streams}
    
    elif action == 'stop':
        
        if not stream_id:
            app_logger.warn(f"Erro ao encerrar stream. Falta stream_id: {data}")
            return 400, {'message': 'Error. Missing stream_id'}
        
        result = stream_model.stop_stream(stream_id)
        if not result:
            app_logger.warn(f"Stream não encontrado stream_id: {stream_id}")
            return 404, {'message': 'Stream not found or already stopped.'}

        app_logger.warn(f"Stream encerrado stream_id: {stream_id}")
        return 200, {'message': f'Stream stopped: {stream_id}'}
    
    app_logger.warn(f"Ação inválida em manage_stream: action={action} | {data}")
    return 400, {'message': 'Invalid action'}