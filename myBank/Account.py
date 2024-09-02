from .Cassandra_client import CassandraClient
from datetime import datetime
import random
import string
import uuid
from werkzeug.security import check_password_hash, generate_password_hash
from .core_auth import login_core
from flask_login import UserMixin
import requests

bank_id = '206f65e1-a83a-4f35-8885-eaf1ee9b3cf2'
bank_secret = 'T10_P@u!oB@nk#2024$S3cur3'

class Account(UserMixin):
    def __init__(self, account_number, account_holder,email, cpf, telefone, account_password, bank_id,  balance=0.0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.email= email
        self.cpf = cpf
        self.telefone = telefone
        self.account_password = account_password
        bank_id = bank_id
        self.balance = balance
        self.created_at = datetime.now()
    
    def get_id(self):
        return self.account_number

    @staticmethod
    def load_user(email):
        cassandra_client = CassandraClient()
        session = cassandra_client.session
        
        query = "SELECT account_number, account_holder, email, cpf, telefone, account_password, bank_id, balance, created_at FROM accounts WHERE email=%s LIMIT 1 ALLOW FILTERING"
        result = session.execute(query, (email,)).one()

        if result:
            return Account(
                account_number=result.account_number,
                account_holder=result.account_holder,
                email=result.email,
                cpf=result.cpf,
                telefone=result.telefone,
                account_password=result.account_password,
                bank_id=result.bank_id,
                balance=result.balance,
                created_at=result.created_at
            )
        return None



    @staticmethod
    def generate_account_number():
        unique_number = uuid.uuid4().int        
        account_number = str(unique_number)[:6]
        return account_number

    @staticmethod
    def create(account_holder, email, cpf, telefone, account_password, bank_id, initial_deposit):
        account_number = Account.generate_account_number()
        cassandra_client = CassandraClient()
        session = cassandra_client.session
        password = generate_password_hash(account_password)
        session.execute("""
            INSERT INTO accounts (account_number, account_holder,email, cpf, telefone, account_password, bank_id, balance, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (account_number, account_holder,email, cpf, telefone, password, bank_id, initial_deposit, datetime.now()))

    @staticmethod
    def get(email, account_password):
        cassandra_client = CassandraClient()
        session = cassandra_client.session
        
        query = "SELECT * FROM accounts WHERE email=%s ALLOW FILTERING"
        result = session.execute(query, (email,)).one()
        print(result)

        if result:
            stored_password_hash = result.account_password
            if check_password_hash(stored_password_hash, account_password):
                return Account(
                account_number=result.account_number,
                account_holder=result.account_holder,
                account_password=result.account_password,
                balance=result.balance,
                bank_id=result.bank_id,
                cpf=result.cpf,
                email=result.email,
                telefone=result.telefone
            )
            return None
        return None

    @staticmethod
    def update_balance(account_number, new_balance):
        cassandra_client = CassandraClient()
        session = cassandra_client.session
        session.execute("""
            UPDATE accounts SET balance=%s WHERE account_number=%s
        """, (new_balance, account_number))

    @staticmethod
    def get_all():
        cassandra_client = CassandraClient()
        session = cassandra_client.session
        results = session.execute("SELECT * FROM accounts")
        accounts = []
        for row in results:
            account = Account(
                account_number=row.account_number,
                account_holder=row.account_holder,
                account_password=row.account_password,
                balance=row.balance,
                email = row.email,
                cpf = row.cpf,
                telefone = row.telefone,
                bank_id = row.bank_id
            )
            accounts.append(account)
        return accounts

    @staticmethod
    def delete(account_number):
        cassandra_client = CassandraClient()
        session = cassandra_client.session
        session.execute("DELETE FROM accounts WHERE account_number=%s", (account_number,))

    def get_balance(account_number):
        session = CassandraClient().session
        query = "SELECT balance FROM accounts WHERE account_number=%s"
        result = session.execute(query, (account_number,)).one()

        if result:
            return result.balance
        else:
            return 0.0
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def insert_into_keys_accounts(self, account_number, account_name, bank_id, key, created_at):
    # Verifica se o account_number existe na tabela accounts
        result = self.session.execute("""
            SELECT account_number FROM accounts WHERE account_number = %s
        """, (account_number,)).one()
    
        if result is not None:
        # Insere na tabela keys_accounts se o account_number existir
            self.session.execute("""
                INSERT INTO keys_accounts (account_number, account_name, bank_id, key, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (account_number, account_name, bank_id, key, created_at))
            print(f"Chave Pix '{key}' inserida com sucesso para a conta '{account_number}'.")
        else:
            print("O número da conta não existe na tabela de contas.")
    

    @staticmethod
    def get_account(account_number):
        session = CassandraClient().session  

        query = """
            SELECT account_number, account_holder, email, cpf, telefone, account_password, bank_id, balance, created_at
            FROM accounts WHERE account_number=%s LIMIT 1
        """
        result = session.execute(query, (account_number,)).one()

        if result:
            
            return Account(
                account_number=result.account_number,
                account_holder=result.account_holder,
                email=result.email,
                cpf=result.cpf,
                telefone=result.telefone,
                account_password=result.account_password,
                bank_id=result.bank_id,
                balance=result.balance,
                created_at=result.created_at
            )
        else:
            return None 


    def get_pix_keys(account_number):
        session = CassandraClient().session
        query = """
            SELECT pixKey, Key FROM keys_accounts WHERE account_number=%s
        """
        result = session.execute(query, (account_number,))
        return result.all()
    
    def inserir_chave_pix(account_number, bank_id, pixKey, Key):
        print('inserindo chave')
        cassandra_client = CassandraClient()
        session = cassandra_client.session

        insert_query = """
            INSERT INTO keys_accounts (account_number, bank_id, Key, pixKey, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        created_at = datetime.now()
        session.execute(insert_query, (account_number, bank_id, pixKey, Key, created_at))
        print(f"Chave Pix {pixKey} inserida na tabela keys_accounts com sucesso.")

    def criar_usuario_no_core(access_token, account_number, account_holder, email, cpf, telefone):
        url = "https://projetosdufv.live/usuario/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        created_at = datetime.now()
        payload = {
            "usuario_id": account_number,
            "nome": account_holder,
            "email": email,
            "cpf": cpf,
            "telefone": telefone,
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            print("Usuário criado com sucesso.")
            return response.json()  # Retorna os dados do usuário criado, incluindo o `usuario_id`
        else:
            print(f"Erro ao criar usuário: {response.status_code} - {response.text}")
            return None

    def criar_chave_no_core(access_token,account_number, pixKey, Key, ):
         # Lógica para enviar a chave Pix para o banco central (core)
        url = "https://projetosdufv.live/chave_pix"  # Substitua pela URL correta do core  
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "chave_pix": pixKey,
            "tipo_chave": Key,
            "usuario_id": account_number,
            "instituicao_id": bank_id 
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                flash('Chave Pix cadastrada com sucesso no banco central.', 'success')
            else:
                flash('Falha ao cadastrar a chave Pix no banco central.', 'error')
        except requests.exceptions.RequestException as e:
            flash(f'Erro ao comunicar com o banco central: {e}', 'error')
    
    def realizar_transferencia(access_token, chave_pix_destino, valor):
        url = "https://projetosdufv.live/transacao/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "chave_pix": chave_pix_destino,
            "valor": valor
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return True
            else:
                print(f"Erro ao realizar a transferência: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Erro ao tentar se conectar ao core: {e}")
            return False