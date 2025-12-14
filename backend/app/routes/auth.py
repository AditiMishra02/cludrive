from flask import Blueprint, request, jsonify
from ..models import db, User, bcrypt
from app.utils.jwt_helper import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 400

    # Hash password
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create user
    user = User(email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Check password
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Incorrect password"}), 401

    # Generate JWT token
    token = generate_token(user.id)

    return jsonify({"msg": "Login successful", "token": token}), 200

