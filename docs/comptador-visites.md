# Comptador de Visites

## Què fa

Compta visites úniques per dia a la pàgina principal. Cada IP només suma un cop al dia.

## Implementació

### Models (backend/models.py)

**DailyVisit**: Registra IP (hash) + data
- Constraint únic: una IP només una vegada per dia
- Hash SHA-256 de 16 caràcters per privacitat

**Stats**: Comptador total acumulat
- Key: 'unique_daily_visits'
- Value: número total de visites úniques

### Lògica (backend/utils.py)

**register_daily_visit(request)**:
1. Genera hash de la IP
2. Comprova si ja ha visitat avui
3. Si és nova, incrementa comptador
4. Neteja automàtica visites >90 dies
5. Retorna total acumulat

### Visualització

- Pàgina principal: "Aquesta pàgina ha estat visitada 0000001 vegades"
- Format: 7 dígits amb zeros a l'esquerra
- Tipografia: Cormorant Garamond (mateixa que estadístiques)

## Taules de base de dades

```sql
CREATE TABLE daily_visits (
    id INTEGER PRIMARY KEY,
    ip_hash TEXT(16) NOT NULL,
    visit_date DATE NOT NULL,
    UNIQUE(ip_hash, visit_date)
);

CREATE TABLE stats (
    key TEXT PRIMARY KEY,
    value INTEGER DEFAULT 0
);
```

## Privacitat

- No es guarda la IP real, només un hash
- Hash irreversible (SHA-256)
- Neteja automàtica cada 90 dies
- No usa cookies

## Manteniment

Les taules es netegen automàticament. Cap acció necessària.

Per consultar estadístiques manualment:

```python
from backend.models import DailyVisit, Stats
from datetime import date, timedelta

# Total de visites
stats = Stats.query.filter_by(key='unique_daily_visits').first()
print(f"Total: {stats.value}")

# Visites avui
today_count = DailyVisit.query.filter_by(visit_date=date.today()).count()
print(f"Avui: {today_count}")

# Visites aquesta setmana
week_ago = date.today() - timedelta(days=7)
week_count = DailyVisit.query.filter(DailyVisit.visit_date >= week_ago).count()
print(f"Setmana: {week_count}")
```

## Notes tècniques

- Compatible amb proxy invers (Nginx)
- Funciona amb `request.remote_addr`
- Si fas servir proxy, assegura't que passa la IP real via headers
