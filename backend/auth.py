from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

auth = HTTPBasicAuth()

# Usuaris i contrasenyes (hash generat amb generate_password_hash)
# Contrasenya per defecte: "canconer2024" (canvia-la després!)
users = {
    "admin": "scrypt:32768:8:1$lZMYWcZUqDBCBShX$f15073cb5c1f1a37fc5cc1d6c109082dcdc671cca1f0493549e1b456327485788fb56979c64a44d6484b603dc50669da24710b7c8caa1d54779e76326ec43ba7"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None
