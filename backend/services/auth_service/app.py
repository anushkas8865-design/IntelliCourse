import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from shared.database.database import SessionLocal
from shared.models.user import User


load_dotenv()


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

jwt = JWTManager(app)


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required."
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email, and password are required."
        }), 400

    db = SessionLocal()

    try:
        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            return jsonify({
                "error": "Email already registered."
            }), 409

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return jsonify({
            "message": "User registered successfully.",
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
            }
        }), 201

    except Exception:
        db.rollback()

        return jsonify({
            "error": "Registration failed."
        }), 500

    finally:
        db.close()


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:
            return jsonify({
                "error": "Invalid email or password."
            }), 401

        if not check_password_hash(user.password, password):
            return jsonify({
                "error": "Invalid email or password."
            }), 401

        access_token = create_access_token(
            identity=user.user_id
        )

        return jsonify({
            "message": "Login successful.",
            "access_token": access_token,
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
            }
        }), 200

    except Exception:
        db.rollback()

        return jsonify({
            "error": "Login failed."
        }), 500

    finally:
        db.close()


@app.route("/api/auth/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            return jsonify({
                "error": "User not found."
            }), 404

        return jsonify({
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
            }
        }), 200

    except Exception:
        return jsonify({
            "error": "Failed to retrieve profile."
        }), 500

    finally:
        db.close()


@app.route("/api/auth/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required."
        }), 400

    name = data.get("name")
    email = data.get("email")

    if not name and not email:
        return jsonify({
            "error": "At least one field is required."
        }), 400

    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            return jsonify({
                "error": "User not found."
            }), 404

        if email and email != user.email:
            existing_user = db.query(User).filter(
                User.email == email,
                User.user_id != user_id
            ).first()

            if existing_user:
                return jsonify({
                    "error": "Email already registered."
                }), 409

        if name:
            user.name = name

        if email:
            user.email = email

        db.commit()
        db.refresh(user)

        return jsonify({
            "message": "Profile updated successfully.",
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
            }
        }), 200

    except Exception:
        db.rollback()

        return jsonify({
            "error": "Profile update failed."
        }), 500

    finally:
        db.close()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True,
    )