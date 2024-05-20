from flask import Blueprint, request, jsonify
from uuid import uuid4
from models import CassandraClient
from kafka_producer import KafkaProducerClient

bp = Blueprint('main', __name__)
cassandra_client = CassandraClient()
kafka_producer = KafkaProducerClient()

@bp.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    account_number = uuid4()
    account_holder = data['account_holder']
    initial_deposit = data.get('initial_deposit', 0.0)

    cassandra_client.execute(
        "INSERT INTO accounts (account_number, account_holder, balance) VALUES (%s, %s, %s)",
        (account_number, account_holder, initial_deposit)
    )

    return jsonify({
        'account_number': str(account_number),
        'account_holder': account_holder,
        'balance': initial_deposit
    }), 201

@bp.route('/accounts/<account_number>', methods=['DELETE'])
def delete_account(account_number):
    cassandra_client.execute(
        "DELETE FROM accounts WHERE account_number = %s",
        (account_number,)
    )
    return '', 204

@bp.route('/accounts/<account_number>/deposit', methods=['POST'])
def deposit(account_number):
    data = request.get_json()
    amount = data['amount']

    kafka_producer.send('transactions', {
        'type': 'deposit',
        'account_number': account_number,
        'amount': amount
    })

    return '', 204

@bp.route('/accounts/<account_number>/withdraw', methods=['POST'])
def withdraw(account_number):
    data = request.get_json()
    amount = data['amount']

    kafka_producer.send('transactions', {
        'type': 'withdraw',
        'account_number': account_number,
        'amount': amount
    })

    return '', 204
