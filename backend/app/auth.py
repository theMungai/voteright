from flask import Blueprint, request, jsonify
from app import db, bcrypt, jwt

from app.models import User
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, password_hash=pw_hash)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User registered"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "Username already exists"}), 400

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token, username=user.username, role=user.role)
    return jsonify({"msg": "Bad username or password"}), 401
