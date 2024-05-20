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
                account_number UUID PRIMARY KEY,
                account_holder TEXT,
                balance DOUBLE
            )
        """)

    def execute(self, query, parameters=None):
        if parameters:
            return self.session.execute(query, parameters)
        return self.session.execute(query)
