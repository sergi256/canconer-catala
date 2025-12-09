# Monitorització

## Sistema

**Script**: `/home/sergi/server-config/scripts/check-services.sh`  
**Cron**: Cada 10 minuts  
**Email**: sergi256@gmail.com via msmtp

## Política d'emails

1. **Primera caiguda**: Email immediatament
2. **Si reinicia**: Email "Reiniciat correctament"
3. **Si NO reinicia**: Email "CRÍTIC - No reinicia"
4. **Caigudes successives**:
   - Dies 0-6: màxim 1 email/dia
   - A partir dia 7: màxim 1 email/setmana

## Estat

**Fitxer**: `/tmp/canconer_alert_state`
- Existeix mentre el servei està caigut
- S'esborra quan es recupera
- Conté: timestamp primera caiguda, últim email, comptador

## Variables d'entorn necessàries

```bash
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"
```

Necessàries perquè el cron pugui usar `systemctl --user`.

## Log

`/home/sergi/server-config/monitor.log`
