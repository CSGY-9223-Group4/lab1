from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from werkzeug.exceptions import UnsupportedMediaType
import os

from .exceptions.auth_exception import AuthException
from .exceptions.user_exists_exception import UserAlreadyExistsException

from .api import pastebin


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = open(os.environ["JWT_SECRET_FILE"], "r").read().strip()
jwt = JWTManager(app)

INTERNAL_SERVER_ERROR = "Internal Server Error"


@app.route("/v1/register_user", methods=["POST"])
def register_user():
    try:
        # TODO: apply realistic validation for username/password
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        access_token = pastebin.register_user(username, password)
        return jsonify(message="User registered", access_token=access_token), 200
    except UnsupportedMediaType as e:
        return jsonify({"error": "Unsupported media type: " + e.get_description()}), 415
    except UserAlreadyExistsException:
        return jsonify({"error": "User already exists"}), 409
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/login", methods=["POST"])
def login():
    try:
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        access_token = pastebin.login(username, password)
        return jsonify(access_token=access_token), 200
    except UnsupportedMediaType as e:
        return jsonify({"error": "Unsupported media type: " + e.get_description()}), 415
    except AuthException:
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/protected", methods=["GET"])
@jwt_required()
def protected():
    try:
        return jsonify(logged_in_as=get_jwt_identity()), 200
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500
