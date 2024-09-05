from logs import logger_config

app_logger = logger_config.setup_logger('stream_manager', 'logs/stream_manager.log')

def manage_stream(action, user_id=None, stream_id=None, user_model=None, stream_model=None):
    if action == 'start':
        if not user_model or not stream_model:
            app_logger.error(f"Erro ao iniciar stream. Missing dependencies.")
            return 500, {'message': 'Missing dependencies'}
        user = user_model.get_user_by_id(user_id)
        if not user:
            return 404, {'message': 'User not found'}
        stream_id, current_streams = stream_model.start_stream(user_id)
        if not stream_id:
            return 403, {'message': 'Stream limit reached', 'current_streams' : current_streams}
        return 201, {'message': 'Stream started', 'stream_id': str(stream_id), 'current_streams' : current_streams}
    
    elif action == 'stop':
        if not stream_model:
            return 500, {'message': 'Missing dependencies'}
        result = stream_model.stop_stream(stream_id)
        if not result:
            return 404, {'message': 'Stream not found'}
        return 200, {'message': 'Stream stopped'}
    
    return 400, {'message': 'Invalid action'}