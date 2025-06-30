# app/auth.py or app/auth/routes.py

from flask import Blueprint, request, jsonify
from app import db, bc
from app.models import User
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # ✅ Get role from request and validate
    role = data.get("role", "user")
    if role not in ["user", "admin"]:
        role = "user"

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    # Hash the password and create the user
    hashed_pw = bc.generate_password_hash(password).decode("utf-8")
    user = User(username=username, password_hash=hashed_pw, role=role)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and bc.check_password_hash(user.password_hash, password):
        token = create_access_token(identity=user.id)
        return jsonify({"access_token": token, "username": user.username, "role": user.role})
    return jsonify({"error": "Invalid credentials"}), 401
