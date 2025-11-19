from flask import Flask, jsonify, request
import jwt
import os
from functools import wraps

app = Flask(__name__)

# Chave JWT (usa variável de ambiente se existir, mesma do serviço de auth)
JWT_SECRET = os.getenv("JWT_SECRET", "minha_chave_secreta_vinheria")

def require_auth(f):
    """Decorator para verificar autenticação JWT ou permitir acesso interno"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permite bypass de autenticação para chamadas internas entre serviços
        # Verifica se há header X-Internal-Service indicando chamada service-to-service
        if 'X-Internal-Service' in request.headers:
            # Chamada interna entre serviços - permite acesso sem autenticação
            request.current_user = {"sub": "internal_service", "role": "service"}
            return f(*args, **kwargs)
        
        # Para acesso externo, requer autenticação JWT
        token = None
        
        # Verifica se o token está no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Formato esperado: "Bearer <token>"
                token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
            except IndexError:
                return jsonify({"error": "Token inválido no header Authorization"}), 401
        
        if not token:
            return jsonify({"error": "Token de autenticação não fornecido"}), 401
        
        try:
            # Decodifica e valida o token
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            # Adiciona as informações do usuário ao request para uso na função
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/check', methods=['GET'])
@require_auth
def check_inventory():
    response = {
        "item_id": "Vinho-001",
        "available": True,
        "service": "InventoryService",
        "message": "Item is available.",
        "user": request.current_user.get("sub", "unknown")
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)