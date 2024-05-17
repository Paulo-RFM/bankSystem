from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank_system.db'
db = SQLAlchemy(app)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_holder = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    receiver = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp
        }

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

@app.route('/accounts/<account_number>', methods=['GET'])
def get_account(account_number):
    account = Account.query.filter_by(account_number=account_number).first_or_404()
    return jsonify({
        'account_number': account.account_number,
        'account_holder': account.account_holder,
        'balance': account.balance,
        'created_at': account.created_at
    })

@app.route('/transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    sender_account = Account.query.filter_by(account_number=data['sender']).first_or_404()
    receiver_account = Account.query.filter_by(account_number=data['receiver']).first_or_404()

    if sender_account.balance < data['amount']:
        return jsonify({'error': 'Insufficient funds'}), 400

    sender_account.balance -= data['amount']
    receiver_account.balance += data['amount']

    new_transaction = Transaction(
        sender=data['sender'],
        receiver=data['receiver'],
        amount=data['amount']
    )
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify(new_transaction.to_dict()), 201

@app.route('/transactions', methods=['GET'])
def list_transactions():
    transactions = Transaction.query.all()
    return jsonify([transaction.to_dict() for transaction in transactions])

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
