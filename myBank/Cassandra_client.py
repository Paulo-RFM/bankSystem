from cassandra.cluster import Cluster

class CassandraClient:
    def __init__(self):
        self.cluster = Cluster(['127.0.0.1'])
        self.session = self.cluster.connect()
        self.session.execute(f"CREATE KEYSPACE IF NOT EXISTS {'mykeyspace'} WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}")
        self.session.set_keyspace('mykeyspace')
        self.create_tables()

    def create_tables(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                account_holder TEXT,
                email TEXT,
                cpf TEXT,
                telefone TEXT,
                account_password TEXT,
                bank_id TEXT,
                balance FLOAT,
                created_at TIMESTAMP
            )
        """)

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS keys_accounts (  
                pixKey TEXT,
                Key TEXT,
                account_number TEXT PRIMARY KEY,
                bank_id TEXT,
                created_at TIMESTAMP
            )
        """)


    def execute(self, query, parameters=None):
        if parameters:
            return self.session.execute(query, parameters)
        return self.session.execute(query)

    def close(self):
        self.session.shutdown()
        self.cluster.shutdown()
