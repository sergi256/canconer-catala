# Guia de Restauració - Cançoner Català

## Pre-requisits
- Raspberry Pi amb Raspbian 12
- Accés root/sudo
- Backup descarregat a `/tmp/restore/`
- **Configuració del servidor:** Veure `~/server-config/SETUP.md` per configuració base del sistema.

## 1. Instal·lació base
```bash
sudo apt update
sudo apt install git podman nginx docker.io certbot
```

## 2. Restaurar repositori
```bash
cd ~
mkdir -p git/projectes
cd git/projectes
git clone https://github.com/sergi256/canconer-catala.git
cd canconer-catala
```

## 3. Extreure backup
```bash
cd /tmp/restore
tar -xzf canconer_YYYYMMDD_HHMMSS.tar.gz
```

## 4. Restaurar fitxers
```bash
# Base de dades
cp /tmp/restore/home/sergi/git/projectes/canconer-catala/db/canconer.db \
   ~/git/projectes/canconer-catala/db/

# Nginx
sudo mkdir -p /home/sergi/nginx
sudo cp -r /tmp/restore/home/sergi/nginx/* /home/sergi/nginx/
sudo chown -R sergi:sergi /home/sergi/nginx

# Systemd
sudo cp /tmp/restore/etc/systemd/system/canconer.service \
   /etc/systemd/system/

# Crontab
crontab /tmp/restore/tmp/crontab-sergi.txt
```

## 5. Construir imatge Podman
```bash
cd ~/git/projectes/canconer-catala
podman build -t canconer-catala:latest .
```

## 6. Configurar DuckDNS
- Crear/actualitzar `canconer-catala.duckdns.org` → nova IP
- Configurar port forwarding router: 80, 443 → Raspberry Pi

## 7. Generar certificats SSL (margenat.duckdns.org i canconer-catala.duckdns.org)
```bash
# Aturar Nginx Docker si existeix
docker stop my-nginx

# Margenat
sudo docker run --rm -it \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  -p 80:80 -p 443:443 \
  certbot/certbot certonly --standalone \
  -d margenat.duckdns.org \
  --email TU_EMAIL \
  --agree-tos

# Canconer
sudo docker run --rm -it \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  -p 80:80 -p 443:443 \
  certbot/certbot certonly --standalone \
  -d canconer-catala.duckdns.org \
  --email TU_EMAIL \
  --agree-tos

# Copiar certificats a ubicació genèrica
mkdir -p ~/ssl-certs/{margenat,canconer}
sudo cp /etc/letsencrypt/live/margenat.duckdns.org/fullchain.pem ~/ssl-certs/margenat/
sudo cp /etc/letsencrypt/live/margenat.duckdns.org/privkey.pem ~/ssl-certs/margenat/
sudo cp /etc/letsencrypt/live/canconer-catala.duckdns.org/fullchain.pem ~/ssl-certs/canconer/
sudo cp /etc/letsencrypt/live/canconer-catala.duckdns.org/privkey.pem ~/ssl-certs/canconer/
```

## 8. Configurar Nginx Docker
```bash
# Verificar mounts correctes al contenidor my-nginx
docker inspect my-nginx | grep Mounts

# Si no existeix, crear amb:
docker run -d --name my-nginx \
  -p 80:80 -p 443:443 \
  -v /etc/nginx/certs:/etc/nginx/certs:ro \
  -v /home/sergi/nginx/conf.d:/etc/nginx/conf.d:ro \
  -v /home/sergi/nginx/html:/usr/share/nginx/html:ro \
  -v /home/sergi/nginx/.htpasswd:/etc/nginx/.htpasswd:ro \
  nginx

# Si existeix, reiniciar
docker start my-nginx
```

## 9. Iniciar serveis

### Configurar user service
```bash
mkdir -p ~/.config/systemd/user
cp ~/git/projectes/canconer-catala/docs/canconer.service.example ~/.config/systemd/user/canconer.service

# Habilitar linger (autostart)
sudo loginctl enable-linger sergi

# Activar servei
systemctl --user daemon-reload
systemctl --user enable canconer.service
systemctl --user start canconer.service
```

## 10. Verificació
```bash
# Local
curl http://localhost:5001
curl https://canconer-catala.duckdns.org

# Logs
podman logs canconer
docker logs my-nginx
sudo journalctl -u canconer.service -f
```

## Notes
- Certificats SSL caduquen cada 90 dies (renovar amb certbot)
- Backups automàtics: `~/backups/canconer/`
- Permisos BD: `chmod 664 db/canconer.db`
