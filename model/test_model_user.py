import pytest
from unittest.mock import patch, MagicMock
import user

def test_create_user(mock_db):
    
    mock_collection = mock_db.__getitem__.return_value

    # Chama a função que queremos testar
    user.UserModel.create_user(mock_db, 'teste', 'abc', 'br', 'teste1234@teste.com.br', 'senha123')

    mock_collection.insert_one.assert_called_once_with({"email": "teste1234@teste.com.br"})

