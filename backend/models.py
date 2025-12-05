from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Tipus(db.Model):
    """Model per la taula tipus"""
    __tablename__ = 'tipus'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relació amb Bibliografia
    bibliografies = db.relationship('Bibliografia', backref='tipus_rel', lazy=True)
    
    def __repr__(self):
        return f'<Tipus {self.nom}>'


class Bibliografia(db.Model):
    """Model per la taula bibliografia"""
    __tablename__ = 'bibliografia'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    tipus = db.Column(db.String(50), db.ForeignKey('tipus.nom'))
    autor = db.Column(db.Text)
    titol = db.Column(db.Text)
    caracteristiques = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Bibliografia #{self.numero}: {self.titol}>'
    
    def to_dict(self):
        """Converteix el registre a diccionari per JSON"""
        return {
            'id': self.id,
            'numero': self.numero,
            'tipus': self.tipus,
            'autor': self.autor,
            'titol': self.titol,
            'caracteristiques': self.caracteristiques
        }


class DailyVisit(db.Model):
    """Model per registrar visites úniques per dia"""
    __tablename__ = 'daily_visits'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_hash = db.Column(db.String(16), nullable=False)
    visit_date = db.Column(db.Date, nullable=False, default=date.today)
    
    # Índex únic per evitar duplicats (una IP només compta una vegada per dia)
    __table_args__ = (
        db.UniqueConstraint('ip_hash', 'visit_date', name='unique_daily_visit'),
    )
    
    def __repr__(self):
        return f'<DailyVisit {self.ip_hash[:8]}... on {self.visit_date}>'


class Stats(db.Model):
    """Model per guardar estadístiques diverses"""
    __tablename__ = 'stats'
    
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'<Stats {self.key}: {self.value}>'
