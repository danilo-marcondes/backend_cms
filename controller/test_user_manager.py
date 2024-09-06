import pytest
import sys
from unittest.mock import MagicMock, patch

# Mockando o módulo logs
mock_logs = MagicMock()
sys.modules['logs'] = mock_logs

from user_manager import register_user, update_stream_limit

# Fixture para o modelo de usuário simulado
@pytest.fixture
def mock_user_model():
    model = MagicMock()
    model.get_user_by_email.return_value = None  # Simula que o usuário não existe
    model.create_user.return_value = 1  # Simula a criação do usuário com sucesso
    model.update_user_stream_limit.return_value = True
    return model

# Fixture para o modelo de sessões simulado
@pytest.fixture
def mock_stream_model():
    model = MagicMock()
    model.read_sessions.return_value = 0  # Simula que não há sessões ativas
    return model

def test_register_user_success(mock_user_model):
    data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'country': 'BR',
        'password': 'password123'
    }
    status, response = register_user(user_model=mock_user_model, data=data)
    assert status == 201
    assert response['message'] == 'Usuário registrado'
    mock_user_model.create_user.assert_called_once()

def test_register_user_missing_data(mock_user_model):
    data = {'email': 'test@example.com', 'first_name': 'Test'}
    status, response = register_user(user_model=mock_user_model, data=data)
    assert status == 400
    assert response['message'] == 'Invalid data'

def test_register_user_already_exists(mock_user_model):
    mock_user_model.get_user_by_email.return_value = {'id': 1}
    data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'country': 'BR',
        'password': 'password123'
    }
    status, response = register_user(user_model=mock_user_model, data=data)
    assert status == 400
    assert 'Usuário já existe' in response['message']

def test_update_stream_limit_success(mock_user_model, mock_stream_model):
    data = {'user_id': 1, 'stream_limit': 5}
    status, response = update_stream_limit(user_model=mock_user_model, stream_model=mock_stream_model, data=data)
    assert status == 200
    assert response['message'] == 'limite de streams atualizado'

def test_update_stream_limit_lower_than_active(mock_user_model, mock_stream_model):
    #Define que o limite de streams do usuário atual é 6
    mock_stream_model.read_sessions.return_value = 6
    data = {'user_id': 1, 'stream_limit': 5}
    status, response = update_stream_limit(user_model=mock_user_model, stream_model=mock_stream_model, data=data)
    assert status == 400
    assert 'novo limite é inferior' in response['Message']
