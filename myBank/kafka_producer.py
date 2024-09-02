from kafka import KafkaProducer
import json

class KafkaProducerClient:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers='127.0.0.1:9092',
            api_version=(0,11,5),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send(self, topic, value):
        self.producer.send(topic, value)
        self.producer.flush()
