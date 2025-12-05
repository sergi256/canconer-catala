"""
Utilitats per l'aplicació Cançoner Català
"""
import hashlib
from datetime import date, timedelta
from backend.models import db, DailyVisit, Stats


def register_daily_visit(request):
    """
    Registra una visita única per IP i dia.
    Cada IP només compta una vegada per dia.
    
    Args:
        request: Objecte Flask request
        
    Returns:
        int: Total de visites úniques acumulades
    """
    # Hash de la IP per privacitat (només guardem 16 caràcters)
    ip = request.remote_addr
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
    today = date.today()
    
    # Comprovar si aquesta IP ja ha visitat avui
    existing = DailyVisit.query.filter_by(
        ip_hash=ip_hash,
        visit_date=today
    ).first()
    
    if not existing:
        # Nova visita avui, registrar-la
        new_visit = DailyVisit(ip_hash=ip_hash, visit_date=today)
        db.session.add(new_visit)
        
        # Incrementar comptador total
        stats = Stats.query.filter_by(key='unique_daily_visits').first()
        if stats:
            stats.value += 1
        else:
            stats = Stats(key='unique_daily_visits', value=1)
            db.session.add(stats)
        
        db.session.commit()
    
    # Obtenir total de visites
    stats = Stats.query.filter_by(key='unique_daily_visits').first()
    total = stats.value if stats else 0
    
    # Neteja automàtica: eliminar visites de més de 90 dies
    cleanup_old_visits()
    
    return total


def cleanup_old_visits(days=90):
    """
    Elimina visites més antigues que X dies per mantenir la BD neta.
    
    Args:
        days: Número de dies a mantenir (per defecte 90)
    """
    cutoff_date = date.today() - timedelta(days=days)
    DailyVisit.query.filter(DailyVisit.visit_date < cutoff_date).delete()
    db.session.commit()


def get_visit_stats():
    """
    Obté estadístiques de visites.
    
    Returns:
        dict: Diccionari amb estadístiques
    """
    stats = Stats.query.filter_by(key='unique_daily_visits').first()
    total = stats.value if stats else 0
    
    # Visites avui
    today = date.today()
    today_count = DailyVisit.query.filter_by(visit_date=today).count()
    
    # Visites aquesta setmana
    week_ago = today - timedelta(days=7)
    week_count = DailyVisit.query.filter(
        DailyVisit.visit_date >= week_ago
    ).count()
    
    # Visites aquest mes
    month_ago = today - timedelta(days=30)
    month_count = DailyVisit.query.filter(
        DailyVisit.visit_date >= month_ago
    ).count()
    
    return {
        'total': total,
        'today': today_count,
        'week': week_count,
        'month': month_count
    }
