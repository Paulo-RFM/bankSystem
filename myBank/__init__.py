from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Configurações da aplicação
    app.config.from_object('config.Config')
    
    # Registrar blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
