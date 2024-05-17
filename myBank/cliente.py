from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///client_bank.db'
db = SQLAlchemy(app)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_holder = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)

@app.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    new_account = Account(
        account_number=data['account_number'],
        account_holder=data['account_holder'],
        balance=data.get('initial_deposit', 0.0)
    )
    db.session.add(new_account)
    db.session.commit()
    return jsonify({
        'account_number': new_account.account_number,
        'account_holder': new_account.account_holder,
        'balance': new_account.balance,
        'created_at': new_account.created_at
    }), 201


@app.route('/accountsAll', methods=['GET'])
def get_accounts():
    accounts = Account.query.all()
    return jsonify([{
        'account_number': account.account_number,
        'account_holder': account.account_holder,
        'balance': account.balance,
        'created_at': account.created_at
    } for account in accounts])


@app.route('/accounts/<account_number>', methods=['GET'])
def get_account(account_number):
    account = Account.query.filter_by(account_number=account_number).first_or_404()
    return jsonify({
        'account_number': account.account_number,
        'account_holder': account.account_holder,
        'balance': account.balance,
        'created_at': account.created_at
    })

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    sender_account = Account.query.filter_by(account_number=data['sender']).first_or_404()
    receiver_account_number = data['receiver']
    amount = data['amount']

    if sender_account.balance < amount:
        return jsonify({'error': 'Insufficient funds'}), 400

    # Communicate with Central Bank
    response = requests.post('http://<192.168.100.15>:5000/transaction', json={
        'sender': sender_account.account_number,
        'receiver': receiver_account_number,
        'amount': amount
    })

    if response.status_code == 201:
        sender_account.balance -= amount
        db.session.commit()
        return jsonify(response.json()), 201
    else:
        return jsonify(response.json()), response.status_code
    
@app.route('/')
def home():
    return "Welcome to the bank API!"

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
