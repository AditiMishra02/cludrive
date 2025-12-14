from flask import Blueprint, request, jsonify
from app.utils.jwt_helper import decode_token
from ..models import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"msg": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    data = decode_token(token)

    if not data:
        return jsonify({"msg": "Invalid or expired token"}), 401

    user = User.query.get(data["user_id"])
    return jsonify({
        "id": user.id,
        "email": user.email
    }), 200
