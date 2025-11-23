import os

# Directori base del projecte
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuració base de l'aplicació"""
    
    # Clau secreta per sessions (canvia-la en producció!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clau-temporal-desenvolupament'
    
    # Base de dades SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'db', 'canconer.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuració Flask
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Configuració per desenvolupament"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuració per producció"""
    DEBUG = False
    # En producció, assegura't de definir SECRET_KEY com variable d'entorn

# Configuració per defecte
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
