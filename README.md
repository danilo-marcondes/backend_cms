# CMS Básico

## Passos para instalar o projeto:

 Preparando o ambiente virtual e instalando as dependências:<br>
  > python -m venv venv <br>
    source venv/bin/activate  # No Windows use venv\Scripts\activate <br>
    
Instalar dependências<br>
  > pip install -r requirements.txt <br>

Para o banco de dados, está sendo utilizado Atlas MongoDB. Configurar dados do cluster no arquivo .env: <br>

Dados para conexão com o BD <br>
  > DB_USERNAME= <br>
    DB_PASSWORD= <br>
    DB_HOST= <br>

 Dados do cluster <br>
  > DB_NAME=backend_cms <br>
    DB_COLLECTION=users <br>

Executar o app.py: <br>
  > python app.py
