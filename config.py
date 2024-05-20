class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///client_bank.db'
    KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
    CASSANDRA_CLUSTER = ['127.0.0.1']

