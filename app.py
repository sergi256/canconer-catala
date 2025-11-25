from flask import Flask, jsonify, Response, render_template, request, redirect, url_for, flash
import json
import random
from config import config
from backend.models import db, Tipus, Bibliografia
from backend.auth import auth

def create_app(config_name='default'):
    """Factory per crear l'aplicació Flask"""
    app = Flask(__name__, template_folder='backend/templates')
    app.config.from_object(config[config_name])
    
    # Força JSON amb UTF-8 sense escapar
    app.config['JSON_AS_ASCII'] = False
    
    # Inicialitzar SQLAlchemy
    db.init_app(app)
    
    # ===== RUTES PÚBLIQUES =====
    
    @app.route('/')
    def index():
        """Pàgina principal amb cerca"""
        # ... (mantén el codi actual sense canvis)
        query = request.args.get('q', '').strip()
        filter_tipus = request.args.get('tipus', '').strip()
        
        total = Bibliografia.query.count()
        stats_query = db.session.query(
            Bibliografia.tipus,
            db.func.count(Bibliografia.id)
        ).group_by(Bibliografia.tipus).all()
        
        stats = {
            'total': total,
            'Cançoner': 0,
            'Folklore': 0,
            'Dansa': 0,
            'Altres': 0
        }
        for tipus, count in stats_query:
            stats[tipus] = count
        
        if query or filter_tipus:
            q = Bibliografia.query
            
            if query:
                search = f'%{query}%'
                q = q.filter(
                    db.or_(
                        Bibliografia.autor.like(search),
                        Bibliografia.titol.like(search),
                        Bibliografia.caracteristiques.like(search)
                    )
                )
            
            if filter_tipus:
                q = q.filter(Bibliografia.tipus == filter_tipus)
            
            registres = q.order_by(Bibliografia.numero).limit(50).all()
        else:
            total_ids = [r.id for r in db.session.query(Bibliografia.id).all()]
            random_ids = random.sample(total_ids, min(10, len(total_ids)))
            registres = Bibliografia.query.filter(Bibliografia.id.in_(random_ids)).all()
        
        return render_template('index.html',
                             stats=stats,
                             registres=registres,
                             query=query,
                             filter_tipus=filter_tipus)
    
    @app.route('/api/registre/<int:id>')
    def api_registre(id):
        """API per obtenir detall d'un registre"""
        registre = Bibliografia.query.get_or_404(id)
        return Response(
            json.dumps(registre.to_dict(), ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8'
        )
    
    # ===== RUTES ADMINISTRACIÓ (PROTEGIDES) =====
    
    @app.route('/gestio/')
    @auth.login_required
    def admin_index():
        """Pàgina principal d'administració amb llistat"""
        query = request.args.get('q', '').strip()
        filter_tipus = request.args.get('tipus', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        # Estadístiques
        total = Bibliografia.query.count()
        stats_query = db.session.query(
            Bibliografia.tipus,
            db.func.count(Bibliografia.id)
        ).group_by(Bibliografia.tipus).all()
        
        stats = {
            'total': total,
            'Cançoner': 0,
            'Folklore': 0,
            'Dansa': 0,
            'Altres': 0
        }
        for tipus, count in stats_query:
            stats[tipus] = count
        
        # Consulta amb filtres
        q = Bibliografia.query
        
        if query:
            search = f'%{query}%'
            q = q.filter(
                db.or_(
                    Bibliografia.autor.like(search),
                    Bibliografia.titol.like(search),
                    Bibliografia.caracteristiques.like(search),
                    Bibliografia.numero.like(search)
                )
            )
        
        if filter_tipus:
            q = q.filter(Bibliografia.tipus == filter_tipus)
        
        # Paginació
        pagination = q.order_by(Bibliografia.numero).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin_index.html',
                             registres=pagination.items,
                             stats=stats,
                             query=query,
                             filter_tipus=filter_tipus,
                             page=page,
                             total_pages=pagination.pages,
                             current_user=auth.current_user())
    
    @app.route('/gestio/nou')
    @auth.login_required
    def admin_nou():
        """Formulari per afegir nou registre"""
        tipus_list = [t.nom for t in Tipus.query.all()]
        return render_template('admin_edit.html',
                             registre=None,
                             tipus_list=tipus_list,
                             current_user=auth.current_user())
    
    @app.route('/gestio/editar/<int:id>')
    @auth.login_required
    def admin_editar(id):
        """Formulari per editar registre existent"""
        registre = Bibliografia.query.get_or_404(id)
        tipus_list = [t.nom for t in Tipus.query.all()]
        return render_template('admin_edit.html',
                             registre=registre,
                             tipus_list=tipus_list,
                             current_user=auth.current_user())
    
    @app.route('/gestio/desar', methods=['POST'])
    @auth.login_required
    def admin_desar():
        """Desar nou registre o actualitzar existent"""
        registre_id = request.form.get('id', type=int)
        
        if registre_id:
            # Actualitzar existent
            registre = Bibliografia.query.get_or_404(registre_id)
        else:
            # Crear nou
            registre = Bibliografia()
            # Generar número automàticament: màxim + 1
            max_numero = db.session.query(db.func.max(Bibliografia.numero)).scalar()
            registre.numero = (max_numero or 0) + 1
        
        # Actualitzar camps (sense numero, que ja està assignat)
        registre.tipus = request.form.get('tipus')
        registre.autor = request.form.get('autor', '').strip() or None
        registre.titol = request.form.get('titol', '').strip()
        registre.caracteristiques = request.form.get('caracteristiques', '').strip() or None
        
        if not registre_id:
            db.session.add(registre)
        
        db.session.commit()
        
        return redirect(url_for('admin_index'))
    
    @app.route('/gestio/esborrar/<int:id>', methods=['POST'])
    @auth.login_required
    def admin_esborrar(id):
        """Esborrar registre"""
        registre = Bibliografia.query.get_or_404(id)
        db.session.delete(registre)
        db.session.commit()
        
        return redirect(url_for('admin_index'))
    
    # ===== RUTES API =====
    
    @app.route('/stats')
    def stats():
        """Estadístiques de la base de dades"""
        total = Bibliografia.query.count()
        per_tipus = db.session.query(
            Bibliografia.tipus,
            db.func.count(Bibliografia.id)
        ).group_by(Bibliografia.tipus).all()
        
        return jsonify({
            'total_registres': total,
            'per_tipus': {tipus: count for tipus, count in per_tipus}
        })
    
    @app.route('/registres')
    def registres():
        """Llista primers 10 registres"""
        registres = Bibliografia.query.limit(10).all()
        data = [r.to_dict() for r in registres]
        return Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8'
        )
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000)
