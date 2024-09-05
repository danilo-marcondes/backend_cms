# CMS Básico

### Passos para instalar o projeto ###
O Concurrent Streaming Manager (CSM) é um módulo essencial em sistemas de streaming,
responsável por controlar a quantidade de streams simultâneos a que um usuário tem
acesso.

 Preparando o ambiente virtual e instalando as dependências:<br>
  ```
    python -m venv venv
    source venv/bin/activate  # No Windows use venv\Scripts\activate
  ``` 
    
Instalar dependências<br>
  ```
    pip install -r requirements.txt
  ```

Para o banco de dados, está sendo utilizado Atlas MongoDB. Configurar dados do cluster no arquivo .env: <br>

### Dados para conexão com o BD ###
  ```
    DB_USERNAME=
    DB_PASSWORD=
    DB_HOST=
  ```

 Dados do cluster
  ```
    DB_NAME=backend_cms
  ```

Executar o app.py:
  ```
    python app.py
  ```

Swagger:
 ```
    http://localhost:5000/apidocs/
 ```
