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

## Execució automàtica
Cron diari a les 3:00 AM:
```bash
crontab -l  # Veure configuració actual
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

## Backup extern recomanat
Còpia setmanal a ubicació externa:
```bash
# USB/Disc extern
cp -r ~/backups/canconer /media/usb/

# Rsync a NAS/servidor remot
rsync -avz ~/backups/canconer/ user@nas:/backups/canconer/

# Cloud (rclone)
rclone sync ~/backups/canconer/ remote:canconer-backups/
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
