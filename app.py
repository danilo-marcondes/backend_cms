from flask import Flask, request, jsonify
from pymongo import MongoClient
from models import UserModel
from dotenv import load_dotenv
import os

app = Flask(__name__)

#Carregando variáveis
load_dotenv()

# Configuração da URI do MongoDB Atlas
db_user = os.getenv('DB_USERNAME')
db_pass = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_client = MongoClient(f'mongodb+srv://{db_user}:{db_pass}@{db_host}/?retryWrites=true&w=majority')

# Inicialize o PyMongo
db_name = os.getenv('DB_NAME')
db_collection = os.getenv('DB_COLLECTION')
db = db_client[db_name]
collection = db[db_collection]

# Verifique se a conexão foi bem-sucedida
try:
    db.command('ping')
    print("Conectado ao MongoDB Atlas com sucesso!")
except Exception as e:
    print("Falha na conexão ao MongoDB Atlas:", e)
    #ToDo: Registrar Falha
    raise

# Criando de instâncias dos modelos
user_model = UserModel(db)

#Rota para registrar um novo usuário
@app.route('/register', methods=['POST'])
def register():
    
    data = request.json
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    country = data.get('country')
    password = data.get('password')

    #Valida campos obrigatórios
    if email == None or first_name == None or last_name == None or country == None or password == None:
        return jsonify({'message': 'Invalid data.'}), 400
    
    user_id = user_model.create_user(first_name, last_name, country, email, password)
    
    #Verifica se o usuário já existe
    if not user_id:
        return jsonify({"message": "User already exists"}), 400
    
    return jsonify({"message": "User registered", "user_id": str(user_id)}), 201




if __name__ == '__main__':
    app.run(debug=True)
