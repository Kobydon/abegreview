from flask import Blueprint, jsonify, request
from flask.helpers import make_response
from application.extensions.extensions import *
from application.settings.setup import app
from application.settings.settings import *
from application.database.user.user_db import db
from datetime import datetime
import flask_praetorian
from application.database.user.user_db import User,Subscription
from flask_marshmallow import Marshmallow
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
import secrets
from sqlalchemy.exc import IntegrityError

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

user = Blueprint("user", __name__)
facebook_bp = make_facebook_blueprint(
    client_id="733317272754649",
    client_secret="0c7ef47906a322ebaad97e1a99fa4e3b",
    redirect_to="user.facebook_login"
)
app.register_blueprint(facebook_bp, url_prefix="/facebook_login")
guard.init_app(app, User)
ma = Marshmallow(app)

class User_schema(ma.Schema):
    class Meta:
        fields=("id","username","email","phone","id","role","is_active",
                "premium_listing","normal_listing","sponsored_ads","premium_analytics","feedbacks","review_contest"
                )
        
        

user_schema = User_schema(many=True)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Basic validation
    required_fields = ["username", "email", "password"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    username = data["username"]
    email = data["email"]
    password = data["password"]
    phone = data.get("phone")
    role = data.get("role", "user")

    # Check if email or username already exists
    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({"error": "User with that email or username already exists"}), 409

    try:
        hashed_password = guard.hash_password(password)

        new_user = User(
            username=username,
            email=email,
            phone=phone,
            role=role,
            password=hashed_password,
            # access="normal",
            is_active=True
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed: " + str(e)}), 500

@user.route("/login", methods=["POST"])
def login():
    try:
        username = request.json.get("username")
        password = request.json.get("password")

        user = guard.authenticate(username, password)
        user.last_login = datetime.utcnow()
        db.session.commit()
        token = guard.encode_jwt_token(user)
        return jsonify({"id_token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    


@user.route("/update_logout", methods=['PUT'])
@flask_praetorian.auth_required
def update_logout():
    user = flask_praetorian.current_user()
    
    # Update the last logout time
    user.last_logout = datetime.utcnow()  # Use UTC for consistency
    
    # Commit the changes
    db.session.commit()
    
    # Optional: no need to call db.session.close manually here
    return jsonify({"message": "Logout time updated successfully"}), 200




@user.route("/facebook-login", methods=["POST"])
def facebook_login():
    data = request.get_json()

    facebook_id = data.get("facebook_id")
    email = data.get("email")
    name = data.get("name")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Check if user exists
    user = User.query.filter_by(email=email).first()

    if not user:
        # Create new user with a dummy password (won't be used for login)
        dummy_password = guard.hash_password(facebook_id)
        user = User(username=name, email=email, password=dummy_password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Email already exists."}), 400

    if not user.is_active:
        return jsonify({"error": "User account is inactive."}), 403

    # Generate JWT token
    token = guard.encode_jwt_token(user)
    return jsonify({
        "id_token": token
    }), 200

@user.route("/get_info", methods=["GET"])
@flask_praetorian.auth_required
def get_info():
    try:
        current_user = flask_praetorian.current_user()

        return jsonify({
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "phone": current_user.phone,
            "role": current_user.role,
            "premium_listing" : current_user.premium_listing,
            "normal_listing" :current_user.normal_listing,
            "sponsored_ads" :current_user.sponsored_ads,
            "premium_analytics" :current_user.premium_analytics,
            "review_contest" :current_user.review_contest
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route("/get_users", methods=["GET"])
@flask_praetorian.auth_required
def get_users():
    try:
        users = User.query.all()
        results = user_schema.dump(users)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route("/get_user/<int:id>", methods=["GET"])
@flask_praetorian.auth_required
def get_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route("/delete_user/<int:id>", methods=["DELETE"])
@flask_praetorian.auth_required
def delete_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user.route("/update_user", methods=["PUT"])
@flask_praetorian.auth_required
def update_user():
    try:
        id = request.json.get("id")
        user = User.query.get(id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.username = request.json.get("username", user.username)
        user.email = request.json.get("email", user.email)
        user.phone = request.json.get("phone", user.phone)
        user.role = request.json.get("role", user.role)

        if "password" in request.json:
            user.password = guard.hash_password(request.json["password"])

        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@user.route("/add_subscription", methods=["PUT"])
@flask_praetorian.auth_required
def add_subscription():
    try:
        subscription_id = request.json.get("id")

        # Get current authenticated user
        user = User.query.get(flask_praetorian.current_user().id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the selected subscription
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return jsonify({"error": "Subscription not found"}), 404

        # Dynamically assign "yes" based on the subscription name
        valid_fields = ["premium_listing", "normal_listing", "sponsored_ads", "premium_analytics", "review_contest"]

        field_to_update = subscription.name.strip().lower().replace(" ", "_")  # Normalize name to match field

        if field_to_update in valid_fields:
            setattr(user, field_to_update, "pending")  # Set user.premium_listing = "yes", etc.
        else:
            return jsonify({"error": f"Invalid subscription name '{subscription.name}'"}), 400

        db.session.commit()
        return jsonify({"message": f"{subscription.name} subscription added successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


@user.route("/google-login", methods=["POST"])
def google_login():
    try:
        token = request.json.get("token")
        if not token:
            return jsonify({"error": "Missing token"}), 400

        # Verify Google ID token
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            "351595459993-vbnlaj5c8jbp21tgnjtlb09gl5igmlf2.apps.googleusercontent.com"
        )

        email = idinfo['email']
        name = idinfo.get('name', email)

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if not user:
            # Create new user with default role 'user'
            user = User(username=name, email=email, password='google_oauth', role='user')
            db.session.add(user)
            db.session.commit()

        # Create JWT token
        jwt_token = guard.encode_jwt_token(user)

        return jsonify({
            "id_token": jwt_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid token"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500
