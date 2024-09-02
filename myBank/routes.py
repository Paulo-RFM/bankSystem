# myBank/routes.py
from .Account import Account
from flask import Blueprint, request, jsonify, render_template, redirect, flash, url_for, session, render_template_string
from flask_login import logout_user, login_required, login_user
from .Account import Account
from werkzeug.security import check_password_hash, generate_password_hash
from myBank.LoginForms import LoginForm
from .KeyValidation import verificar_string
from dotenv import load_dotenv
import os
import requests
from .core_auth import login_core

bank_id = '206f65e1-a83a-4f35-8885-eaf1ee9b3cf2'
bank_secret = 'T10_P@u!oB@nk#2024$S3cur3'


bp = Blueprint('main', __name__)

@bp.route('/create_account', methods=['GET', 'POST'])
def create_account():
    
    print(bank_id)
    if request.method == 'POST':
        account_holder = request.form['account_holder']
        account_password = request.form['account_password']
        initial_deposit = float(request.form['initial_deposit'])
        cpf = request.form['cpf']
        email = request.form['email']
        telefone = request.form['telefone']

        Account.create(account_holder, email, cpf, telefone, account_password, bank_id, initial_deposit)
        return redirect(url_for('main.home'))

    return render_template('createAccount.html')
 
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        
        email = form.email.data
        account_password = form.account_password.data

        account = Account.get(email, account_password)

        if account:
            login_user(account)
            session['account_number'] = account.account_number
            session['account_holder'] = account.account_holder
            session['email'] = account.email
            session['cpf'] = account.cpf
            session['telefone'] = account.telefone
            session['balance'] = account.balance

            print('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            print('Invalid account number or password.', 'error')
            return redirect(url_for('main.home'))

    return render_template('login.html', form = form)

'''
@bp.route('/myaccount', methods=['GET', 'POST'])
def my_account(account_number, account_password):

    return render_template('myAccount.html')
'''


@bp.route('/accounts/<account_number>', methods=['GET'])
def get_account(account_number):
    account = Account.get(account_number)
    if account:
        return jsonify({
            'account_number': account.account_number,
            'account_holder': account.account_holder,
            'balance': account.balance,
            'bank_id': account.bank_id,
            'created_at': account.created_at
        })
    else:
        return jsonify({'error': 'Account not found'}), 404

@bp.route('/accounts', methods=['GET'])
def get_all_accounts():
    accounts = Account.get_all()
    return jsonify([{
        'account_number': account.account_number,
        'account_holder': account.account_holder,
        'email': account.email,
        'cpf': account.cpf,
        'telefone': account.telefone,
        'account_password': account.account_password,
        'balance': account.balance,
        'created_at': account.created_at,
        'is_active': account.is_active
    } for account in accounts])


@bp.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        chave_pix_destino = request.form.get('chave_pix_destino')
        valor = float(request.form.get('valor'))
        account_number = session.get('account_number')

        # Validar os dados da transferência
        if not chave_pix_destino or not valor or valor <= 0:
            flash('Dados inválidos. Verifique a chave Pix e o valor.', 'error')
            return redirect(url_for('main.transfer'))

        # Obter o token de autenticação
        access_token = login_core()
        if not access_token:
            flash('Erro na autenticação com o core.', 'error')
            return redirect(url_for('main.transfer'))

        # Realizar a transferência no core
        transfer_success = Account.realizar_transferencia(access_token, chave_pix_destino, valor)

        if transfer_success:
            flash('Transferência realizada com sucesso.', 'success')
            current_balance = Account.get_balance(account_number)
            new_balance = current_balance - valor
            Account.update_balance(account_number, new_balance)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Erro ao realizar a transferência.', 'error')
            return redirect(url_for('main.transfer'))

    return render_template('transfer.html')


def render_home():
    return render_template('home.html')

@bp.route('/home')
def home():
    return render_home()

@bp.route('/')
def index():
    return render_home()

@bp.route('/logout')
def logout():
    session.pop('account_number', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.logout'))


@bp.route('/dashboard')
def dashboard():
    print("Entrando na rota do dashboard")
    account_number = session.get('account_number')
    account_holder = session.get('account_holder')
    balance = session.get('balance')
    
    
    pix_keys = Account.get_pix_keys(account_number)
    print(pix_keys)
    return render_template('dashboard.html', 
                           account_number=account_number, 
                           account_holder=account_holder,
                           balance=balance, 
                           pix_keys=pix_keys)

@bp.route('/registerkey', methods=['GET', 'POST'])

def registerkey():
    if request.method == 'POST':
        account_holder = session.get('account_holder')
        email = session.get('email')
        cpf = session.get('cpf')
        telefone = session.get('telefone')
        pix_key = request.form.get('pixKey')
        account_number = session.get('account_number')
        bank_id = session.get('bank_id')  # Certifique-se de que bank_id está na sessão

        # Validação usando a função importada
        is_valid, chave_tipo = verificar_string(pix_key)
        if not pix_key or not is_valid:
            flash('A chave Pix é inválida. Por favor, insira um CPF, e-mail ou telefone válido.', 'error')
            return redirect(url_for('main.registerkey'))
        
        access_token = login_core()
        print('aquiiii '+ access_token)
               
        # Obtenção do token de autenticação
        if not access_token:
            flash('Erro na autenticação com o core.', 'error')
            return redirect(url_for('main.registerkey'))

        #criar Usuario no Core
        Account.criar_usuario_no_core(access_token,account_number, account_holder, email, cpf, telefone)

         # Inserir a chave Pix no banco de dados local
        Account.inserir_chave_pix(account_number, bank_id, pix_key, chave_tipo)
        
        return redirect(url_for('main.dashboard'))

    account_holder = session.get('account_holder')
    balance = session.get('balance')

    return render_template('registerkey.html', account_holder=account_holder, balance=balance)