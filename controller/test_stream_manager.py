import pytest
import sys
from unittest.mock import MagicMock, patch

# Mockando o módulo logs antes de importar user_manager
mock_logs = MagicMock()
sys.modules['logs'] = mock_logs

from stream_manager import manage_stream

# Fixtures para criar mocks dos modelos de usuário e stream
@pytest.fixture
def mock_user_model():
    model = MagicMock()
    model.get_user_by_id.return_value = {'id': 1, 'name': 'Test User'}
    return model

@pytest.fixture
def mock_stream_model():
    model = MagicMock()
    model.start_stream.return_value = (1, 0)  # Retorna stream_id e current_streams
    model.stop_stream.return_value = True
    return model

@pytest.fixture
def mock_stream_limit_model():
    model = MagicMock()
    model.start_stream.return_value = (None, 3)  # Retorna stream_id e current_streams
    return model


# Testando manage_stream para o cenário de start com sucesso
def test_manage_stream_start_success(mock_user_model, mock_stream_model):
    data = {'user_id': 1}
    status, response = manage_stream('start', user_model=mock_user_model, stream_model=mock_stream_model, data=data)
    assert status == 201
    assert response['message'] == 'Stream started'
    mock_logs.logger_config.setup_logger.assert_called_once()  # Verifica se o logger foi chamado

# Testando manage_stream para o cenário de start sem sucesso. Limite atingido
def test_manage_stream_start_limit_reached(mock_user_model, mock_stream_limit_model):
    data = {'user_id': 1}
    status, response = manage_stream('start', user_model=mock_user_model, stream_model=mock_stream_limit_model, data=data)
    assert status == 403
    assert response['message'] == 'Stream limit reached'

# Testando manage_stream para o cenário de stop com sucesso
def test_manage_stream_stop_success(mock_user_model, mock_stream_model):
    data = {'stream_id': 1}
    status, response = manage_stream('stop', user_model=mock_user_model, stream_model=mock_stream_model, data=data)
    assert status == 200
    assert 'Stream stopped' in response['message']

# Testando manage_stream para o cenário de stop com stream_id faltando
def test_manage_stream_stop_missing_stream_id(mock_user_model, mock_stream_model):
    data = {}
    status, response = manage_stream('stop', user_model=mock_user_model, stream_model=mock_stream_model, data=data)
    assert status == 400
    assert response['message'] == 'Error. Missing stream_id'
