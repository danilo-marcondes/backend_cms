# database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    db_user = os.getenv('DB_USERNAME')
    db_pass = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    
    db_client = MongoClient(f'mongodb+srv://{db_user}:{db_pass}@{db_host}/?retryWrites=true&w=majority')
    test_db(db_client[db_name])
    
    return db_client[db_name]

def test_db(db):
    # Verifique se a conexão foi bem-sucedida
    try:
        db.command('ping')
        #app.logger.info("Conectado ao MongoDB Atlas com sucesso!")
        print('Conectado ao MongoDB Atlas com sucesso!')
    except Exception as e:
        #app.logger.error(f"Falha na conexão ao MongoDB Atlas: {e}")
        print(f'Falha na conexão ao MongoDB Atlas: {e}')
        raise