from flask import Flask
from config import config

def create_app(config_name='default'):
    """Factory per crear l'aplicació Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Aquí registrarem les rutes més endavant
    
    @app.route('/')
    def index():
        return "Benvingut al Cançoner Català"
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000)
