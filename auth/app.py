from flask import Flask, request, jsonify
import jwt
import datetime
import os

app = Flask(__name__)

# Chave JWT (usa variável de ambiente se existir)
JWT_SECRET = os.getenv("JWT_SECRET", "minha_chave_secreta_vinheria")

@app.post("/login")
def login():
    creds = request.get_json()

    username = creds.get("username")
    password = creds.get("password")

    # Simulação de validação
    if username != "admin" or password != "password":
        return jsonify({"error": "credenciais inválidas"}), 401

    # Claims do JWT
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        "role": "user"
    }

    # Gera o token
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token})

if __name__ == "__main__":
    print("auth-service rodando em :8080")
    app.run(host="0.0.0.0", port=8080)
