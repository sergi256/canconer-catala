from flask_sqlalchemy import SQLAlchemy

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
