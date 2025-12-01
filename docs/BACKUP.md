# Sistema de Backups - Cançoner Català

## Estructura
```
~/backups/canconer/
├── scripts/backup-canconer.sh    # Script automàtic
├── daily/                         # Últims 7 dies
├── weekly/                        # Últimes 4 setmanes
├── monthly/                       # Últims 6 mesos
└── backup.log                     # Historial execucions
```

## Contingut dels backups
- Base de dades: `db/canconer.db`
- Configuració Nginx: `nginx/conf.d/`, `nginx/certs/`, `nginx/.htpasswd`
- Servei systemd: `canconer.service`
- Crontab de l'usuari

## Execució automàtica: backup-canconer.sh i auto-commit-bd-sh
Cron diari (3:00 AM):
```bash
# Backup local automàtic (diari/setmanal/mensual) amb rotació
0 3 * * * /home/sergi/backups/canconer/scripts/backup-canconer.sh >> /home/sergi/backups/canconer/backup.log 2>&1
```
Cron diari (4:00 AM) detecta canvis reals a la BD i fa commit automàtic:
```bash
# Executa sqldump + md5sum sobre la BD, compara amb hash anterior
# Si diferent → git commit + push → desencadena hook → backup Google Drive
0 4 * * * ~/backups/canconer/scripts/auto-commit-bd.sh
```
**Logs:**
```bash
tail -f ~/backups/canconer/auto-commit-db.log
```

## Backup manual
```bash
~/backups/canconer/scripts/backup-canconer.sh
```

El fitxer es guardarà a `daily/` amb timestamp.

## Rotació automàtica
- **Diaris:** Es mantenen 7, s'esborra el més antic
- **Setmanals:** Cada diumenge, es mantenen 4
- **Mensuals:** Dia 1 de mes, es mantenen 6

## Verificar backups
```bash
# Llistar contingut
tar -tzf ~/backups/canconer/daily/canconer_*.tar.gz

# Extreure a temporal
mkdir /tmp/test-backup
tar -xzf ~/backups/canconer/daily/canconer_YYYYMMDD_HHMMSS.tar.gz -C /tmp/test-backup

# Verificar BD
sqlite3 /tmp/test-backup/home/sergi/git/projectes/canconer-catala/db/canconer.db "SELECT COUNT(*) FROM bibliografia"
```

## Backup extern

### Backup a Pi-hole (automàtic)

Sincronització diària (5:00 AM) via rsync:
```crontab
0 5 * * * ~/backups/canconer/scripts/backup-to-pihole.sh
```

**Destinació:** `sergi@192.168.1.199:~/backups/raspimarge2-canconer/`

**Logs:**
```bash
tail -f ~/backups/canconer/pihole-sync.log
```

### Sincronització automàtica Google Drive

Cada commit al repositori desencadena backup automàtic a Google Drive via Git hook.

**Configuració:**
- Hook: `.git/hooks/post-commit`
- Script: `~/backups/canconer/scripts/backup-to-gdrive.sh`
- Destinació: `gdrive:Backups/Canconer/`
- Sincronització completa de: `daily/`, `weekly/`, `monthly/`, `scripts/`

**Verificar:**
```bash
rclone ls gdrive:Backups/Canconer/
tail -f ~/backups/canconer/gdrive-sync.log
```

## Restauració
Veure `docs/RESTORE.md`

## Manteniment
```bash
# Veure log
tail -f ~/backups/canconer/backup.log

# Espai utilitzat
du -sh ~/backups/canconer/*

# Últim backup
ls -lht ~/backups/canconer/daily/ | head -2
```
