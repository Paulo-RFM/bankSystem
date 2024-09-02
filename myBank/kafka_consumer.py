from kafka import KafkaConsumer
import json
from config import KAFKA_BOOTSTRAP_SERVERS
from myBank.Account import CassandraClient

class KafkaConsumerClient:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'transactions',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.cassandra_client = CassandraClient()

    def consume(self):
        for message in self.consumer:
            self.process_message(message.value)

    def process_message(self, message):
        if message['type'] == 'deposit':
            self.cassandra_client.execute(
                "UPDATE accounts SET balance = balance + %s WHERE account_number = %s",
                (message['amount'], message['account_number'])
            )
        elif message['type'] == 'withdraw':
            self.cassandra_client.execute(
                "UPDATE accounts SET balance = balance - %s WHERE account_number = %s",
                (message['amount'], message['account_number'])
            )
