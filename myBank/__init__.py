from flask import Flask, render_template, redirect, url_for
from .Cassandra_client import CassandraClient
from flask_login import LoginManager
from .Account import Account

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cryptbank11'

def create_app():
    app = Flask(__name__, template_folder = 'templates')
    
    # Configurações da aplicação
    app.config.from_object('config.Config')
    
    # Inicialize a conexão com Cassandra
    cassandra_client = CassandraClient()

    # iniciando usuario
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Registrar rotas
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        cassandra_client.close()

    @login_manager.user_loader
    def load_user(account_number):
        return Account.load_user(account_number)
    
    return app